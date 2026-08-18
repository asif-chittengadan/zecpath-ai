import json
import os
import time

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

    print("\n===== DAY 18 WARM MODEL BENCHMARK =====\n")

    job_description = load_json(JD_PATH)

    cv_files = [
        file_name
        for file_name in os.listdir(CV_FOLDER)
        if file_name.lower().endswith(".json")
    ]

    if not cv_files:

        print("No CV JSON files found.")

        return

    service = CandidateMatchingService()

    # -------------------------------------------------
    # Warm-up
    # -------------------------------------------------

    print("Loading model and performing warm-up...")

    first_resume = load_json(
        os.path.join(
            CV_FOLDER,
            cv_files[0]
        )
    )

    warmup_start = time.perf_counter()

    service.generate_score(
        first_resume,
        job_description
    )

    warmup_time = (
        time.perf_counter() - warmup_start
    )

    print(
        f"Warm-up / first scoring: "
        f"{warmup_time:.4f} seconds"
    )

    # -------------------------------------------------
    # Warm scoring
    # -------------------------------------------------

    print("\n===== WARM SCORING =====")

    timings = []

    for file_name in cv_files:

        resume_path = os.path.join(
            CV_FOLDER,
            file_name
        )

        resume = load_json(
            resume_path
        )

        start = time.perf_counter()

        result = service.generate_score(
            resume,
            job_description
        )

        elapsed = (
            time.perf_counter() - start
        )

        timings.append(elapsed)

        print(
            f"{file_name}: "
            f"{elapsed:.4f} seconds | "
            f"Score: {result['percentage']}%"
        )

    # -------------------------------------------------
    # Summary
    # -------------------------------------------------

    average_time = (
        sum(timings) / len(timings)
    )

    total_warm_time = sum(
        timings
    )

    print(
        "\n===== DAY 18 WARM BENCHMARK SUMMARY ====="
    )

    print(
        f"Candidates tested: "
        f"{len(timings)}"
    )

    print(
        f"Total warm scoring time: "
        f"{total_warm_time:.4f} seconds"
    )

    print(
        f"Average warm scoring time: "
        f"{average_time:.4f} seconds"
    )

    cache_info = service.semantic_engine._encode_cached.cache_info()

    print(
        f"Embedding Cache Hits: {cache_info.hits}"
    )

    print(
        f"Embedding Cache Misses: {cache_info.misses}"
    )

    print(
        f"Embedding Cache Size: {cache_info.currsize}"
    )

    print(
        "\n===== BENCHMARK COMPLETE =====\n"
    )


if __name__ == "__main__":
    main()