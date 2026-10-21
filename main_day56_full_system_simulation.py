"""Run a reproducible, synthetic Day 56 hiring-pipeline simulation."""

import json
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path

from compliance.audit_logger import AuditLogger
from compliance.consent_manager import ConsentManager
from compliance.models import ConsentType
from interview_ai.hr.day45_demo import (
    DEMO_RESPONSES,
    calculate_answer_relevance,
)
from interview_ai.hr.hr_interview_engine import HRInterviewEngine
from interview_ai.technical.technical_engine import TechnicalInterviewEngine
from interview_ai.technical.technical_scoring_engine import TechnicalScoringEngine
from main_candidate_ranking import require_resume_screening_consent
from screening_ai.conversation_flow import ConversationFlowEngine
from screening_ai.day29_answer_adapter import Day29AnswerAdapter
from screening_ai.intent_classifier import IntentClassifier
from scoring.candidate_matching_service import CandidateMatchingService
from scoring.final_recommendation_generator import FinalRecommendationGenerator
from scoring.screening_scoring_engine import ScreeningScoringEngine
from scoring.unified_candidate_score_generator import UnifiedCandidateScoreGenerator


BASE_DIR = Path(__file__).resolve().parent
INPUT_PATH = BASE_DIR / "data" / "day56_simulation_input.json"
HUMAN_CASES_PATH = BASE_DIR / "data" / "day30_test_cases.json"
DEFAULT_OUTPUT_PATH = BASE_DIR / "reports" / "day56_e2e_run.json"


def _load_json(path):
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def _run_screening(candidate_id, screening_inputs):
    answer_adapter = Day29AnswerAdapter()
    questions = [
        {
            "category": item["category"],
            "question": item["question"],
            "fallback_question": "Please clarify your answer briefly.",
        }
        for item in screening_inputs
    ]
    flow = ConversationFlowEngine(
        rules_path=str(BASE_DIR / "config" / "conversation_flow_rules.json"),
        answer_analyzer=answer_adapter.analyze,
    )
    context = flow.start(
        session_id="DAY56-SYNTH-SESSION",
        candidate_id=candidate_id,
        questions=questions,
    )
    scoring = ScreeningScoringEngine(
        rules_path=str(BASE_DIR / "config" / "screening_scoring_rules.json")
    )
    question_scores = []
    answer_results = []

    for item in screening_inputs:
        result = flow.receive_response(context, item["answer"])
        answer_results.append(result)
        question_scores.append(
            scoring.score_question(
                question=item["question"],
                answer=item["answer"],
                category=item["category"],
                expected_keywords=item["expected_keywords"],
                previous_answers=[entry["answer"] for entry in context.answers[:-1]],
            )
        )

    aggregate = scoring.aggregate_scores(question_scores)
    if not context.completed:
        raise RuntimeError(
            "Screening flow did not complete: "
            f"state={context.state}, answers={len(context.answers)}"
        )

    return {
        "score_0_100": aggregate["total_screening_score"],
        "questions_evaluated": aggregate["questions_evaluated"],
        "answers_accepted": len(context.answers),
        "conversation_completed": context.completed,
        "parameter_scores": aggregate.get("parameter_scores", {}),
        "answer_actions": [item.get("action") for item in answer_results],
    }


def _run_hr_interview(candidate_id, role):
    engine = HRInterviewEngine(
        session_id="DAY56-SYNTH-HR",
        candidate_id=candidate_id,
        role=role,
        candidate_type="experienced",
        role_type="technical",
    )
    question = engine.start()
    response_index = 0

    while question is not None and response_index < len(DEMO_RESPONSES):
        result = engine.submit_response(DEMO_RESPONSES[response_index])
        response_index += 1
        question = result.get("question")

    state = engine.get_state()
    response_history = state.get("response_history", [])
    communication_history = engine.get_communication_history()
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
            previous_data={
                "experience_years": 2,
                "availability_days": 30,
                "skills": ["python", "django", "sql"],
            },
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
                    item.get("question", ""), response
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
        "scoring_note": (
            "Uses the current Day 45 deterministic demonstration heuristics; "
            "the interview responses are synthetic."
        ),
    }


