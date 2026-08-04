import os

from utils.logger import logger
from parsers.resume_engine import ResumeEngine

logger.info("Zecpath AI Resume Text Extraction Engine Started")


def main():

    folder = "data/resumes"

    pdf_files = [f for f in os.listdir(folder) if f.lower().endswith(".pdf")]

    if not pdf_files:
        print("No resume PDF found in data/resumes")
        return

    resume_path = os.path.join(folder, pdf_files[0])

    engine = ResumeEngine()

    try:

        cleaned_text = engine.process(resume_path)

        print("\n===== CLEANED RESUME TEXT =====\n")

        print(cleaned_text)

        logger.info("Resume processed successfully.")

    except Exception as e:

        logger.error(f"Error processing resume: {e}")

        print(f"Error: {e}")


if __name__ == "__main__":
    main()