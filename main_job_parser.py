import os

from utils.logger import logger
from parsers.job_parser import JobParser
from parsers.jd_builder import JDBuilder

logger.info("Zecpath AI Job Description Parser Started")


def main():

    folder = "data/job_descriptions"

    output_folder = "data/parsed_jd"

    pdf_files = [
        f for f in os.listdir(folder)
        if f.lower().endswith(".pdf")
    ]

    if not pdf_files:
        print("No Job Description PDFs found.")
        return

    parser = JobParser()
    builder = JDBuilder()

    for pdf in pdf_files:

        pdf_path = os.path.join(folder, pdf)

        print(f"\nProcessing: {pdf}")

        parsed_jd = parser.parse(pdf_path)

        output_file = os.path.splitext(pdf)[0] + ".json"

        output_path = os.path.join(
            output_folder,
            output_file
        )

        builder.save(parsed_jd, output_path)

        print(f"Saved: {output_path}")


if __name__ == "__main__":
    main()