def _run_technical_interview(candidate_id, role, years, rubric_input):
    engine = TechnicalInterviewEngine(
        candidate_id=candidate_id,
        role=role,
        experience_years=years,
    )
    if not engine.skill_domain:
        raise ValueError(f"Technical interview does not support role: {role}")

    question = engine.get_next_question()
    while question is not None:
        question = engine.submit_answer(answer_quality="acceptable")

    score = TechnicalScoringEngine.score_answer(
        accuracy=rubric_input["accuracy"],
        depth=rubric_input["depth"],
        logical_reasoning=rubric_input["logical_reasoning"],
        real_world_applicability=rubric_input["real_world_applicability"],
    )
    progress = engine.get_progress()
    return {
        "score_0_100": score["final_score"],
        "questions_answered": progress["questions_answered"],
        "completed": progress["interview_completed"],
        "skill_domain": engine.skill_domain,
        "score_source": "illustrative rubric inputs from the simulation fixture",
    }


def _compare_screening_human_cases():
    dataset = _load_json(HUMAN_CASES_PATH)
    classifier = IntentClassifier()
    action_map = {
        "on_topic": "accept",
        "vague": "clarify",
        "missing": "clarify",
        "off_topic": "fallback",
    }
    evaluations = []

    for case in dataset["cases"]:
        ai_result = classifier.classify(
            case["candidate_answer"],
            case["category"],
        )
        ai_intent = ai_result["intent_label"]
        ai_action = action_map.get(ai_intent, "review")
        match = (
            ai_intent == case["human_expected_intent"]
            and ai_action == case["human_expected_action"]
        )
        evaluations.append(
            {
                "case_id": case["case_id"],
                "human_intent": case["human_expected_intent"],
                "ai_intent": ai_intent,
                "human_action": case["human_expected_action"],
                "ai_action": ai_action,
                "match": match,
            }
        )

    matches = sum(item["match"] for item in evaluations)
    return {
        "comparison_scope": "screening intent and action only",
        "cases": len(evaluations),
        "matches": matches,
        "mismatches": len(evaluations) - matches,
        "agreement_percent": round(matches * 100 / len(evaluations), 2)
        if evaluations
        else None,
        "evaluations": evaluations,
        "candidate_level_human_reference_available": False,
    }


