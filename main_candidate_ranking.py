import copy
import json
import os
import traceback

from scoring.candidate_matching_service import CandidateMatchingService
from scoring.ranking_engine import RankingEngine
from parsers.normalizer import Normalizer
from scoring.fairness_masker import FairnessMasker
from scoring.bias_evaluator import BiasEvaluator
from scoring.eligibility_decision_engine import EligibilityDecisionEngine


CV_FOLDER = "data/labeled_resumes"

JD_FOLDER = "data/parsed_jd"

ELIGIBILITY_RULES_PATH = (
    "config/eligibility_rules.json"
)


def load_json(path):

    with open(
        path,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


def normalize_resume(
    resume,
    normalizer
):

    normalized = copy.deepcopy(
        resume
    )

    text_fields = [
        "Summary",
        "Projects",
        "Others"
    ]

    for field in text_fields:

        value = normalized.get(
            field
        )

        if isinstance(
            value,
            list
        ):

            normalized[field] = [
                normalizer.normalize(
                    str(item)
                )
                for item in value
            ]

        elif isinstance(
            value,
            str
        ):

            normalized[field] = (
                normalizer.normalize(
                    value
                )
            )

    return normalized


def extract_candidate_skills(
    resume
):

    skills = resume.get(
        "Skills",
        {}
    )

    result = []

    for category in [
        "technical",
        "business",
        "creative"
    ]:

        category_skills = skills.get(
            category,
            []
        )

        for item in category_skills:

            if isinstance(
                item,
                dict
            ):

                skill = item.get(
                    "skill",
                    ""
                )

            else:

                skill = str(
                    item
                )

            if skill:

                result.append(
                    skill
                )

    return list(
        dict.fromkeys(
            result
        )
    )


def extract_candidate_experience(
    resume
):

    experience = resume.get(
        "Experience",
        {}
    )

    total_experience = (
        experience.get(
            "total_experience",
            {}
        )
    )

    candidate_years = (
        total_experience.get(
            "years"
        )
    )

    if candidate_years is not None:

        return candidate_years

    total_months = (
        total_experience.get(
            "total_months"
        )
    )

    if total_months is not None:

        return total_months / 12

    return None


def extract_candidate_location(
    resume
):

    location = resume.get(
        "Location"
    )

    if location:

        return location

    return None


def extract_candidate_availability(
    resume
):

    availability = resume.get(
        "Availability"
    )

    if availability:

        return availability

    return None


def main():

    # ---------------------------------
    # Find Job Description
    # ---------------------------------

    jd_files = [
        file_name
        for file_name in os.listdir(
            JD_FOLDER
        )
        if file_name.lower().endswith(
            ".json"
        )
    ]

    if not jd_files:

        raise FileNotFoundError(
            "No JD JSON file found in "
            "data/parsed_jd"
        )

    jd_files.sort()

    jd_path = os.path.join(
        JD_FOLDER,
        jd_files[0]
    )

    # ---------------------------------
    # Load JD and Eligibility Rules
    # ---------------------------------

    job_description = load_json(
        jd_path
    )

    eligibility_rules = load_json(
        ELIGIBILITY_RULES_PATH
    )

    # ---------------------------------
    # Initialize Services
    # ---------------------------------

    matching_service = (
        CandidateMatchingService()
    )

    ranking_engine = (
        RankingEngine()
    )

    normalizer = (
        Normalizer()
    )

    fairness_masker = (
        FairnessMasker()
    )

    bias_evaluator = (
        BiasEvaluator()
    )

    eligibility_engine = (
        EligibilityDecisionEngine()
    )

    candidates = []

    # ---------------------------------
    # Get JD Role
    # ---------------------------------

    job_role = job_description.get(
        "role",
        ""
    )

    rules = eligibility_rules.get(
        job_role,
        {}
    )

    if not rules:

        raise ValueError(
            f"No eligibility rules configured "
            f"for JD role: {job_role}"
        )

    # ---------------------------------
    # Process Candidate Resumes
    # ---------------------------------

    for file_name in os.listdir(
        CV_FOLDER
    ):

        if not file_name.lower().endswith(
            ".json"
        ):

            continue

        cv_path = os.path.join(
            CV_FOLDER,
            file_name
        )

        try:

            # ---------------------------------
            # Load Resume
            # ---------------------------------

            resume = load_json(
                cv_path
            )

            if not isinstance(resume, dict):
                print(
                    f"Skipping {file_name}: "
                    "expected a resume JSON object."
                )
                continue

            skills = resume.get("Skills", {})

            if not isinstance(skills, dict):
                print(
                    f"Skipping {file_name}: "
                    "unsupported Skills format."
                )
                continue

            # ---------------------------------
            # Normalize Resume
            # ---------------------------------

            normalized_resume = (
                normalize_resume(
                    resume,
                    normalizer
                )
            )

            # ---------------------------------
            # Preserve Candidate Identity
            # ---------------------------------

            others = normalized_resume.get(
                "Others",
                []
            )

            if others:

                candidate_name = (
                    str(
                        others[0]
                    ).strip()
                )

            else:

                candidate_name = "Unknown"

            # ---------------------------------
            # Create Scoring-Safe Copy
            # ---------------------------------

            scoring_resume = (
                fairness_masker.mask(
                    normalized_resume
                )
            )

            # ---------------------------------
            # Calculate ATS Score
            # ---------------------------------

            result = (
                matching_service.generate_score(
                    scoring_resume,
                    job_description
                )
            )

            ats_score = result.get(
                "percentage",
                0
            )

            # ---------------------------------
            # Extract Candidate Information
            # ---------------------------------

            candidate_skills = (
                extract_candidate_skills(
                    normalized_resume
                )
            )

            candidate_experience = (
                extract_candidate_experience(
                    normalized_resume
                )
            )

            candidate_location = (
                extract_candidate_location(
                    normalized_resume
                )
            )

            candidate_availability = (
                extract_candidate_availability(
                    normalized_resume
                )
            )

            # ---------------------------------
            # Build Eligibility Candidate
            # ---------------------------------

            eligibility_candidate = {

                "candidate": candidate_name,

                "ats_score": ats_score,

                "skills": candidate_skills,

                "experience": candidate_experience,

                "location": candidate_location,

                "availability": candidate_availability
            }

            # ---------------------------------
            # Day 21:
            # Connect ATS Output
            # with Eligibility Engine
            # ---------------------------------

            eligibility_result = (
                eligibility_engine.evaluate(
                    eligibility_candidate,
                    rules
                )
            )

            # ---------------------------------
            # Store Final Candidate Result
            # ---------------------------------

            candidates.append({

                "candidate": candidate_name,

                "score": ats_score,

                "status": (
                    eligibility_result[
                        "decision"
                    ]
                ),

                "failed_rules": (
                    eligibility_result[
                        "failed_rules"
                    ]
                ),

                "review_rules": (
                    eligibility_result[
                        "review_rules"
                    ]
                ),

                "missing_mandatory_skills": (
                    eligibility_result[
                        "missing_mandatory_skills"
                    ]
                ),

                "source_file": file_name
            })

            # ---------------------------------
            # Day 21 Rule Check
            # ---------------------------------

            print(
                "\n===== DAY 21 RULE CHECK ====="
            )

            print(
                "Candidate:",
                candidate_name
            )

            print(
                "JD Role:",
                job_role
            )

            print(
                "ATS Score:",
                f"{ats_score}%"
            )

            print(
                "Decision:",
                eligibility_result[
                    "decision"
                ]
            )

            print(
                "Failed Rules:",
                eligibility_result[
                    "failed_rules"
                ]
            )

            print(
                "Review Rules:",
                eligibility_result[
                    "review_rules"
                ]
            )

            print(
                "Missing Mandatory Skills:",
                eligibility_result[
                    "missing_mandatory_skills"
                ]
            )

        except Exception as e:

            print(
                f"\nError processing {file_name}: {e}"
            )

            traceback.print_exc()

    # ---------------------------------
    # Check Candidate Results
    # ---------------------------------

    if not candidates:

        print(
            "No candidate CVs found."
        )

        return

    # ---------------------------------
    # Day 15:
    # Fairness / Bias Evaluation
    # ---------------------------------

    bias_result = (
        bias_evaluator.evaluate(
            candidates
        )
    )

    print(
        "\n===== FAIRNESS / BIAS EVALUATION =====\n"
    )

    print(
        "Candidate Count:",
        bias_result[
            "candidate_count"
        ]
    )

    print(
        "Score Range:",
        bias_result[
            "score_range"
        ]
    )

    print(
        "Bias Indicators:",
        bias_result[
            "bias_indicators"
        ]
    )

    # ---------------------------------
    # Day 14:
    # Rank Candidates
    # ---------------------------------

    ranked_candidates = (
        ranking_engine.rank_candidates(
            candidates
        )
    )

    # ---------------------------------
    # Final Day 21 Output
    # ---------------------------------

    print(
        "\n===== FINAL CANDIDATE "
        "ELIGIBILITY RANKING =====\n"
    )

    for candidate in ranked_candidates:

        print(
            f'Rank {candidate["rank"]}: '
            f'{candidate["candidate"]} | '
            f'Score: {candidate["score"]}% | '
            f'Status: {candidate["status"]}'
        )


if __name__ == "__main__":

    main()