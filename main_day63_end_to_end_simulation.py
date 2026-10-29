"""Run the synthetic Day 63 end-to-end hiring-pipeline demonstration."""

from __future__ import annotations

import json
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path

from compliance.audit_logger import AuditLogger
from compliance.consent_manager import ConsentManager
from compliance.models import ConsentType
from interview_ai.hr.day45_demo import calculate_answer_relevance
from interview_ai.hr.hr_interview_engine import HRInterviewEngine
from interview_ai.machine_test.machine_test_evaluator import MachineTestEvaluator
from interview_ai.machine_test.machine_test_framework import MachineTestFramework
from interview_ai.technical.technical_engine import TechnicalInterviewEngine
from interview_ai.technical.technical_scoring_engine import TechnicalScoringEngine
from main_candidate_ranking import require_resume_screening_consent
from screening_ai.conversation_flow import ConversationFlowEngine
from scoring.candidate_matching_service import CandidateMatchingService
from scoring.eligibility_decision_engine import EligibilityDecisionEngine
from scoring.final_recommendation_generator import FinalRecommendationGenerator
from scoring.screening_scoring_engine import ScreeningScoringEngine
from scoring.unified_candidate_score_generator import UnifiedCandidateScoreGenerator


BASE_DIR = Path(__file__).resolve().parent
DATASET_PATH = BASE_DIR / "data" / "day63_demo" / "dataset_manifest.json"
DEFAULT_OUTPUT_PATH = BASE_DIR / "reports" / "day63_end_to_end_simulation.json"
CONSENT_TYPES = (
    ConsentType.RESUME_PROCESSING,
    ConsentType.AI_SCREENING,
    ConsentType.TRANSCRIPT_PROCESSING,
    ConsentType.AI_EVALUATION,
)


def _load_dataset(path: Path) -> dict:
    manifest_path = Path(path).resolve()
    with manifest_path.open("r", encoding="utf-8") as file:
        manifest = json.load(file)

    if not manifest.get("synthetic_only"):
        raise ValueError("The Day 63 demo runner only accepts synthetic data.")

    dataset_root = manifest_path.parent.resolve()

    def load_asset(relative_path: str) -> dict:
        if not isinstance(relative_path, str) or not relative_path.strip():
            raise ValueError("Manifest asset paths must be non-empty strings.")
        asset_path = (dataset_root / relative_path).resolve()
        if asset_path != dataset_root and dataset_root not in asset_path.parents:
            raise ValueError(f"Dataset asset escapes its root: {relative_path}")
        with asset_path.open("r", encoding="utf-8") as asset_file:
            return json.load(asset_file)

    job_descriptions = []
    for record in manifest.get("job_descriptions", []):
        job_description = load_asset(record.get("file"))
        if job_description.get("job_description_id") != record.get("job_description_id"):
            raise ValueError(f"Job description ID does not match manifest entry: {record}")
        job_descriptions.append(job_description)

    candidates = []
    for record in manifest.get("candidate_profiles", []):
        candidate = load_asset(record.get("file"))
        if candidate.get("candidate_id") != record.get("candidate_id"):
            raise ValueError(f"Candidate ID does not match manifest entry: {record}")
        candidates.append(candidate)

    if not job_descriptions:
        raise ValueError("The demo manifest must reference job descriptions.")
    if not candidates:
        raise ValueError("The demo manifest must reference candidate profiles.")

    return {
        "dataset_id": manifest.get("dataset_id"),
        "version": manifest.get("version"),
        "synthetic_only": manifest.get("synthetic_only"),
        "description": manifest.get("description"),
        "job_descriptions": job_descriptions,
        "candidates": candidates,
        "machine_test_task": load_asset(manifest.get("machine_test_task_file")),
    }


def _grant_demo_consents(consent_manager: ConsentManager, candidate_id: str) -> None:
    for consent_type in CONSENT_TYPES:
        consent_manager.grant_consent(
            candidate_id,
            consent_type,
            source="synthetic_day63_demo_fixture",
        )

    require_resume_screening_consent(consent_manager, candidate_id)
    consent_manager.require_consent(
        candidate_id,
        ConsentType.TRANSCRIPT_PROCESSING,
    )
    consent_manager.require_consent(
        candidate_id,
        ConsentType.AI_EVALUATION,
    )