def run_simulation(output_path=DEFAULT_OUTPUT_PATH):
    durations = {}
    run_start = time.perf_counter()

    start = time.perf_counter()
    scenario = _load_json(INPUT_PATH)
    candidate_id = scenario["candidate_id"]
    candidate_name = scenario["candidate_name"]
    role = scenario["role"]
    resume = scenario["resume"]
    job_description = scenario["job_description"]
    durations["resume_intake"] = time.perf_counter() - start

    consent_manager = ConsentManager(policy_version="day56-simulation")
    for consent_type in (
        ConsentType.RESUME_PROCESSING,
        ConsentType.AI_SCREENING,
        ConsentType.TRANSCRIPT_PROCESSING,
        ConsentType.AI_EVALUATION,
    ):
        consent_manager.grant_consent(
            candidate_id,
            consent_type,
            source="synthetic_day56_fixture",
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

    start = time.perf_counter()
    ats_result = CandidateMatchingService().generate_score(
        resume,
        job_description,
    )
    durations["ats_scoring"] = time.perf_counter() - start

    start = time.perf_counter()
    screening_result = _run_screening(
        candidate_id,
        scenario["screening"],
    )
    durations["screening"] = time.perf_counter() - start

    start = time.perf_counter()
    hr_result = _run_hr_interview(candidate_id, role)
    durations["hr_interview"] = time.perf_counter() - start

    start = time.perf_counter()
    technical_result = _run_technical_interview(
        candidate_id,
        role,
        scenario["experience_years"],
        scenario["technical_rubric_input"],
    )
    durations["technical_interview"] = time.perf_counter() - start

    with tempfile.TemporaryDirectory(prefix="day56-") as temp_dir:
        temp_root = Path(temp_dir)
        audit_logger = AuditLogger(temp_root / "audit")

        start = time.perf_counter()
        unified = UnifiedCandidateScoreGenerator(
            output_path=temp_root / "unified_score.json",
            audit_logger=audit_logger,
        ).generate(
            candidate_id=candidate_id,
            candidate_name=candidate_name,
            role=role,
            ats_score=ats_result["percentage"],
            # All pipeline stage scores use the same 0-100 scale.
            screening_score=screening_result["score_0_100"],
            hr_interview_score=hr_result["score_0_100"],
            technical_interview_score=technical_result["score_0_100"],
        )
        durations["unified_scoring"] = time.perf_counter() - start

        start = time.perf_counter()
        recommendation = FinalRecommendationGenerator(
            output_path=temp_root / "recommendation.json",
            audit_logger=audit_logger,
        ).generate(
            candidate_id=candidate_id,
            candidate_name=candidate_name,
            role=role,
            unified_score=unified["unified_score"],
            eligibility_result={
                "failed_rules": [],
                "review_rules": [
                    "Synthetic simulation requires human review before any real hiring action."
                ],
                "missing_mandatory_skills": [],
            },
        )
        durations["final_decision"] = time.perf_counter() - start

    start = time.perf_counter()
    human_comparison = _compare_screening_human_cases()
    durations["screening_human_comparison"] = time.perf_counter() - start
    durations["total_seconds"] = time.perf_counter() - run_start

    report = {
        "report_title": "Day 56 Full System Simulation",
        "run_at_utc": datetime.now(timezone.utc).isoformat(),
        "scenario": {
            "candidate_id": candidate_id,
            "candidate_name": candidate_name,
            "role": role,
            "synthetic": True,
            "resume_source": scenario["resume_filename"],
            "resume_intake_note": (
                "The upload step is represented by loading the synthetic JSON fixture. "
                "The repository has no upload endpoint, and its PDF/DOCX parser output "
                "is not directly connected to the ATS resume schema."
            ),
        },
        "stages": {
            "ats": {
                "score_0_100": ats_result["percentage"],
                "components": ats_result["components"],
            },
            "screening": screening_result,
            "hr_interview": hr_result,
            "technical_interview": technical_result,
            "unified_score": {
                "score_0_100": unified["unified_score"],
                "round_scores": unified["round_scores"],
                "weights": unified["weights"],
                "note": (
                "All stage scores use the shared 0-100 input scale."
                ),
            },
            "final_decision": recommendation,
        },
        "human_comparison": human_comparison,
        "performance": {
            "stage_seconds": {
                name: round(seconds, 4)
                for name, seconds in durations.items()
                if name != "total_seconds"
            },
            "total_seconds": round(durations["total_seconds"], 4),
            "measurement_note": (
                "One local synthetic run using a cached model; local model initialization "
                "is included but first-time model download is excluded. This is not a "
                "production load or throughput benchmark."
            ),
        },
        "limitations": [
            "The human benchmark covers 10 screening cases only; no human ratings were supplied for this candidate's ATS, HR, technical, or final decision.",
            "Technical question flow is exercised, but the current technical interview engine does not score free-text answers; illustrative rubric values are used.",
            "HR responses and candidate data are synthetic, and HR scoring uses deterministic demonstration heuristics.",
            "Resume intake loads a structured fixture rather than exercising a production file-upload endpoint or parser-to-ATS adapter.",
            "Single-candidate timings do not establish production performance or fairness across a representative population.",
        ],
    }

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(report, indent=2),
        encoding="utf-8",
    )
    return report


def main():
    report = run_simulation()
    print(json.dumps({
        "output": str(DEFAULT_OUTPUT_PATH),
        "candidate": report["scenario"]["candidate_id"],
        "ats_score": report["stages"]["ats"]["score_0_100"],
        "screening_score": report["stages"]["screening"]["score_0_100"],
        "hr_score": report["stages"]["hr_interview"]["score_0_100"],
        "technical_score": report["stages"]["technical_interview"]["score_0_100"],
        "unified_score": report["stages"]["unified_score"]["score_0_100"],
        "final_decision": report["stages"]["final_decision"]["decision"],
        "screening_human_agreement_percent": report["human_comparison"]["agreement_percent"],
        "total_seconds": report["performance"]["total_seconds"],
    }, indent=2))


if __name__ == "__main__":
    main()
