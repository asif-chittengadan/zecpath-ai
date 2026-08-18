import json
import os
import time
import tracemalloc

from parsers.pdf_reader import PDFReader
from parsers.resume_engine import ResumeEngine
from scoring.candidate_matching_service import CandidateMatchingService


CV_FOLDER = "data/labeled_resumes"
JD_FOLDER = "data/parsed_jd"

CV_FILE = "cv-2.json"
JD_FILE = "JD_Solution Consultant Apprentice(1).json"


def load_json(path):

    with open(
        path,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


def find_pdf(folder):

    for file_name in os.listdir(folder):

        if file_name.lower().endswith(".pdf"):

            return os.path.join(
                folder,
                file_name
            )

    return None


def main():

    print(
        "\n===== DAY 18 PERFORMANCE BASELINE =====\n"
    )

    # -------------------------------------------------
    # 1. Text extraction benchmark
    # -------------------------------------------------

    pdf_path = find_pdf(
        "data/resumes"
    )

    if pdf_path:

        reader = PDFReader()

        start = time.perf_counter()

        text = reader.extract_text(
            pdf_path
        )

        extraction_time = (
            time.perf_counter() - start
        )

        print(
            f"Text Extraction Time: "
            f"{extraction_time:.4f} seconds"
        )

        print(
            f"Extracted Characters: "
            f"{len(text)}"
        )

    else:

        extraction_time = 0

        print(
            "No PDF found in data/resumes"
        )

    # -------------------------------------------------
    # 2. Resume engine benchmark
    # -------------------------------------------------

    if pdf_path:

        engine = ResumeEngine()

        start = time.perf_counter()

        engine.process(
            pdf_path
        )

        resume_processing_time = (
            time.perf_counter() - start
        )

        print(
            f"Resume Processing Time: "
            f"{resume_processing_time:.4f} seconds"
        )

    else:

        resume_processing_time = 0

    # -------------------------------------------------
    # 3. ATS scoring benchmark
    # -------------------------------------------------

    cv_path = os.path.join(
        CV_FOLDER,
        CV_FILE
    )

    jd_path = os.path.join(
        JD_FOLDER,
        JD_FILE
    )

    if not os.path.exists(cv_path):

        print(
            f"CV not found: {cv_path}"
        )

        return

    if not os.path.exists(jd_path):

        print(
            f"JD not found: {jd_path}"
        )

        return

    resume = load_json(
        cv_path
    )

    job_description = load_json(
        jd_path
    )

    matching_service = (
        CandidateMatchingService()
    )

    # -------------------------------------------------
    # 4. Memory + scoring benchmark
    # -------------------------------------------------

    tracemalloc.start()

    start = time.perf_counter()

    result = matching_service.generate_score(
        resume,
        job_description
    )

    scoring_time = (
        time.perf_counter() - start
    )

    current_memory, peak_memory = (
        tracemalloc.get_traced_memory()
    )

    tracemalloc.stop()

    print(
        f"Scoring Time: "
        f"{scoring_time:.4f} seconds"
    )

    print(
        f"Current Memory: "
        f"{current_memory / 1024:.2f} KB"
    )

    print(
        f"Peak Memory: "
        f"{peak_memory / 1024:.2f} KB"
    )

    # -------------------------------------------------
    # 5. Summary
    # -------------------------------------------------

    total_time = (
        extraction_time
        + resume_processing_time
        + scoring_time
    )

    print(
        f"\nTotal Measured Time: "
        f"{total_time:.4f} seconds"
    )

    print(
        f"ATS Score: "
        f"{result['percentage']}%"
    )

    print(
        "\n===== BASELINE COMPLETE =====\n"
    )


if __name__ == "__main__":
    main()