def _run_screening(candidate_id: str, screening_inputs: list[dict]) -> dict:
    questions = [
        {
            "category": item["category"],
            "question": item["question"],
            "fallback_question": "Please clarify your answer briefly.",
        }
        for item in screening_inputs
    ]
    flow = ConversationFlowEngine(
        rules_path=str(BASE_DIR / "config" / "conversation_flow_rules.json")
    )
    context = flow.start(
        session_id=f"DAY63-{candidate_id}-SCREENING",
        candidate_id=candidate_id,
        questions=questions,
    )
    scoring = ScreeningScoringEngine(
        rules_path=str(BASE_DIR / "config" / "screening_scoring_rules.json")
    )

    question_scores = []
    answers = []
    actions = []
    for item in screening_inputs:
        flow_result = flow.receive_response(context, item["answer"])
        actions.append(flow_result["action"])
        if len(context.answers) != len(answers) + 1:
            raise RuntimeError(
                f"Screening did not store the supplied answer for {candidate_id}: "
                f"{flow_result['action']}"
            )

        previous_answers = [answer["answer"] for answer in context.answers[:-1]]
        score = scoring.score_question(
            question=item["question"],
            answer=item["answer"],
            category=item["category"],
            expected_keywords=item.get("expected_keywords", []),
            previous_answers=previous_answers,
        )
        question_scores.append(score)
        answers.append(
            {
                "question": item["question"],
                "category": item["category"],
                "answer": item["answer"],
                "normalized_scores": score["normalized_scores"],
                "explanations": score["explanations"],
            }
        )

    if not context.completed:
        raise RuntimeError(
            f"Screening flow did not complete for {candidate_id}: "
            f"state={context.state}, answers={len(context.answers)}"
        )

    aggregate = scoring.aggregate_scores(question_scores)
    return {
        "score_0_100": aggregate["total_screening_score"],
        "questions_evaluated": aggregate["questions_evaluated"],
        "answers_accepted": len(context.answers),
        "conversation_completed": context.completed,
        "parameter_scores": aggregate.get("parameter_scores", {}),
        "answer_actions": actions,
        "answers": answers,
        "scoring_note": (
            "Uses the screening conversation state machine and configured rubric. "
            "This fixture harness supplies pre-curated non-empty responses and does "
            "not invoke the semantic answer-intent adapter."
        ),
    }


def _run_hr_interview(candidate: dict, role: str) -> dict:
    candidate_id = candidate["candidate_id"]
    engine = HRInterviewEngine(
        session_id=f"DAY63-{candidate_id}-HR",
        candidate_id=candidate_id,
        role=role,
        candidate_type=("experienced" if candidate["experience_years"] >= 2 else "fresher"),
        role_type="technical",
    )
    responses_by_category = candidate["hr_responses"]
    question = engine.start()
    interview_answers = []

    while question is not None and len(interview_answers) < 40:
        category = engine.current_category or "fallback"
        response = responses_by_category.get(
            category,
            responses_by_category["fallback"],
        )
        interview_answers.append(
            {
                "category": category,
                "question": question,
                "response": response,
            }
        )
        result = engine.submit_response(response)
        question = result.get("question")

    state = engine.get_state()
    if not state.get("interview_completed"):
        raise RuntimeError(
            f"HR interview did not complete for {candidate_id} after "
            f"{state.get('questions_answered', 0)} responses."
        )

    response_history = state.get("response_history", [])
    communication_history = engine.get_communication_history()
    resume_skills = candidate["resume"].get("Skills", {}).get("technical", [])
    behavioral_previous_data = {
        "experience_years": candidate["experience_years"],
        "skills": resume_skills,
    }
    question_scores = []

    for index, item in enumerate(response_history):
        response = item.get("response", "")
        communication_score = 0.0
        if index < len(communication_history):
            communication_score = communication_history[index].get(
                "normalized_score", 0.0
            )

        behavioral = engine.analyze_behavioral_signals(
            response=response,
            previous_data=behavioral_previous_data,
        )
        confidence = behavioral.get("behavioral_confidence", {}).get(
            "behavioral_confidence_score", communication_score
        )
        try:
            confidence = max(0.0, min(100.0, float(confidence)))
        except (TypeError, ValueError):
            confidence = communication_score

        contradictions = behavioral.get("contradiction", {}).get("count", 0)
        question_scores.append(
            {
                "answer_relevance": calculate_answer_relevance(
                    item.get("question", ""),
                    response,
                ),
                "communication": communication_score,
                "confidence": confidence,
                "consistency": max(0.0, 100.0 - contradictions * 10.0),
            }
        )

    score = engine.calculate_hr_interview_score(question_scores)
    return {
        "score_0_100": score["final_score"],
        "questions_answered": state.get("questions_answered", len(response_history)),
        "completed": state.get("interview_completed", False),
        "completion_ratio": score.get("completion_ratio"),
        "normalized_scores": score.get("normalized_scores", {}),
        "responses": interview_answers,
        "scoring_note": (
            "Uses the current deterministic HR demonstration heuristics. "
            "Responses are fictional fixture inputs and require human interpretation."
        ),
    }


