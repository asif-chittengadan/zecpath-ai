import json
import os
import tracemalloc

from scoring.candidate_matching_service import CandidateMatchingService


CV_FOLDER = "data/labeled_resumes"
JD_PATH = "data/parsed_jd/JD_Solution Consultant Apprentice(1).json"


def load_json(path):

    with open(
        path,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


def main():

    print("\n===== DAY 18 MEMORY BENCHMARK =====\n")

    job_description = load_json(JD_PATH)

    cv_files = [
        file_name
        for file_name in os.listdir(CV_FOLDER)
        if file_name.lower().endswith(".json")
    ]

    service = CandidateMatchingService()

    tracemalloc.start()

    for file_name in cv_files:

        resume = load_json(
            os.path.join(
                CV_FOLDER,
                file_name
            )
        )

        service.generate_score(
            resume,
            job_description
        )

        current, peak = tracemalloc.get_traced_memory()

        print(
            f"{file_name} | "
            f"Current: {current / 1024:.2f} KB | "
            f"Peak: {peak / 1024:.2f} KB"
        )

    current, peak = tracemalloc.get_traced_memory()

    tracemalloc.stop()

    print("\n===== MEMORY SUMMARY =====")

    print(
        f"Final Current Memory: "
        f"{current / 1024:.2f} KB"
    )

    print(
        f"Final Peak Memory: "
        f"{peak / 1024:.2f} KB"
    )

    print(
        "\n===== MEMORY BENCHMARK COMPLETE =====\n"
    )


if __name__ == "__main__":
    main()