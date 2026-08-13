import json
import os

from scoring.candidate_matching_service import CandidateMatchingService
from scoring.ranking_engine import RankingEngine
from scoring.shortlisting_module import ShortlistingModule


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


def main():

    job_description = load_json(
        JD_PATH
    )

    matching_service = CandidateMatchingService()

    ranking_engine = RankingEngine()

    shortlisting_module = ShortlistingModule()

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

            result = matching_service.generate_score(
                resume,
                job_description
            )

            candidates.append({
                "candidate": result["candidate"],
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

    ranked_candidates = ranking_engine.rank_candidates(
        candidates
    )

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