def _run_technical_interview(candidate: dict, role: str) -> dict:
    candidate_id = candidate["candidate_id"]
    engine = TechnicalInterviewEngine(
        candidate_id=candidate_id,
        role=role,
        experience_years=candidate["experience_years"],
    )
    if not engine.skill_domain:
        raise ValueError("The demo role is not supported by technical interview mapping.")

    answers = candidate["technical_answers"]
    answer_quality = candidate.get("technical_answer_quality", "acceptable")
    question_answers = []
    question = engine.get_next_question()

    while question is not None:
        question_data = {
            "stage": engine.state.current_stage,
            "difficulty": engine.state.current_difficulty,
            "question": question,
            "answer": answers[len(question_answers) % len(answers)],
        }
        question_answers.append(question_data)
        question = engine.submit_answer(answer_quality=answer_quality)

    rubric_input = candidate["technical_rubric_input"]
    score = TechnicalScoringEngine.score_answer(
        accuracy=rubric_input["accuracy"],
        depth=rubric_input["depth"],
        logical_reasoning=rubric_input["logical_reasoning"],
        real_world_applicability=rubric_input["real_world_applicability"],
    )
    progress = engine.get_progress()
    return {
        "score_0_100": score["final_score"],
        "score_breakdown": score["breakdown"],
        "questions_answered": progress["questions_answered"],
        "completed": progress["interview_completed"],
        "skill_domain": engine.skill_domain,
        "question_answers": question_answers,
        "score_source": rubric_input.get("note", "Illustrative rubric fixture."),
    }


def _run_machine_test(candidate_id: str, task: dict, test_input: dict) -> dict:
    framework = MachineTestFramework()
    validated_task = framework.create_task(**task)
    result = MachineTestEvaluator().evaluate_submission(
        task=validated_task,
        candidate_id=candidate_id,
        code=test_input["code"],
        execution_result=test_input["execution_result"],
        correctness=test_input["correctness"],
        efficiency=test_input["efficiency"],
        code_quality=test_input["code_quality"],
        problem_solving=test_input["problem_solving"],
        time_taken_minutes=test_input["time_taken_minutes"],
    )
    result["scoring_note"] = (
        "The evaluator scores fixture-supplied rubric values and captures the code. "
        "The current framework does not execute candidate code; execution summaries "
        "are synthetic inputs and must not be treated as verified test results."
    )
    return result


def _candidate_skills(candidate: dict) -> list[str]:
    skills = candidate["resume"].get("Skills", {})
    found = []
    if isinstance(skills, dict):
        for category in ("technical", "business", "creative"):
            values = skills.get(category, [])
            if isinstance(values, list):
                found.extend(
                    str(value.get("skill", "")) if isinstance(value, dict) else str(value)
                    for value in values
                )
    return [skill for skill in found if skill.strip()]


