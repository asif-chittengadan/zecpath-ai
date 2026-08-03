from utils.logger import logger
from parsers.resume_engine import ResumeEngine

logger.info("Zecpath AI Resume Text Extraction Engine Started")

def main():
    resume_path = "data/resumes/mycv.pdf"   # Change this to your resume file

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