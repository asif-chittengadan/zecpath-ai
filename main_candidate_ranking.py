import copy
import json
import os

from scoring.candidate_matching_service import CandidateMatchingService
from scoring.ranking_engine import RankingEngine
from scoring.shortlisting_module import ShortlistingModule
from parsers.normalizer import Normalizer
from scoring.fairness_masker import FairnessMasker
from scoring.bias_evaluator import BiasEvaluator


CV_FOLDER = "data/labeled_resumes"

JD_PATH = (
    "data/parsed_jd/"
    "JD_Solution Consultant Apprentice(1).json"
)


def load_json(path):

    with open(
        path,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


def normalize_resume(resume, normalizer):

    normalized = copy.deepcopy(resume)

    text_fields = [
        "Summary",
        "Projects",
        "Others"
    ]

    for field in text_fields:

        value = normalized.get(field)

        if isinstance(value, list):

            normalized[field] = [
                normalizer.normalize(str(item))
                for item in value
            ]

        elif isinstance(value, str):

            normalized[field] = normalizer.normalize(
                value
            )

    return normalized


def main():

    job_description = load_json(
        JD_PATH
    )

    matching_service = CandidateMatchingService()

    ranking_engine = RankingEngine()

    shortlisting_module = ShortlistingModule()

    normalizer = Normalizer()

    fairness_masker = FairnessMasker()

    bias_evaluator = BiasEvaluator()

    candidates = []

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

            resume = load_json(
                cv_path
            )

            # Day 15: normalize resume
            normalized_resume = normalize_resume(
                resume,
                normalizer
            )

            # Preserve candidate identity
            candidate_name = normalized_resume.get(
                "Others",
                ["Unknown"]
            )[0]

            # Day 15: create scoring-safe copy
            scoring_resume = fairness_masker.mask(
                normalized_resume
            )

            # Day 13: calculate actual CV ↔ JD score
            result = matching_service.generate_score(
                scoring_resume,
                job_description
            )

            candidates.append({
                "candidate": candidate_name,
                "score": result["percentage"],
                "source_file": file_name
            })

        except Exception as e:

            print(
                f"Error processing {file_name}: {e}"
            )

    if not candidates:

        print(
            "No candidate CVs found."
        )

        return

    # Day 15: evaluate score distribution
    bias_result = bias_evaluator.evaluate(
        candidates
    )

    print(
        "\n===== FAIRNESS / BIAS EVALUATION =====\n"
    )

    print(
        "Candidate Count:",
        bias_result["candidate_count"]
    )

    print(
        "Score Range:",
        bias_result["score_range"]
    )

    print(
        "Bias Indicators:",
        bias_result["bias_indicators"]
    )

    # Day 14: rank candidates
    ranked_candidates = ranking_engine.rank_candidates(
        candidates
    )

    # Day 14: shortlist / review / reject
    recruiter_output = ranking_engine.build_recruiter_output(
        ranked_candidates,
        shortlisting_module
    )

    print(
        "\n===== FINAL CANDIDATE RANKING =====\n"
    )

    for candidate in recruiter_output:

        print(
            f'Rank {candidate["rank"]}: '
            f'{candidate["candidate"]} | '
            f'Score: {candidate["score"]}% | '
            f'Status: {candidate["status"]}'
        )


if __name__ == "__main__":
    main()