def _run_candidate(candidate: dict, dataset: dict, job_description: dict,
                   matching_service: CandidateMatchingService,
                   consent_manager: ConsentManager, audit_logger: AuditLogger,
                   temp_root: Path) -> dict:
    candidate_id = candidate["candidate_id"]
    durations = {}

    started = time.perf_counter()
    _grant_demo_consents(consent_manager, candidate_id)
    durations["resume_intake_and_consent"] = time.perf_counter() - started

    started = time.perf_counter()
    ats_result = matching_service.generate_score(
        candidate["resume"],
        job_description,
    )
    durations["ats_scoring"] = time.perf_counter() - started

    started = time.perf_counter()
    screening_result = _run_screening(candidate_id, candidate["screening"])
    durations["screening"] = time.perf_counter() - started

    started = time.perf_counter()
    hr_result = _run_hr_interview(candidate, job_description["role"])
    durations["hr_interview"] = time.perf_counter() - started

    started = time.perf_counter()
    technical_result = _run_technical_interview(candidate, job_description["role"])
    durations["technical_interview"] = time.perf_counter() - started

    started = time.perf_counter()
    machine_result = _run_machine_test(
        candidate_id,
        dataset["machine_test_task"],
        candidate["machine_test"],
    )
    durations["machine_test"] = time.perf_counter() - started

    started = time.perf_counter()
    unified = UnifiedCandidateScoreGenerator(
        output_path=temp_root / f"{candidate_id}_unified_score.json",
        audit_logger=audit_logger,
    ).generate(
        candidate_id=candidate_id,
        candidate_name=candidate["candidate_name"],
        role=job_description["role"],
        ats_score=ats_result["percentage"],
        screening_score=screening_result["score_0_100"],
        hr_interview_score=hr_result["score_0_100"],
        technical_interview_score=technical_result["score_0_100"],
        machine_test_score=machine_result["final_score"],
    )
    durations["unified_scoring"] = time.perf_counter() - started

    started = time.perf_counter()
    eligibility = EligibilityDecisionEngine().evaluate(
        candidate={
            "ats_score": ats_result["percentage"],
            "skills": _candidate_skills(candidate),
            "experience": candidate["experience_years"],
            "location": candidate.get("location"),
            "availability": candidate.get("availability"),
        },
        rules=job_description["eligibility_rules"],
    )
    recommendation = FinalRecommendationGenerator(
        output_path=temp_root / f"{candidate_id}_recommendation.json",
        audit_logger=audit_logger,
    ).generate(
        candidate_id=candidate_id,
        candidate_name=candidate["candidate_name"],
        role=job_description["role"],
        unified_score=unified["unified_score"],
        eligibility_result=eligibility,
    )
    durations["eligibility_and_final_decision"] = time.perf_counter() - started

    return {
        "candidate": {
            "candidate_id": candidate_id,
            "candidate_name": candidate["candidate_name"],
            "job_description_id": job_description["job_description_id"],
            "job_title": job_description["title"],
            "scenario": candidate["scenario"],
            "resume_quality": candidate["resume_quality"],
            "experience_years": candidate["experience_years"],
            "synthetic": True,
        },
        "stages": {
            "resume_intake": {
                "source": "structured synthetic resume fixture",
                "profile_quality_scenario": candidate["resume_quality"],
                "parser_or_upload_endpoint_exercised": False,
            },
            "ats": {
                "score_0_100": ats_result["percentage"],
                "components": ats_result["components"],
                "weights": ats_result["weights"],
                "explanations": ats_result["explanations"],
            },
            "screening": screening_result,
            "hr_interview": hr_result,
            "technical_interview": technical_result,
            "machine_test": machine_result,
            "unified_score": {
                "score_0_100": unified["unified_score"],
                "round_scores": unified["round_scores"],
                "normalized_scores": unified["normalized_scores"],
                "weights": unified["weights"],
                "weighted_scores": unified["weighted_scores"],
            },
            "eligibility": eligibility,
            "final_recommendation": recommendation,
        },
        "performance": {
            "stage_seconds": {name: round(value, 4) for name, value in durations.items()},
            "total_seconds": round(sum(durations.values()), 4),
        },
    }


def _summarize_observations(candidates: list[dict]) -> list[dict]:
    observations = []

    hr_scores = [
        candidate["stages"]["hr_interview"]["score_0_100"]
        for candidate in candidates
    ]
    if hr_scores and max(hr_scores) - min(hr_scores) < 10:
        observations.append(
            {
                "finding": "HR interview scores are tightly clustered across varied profiles.",
                "evidence": {
                    "minimum_score": min(hr_scores),
                    "maximum_score": max(hr_scores),
                    "score_spread": round(max(hr_scores) - min(hr_scores), 2),
                },
                "interpretation": (
                    "The deterministic HR heuristics produce similar outputs even "
                    "when resume and technical evidence differ. Treat this stage "
                    "as a conversation aid, not a reliable ranking signal."
                ),
            }
        )

    limited_profiles = [
        candidate
        for candidate in candidates
        if candidate["candidate"]["resume_quality"] == "limited"
        and candidate["stages"]["screening"]["score_0_100"] >= 75
    ]
    if limited_profiles:
        observations.append(
            {
                "finding": "A limited-evidence profile receives a relatively high screening score.",
                "evidence": [
                    {
                        "candidate_id": candidate["candidate"]["candidate_id"],
                        "screening_score": candidate["stages"]["screening"]["score_0_100"],
                    }
                    for candidate in limited_profiles
                ],
                "interpretation": (
                    "The configured screening rubric also rewards clarity and "
                    "consistency, so its aggregate score can remain high when "
                    "job-skill evidence is limited. Compare it with ATS, interview, "
                    "and human-reviewed evidence."
                ),
            }
        )

    return observations


def run_simulation(dataset_path: Path = DATASET_PATH,
                   output_path: Path = DEFAULT_OUTPUT_PATH) -> dict:
    dataset = _load_dataset(Path(dataset_path))
    job_descriptions = {
        item["job_description_id"]: item
        for item in dataset.get("job_descriptions", [])
    }
    if not job_descriptions:
        raise ValueError("The demo dataset must include job descriptions.")
    unknown_job_ids = sorted(
        {
            candidate.get("job_description_id")
            for candidate in dataset["candidates"]
            if candidate.get("job_description_id") not in job_descriptions
        }
    )
    if unknown_job_ids:
        raise ValueError(f"Candidates reference unknown job descriptions: {unknown_job_ids}")

    matching_service = CandidateMatchingService()
    consent_manager = ConsentManager(policy_version="day63-synthetic-demo")
    run_started = time.perf_counter()

    temp_parent = BASE_DIR / "reports"
    temp_parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(
        prefix="day63-demo-",
        dir=temp_parent,
    ) as temp_dir:
        temp_root = Path(temp_dir)
        audit_logger = AuditLogger(temp_root / "audit")
        candidates = [
            _run_candidate(
                candidate,
                dataset,
                job_descriptions[candidate["job_description_id"]],
                matching_service,
                consent_manager,
                audit_logger,
                temp_root,
            )
            for candidate in dataset["candidates"]
        ]

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    report = {
        "report_title": "Day 63 Synthetic End-to-End Hiring Pipeline Simulation",
        "dataset_id": dataset["dataset_id"],
        "dataset_version": dataset["version"],
        "dataset_storage": {
            "manifest": "data/day63_demo/dataset_manifest.json",
            "job_descriptions": "data/day63_demo/job_descriptions/",
            "candidate_profiles": "data/day63_demo/candidates/",
            "shared_assessment": "data/day63_demo/assessments/python_unique_sorted_task.json",
        },
        "run_at_utc": datetime.now(timezone.utc).isoformat(),
        "synthetic_only": True,
        "job_descriptions": dataset["job_descriptions"],
        "candidate_count": len(candidates),
        "candidates": candidates,
        "pipeline_observations": _summarize_observations(candidates),
        "pipeline_stages": [
            "synthetic resume intake",
            "ATS scoring",
            "screening",
            "HR interview",
            "technical interview",
            "machine test evaluation",
            "unified scoring",
            "eligibility and final recommendation",
        ],
        "performance": {
            "total_seconds": round(time.perf_counter() - run_started, 4),
            "measurement_note": (
                "One local synthetic run. Model initialization and any first-use "
                "download affect timings; this is not a production benchmark."
            ),
        },
        "limitations": [
            "Resume upload and parser integration are represented by pre-structured synthetic JSON; this runner does not exercise a production upload endpoint.",
            "The screening state machine and configured answer rubric are used, but the semantic answer-intent adapter is not invoked by this fixture harness.",
            "HR scoring uses the repository's deterministic demonstration heuristics and synthetic responses.",
            "Technical interview and machine-test scores use explicitly labeled rubric fixtures; candidate free text and code are not automatically evaluated by those components.",
            "Machine-test execution summaries are simulated fixture data; no submitted code is executed or sandboxed.",
            "The final recommendations are demonstration outputs only. Human review is required before any real hiring decision.",
        ],
    }
    output_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report


def main() -> None:
    report = run_simulation()
    print("ZECPATH AI — DAY 63 END-TO-END DEMO")
    print(f"Synthetic profiles: {report['candidate_count']}")
    for candidate in report["candidates"]:
        stages = candidate["stages"]
        print(
            f"{candidate['candidate']['candidate_id']}: "
            f"ATS {stages['ats']['score_0_100']:.2f} | "
            f"Screening {stages['screening']['score_0_100']:.2f} | "
            f"HR {stages['hr_interview']['score_0_100']:.2f} | "
            f"Technical {stages['technical_interview']['score_0_100']:.2f} | "
            f"Machine {stages['machine_test']['final_score']:.2f} | "
            f"Unified {stages['unified_score']['score_0_100']:.2f} | "
            f"Recommendation: {stages['final_recommendation']['decision']}"
        )
    print(f"\nReport written to: {DEFAULT_OUTPUT_PATH}")
    print("All profiles and responses in this run are fictional demo data.")


if __name__ == "__main__":
    main()
