import os

from parsers.pdf_reader import PDFReader
from parsers.docx_reader import DOCXReader
from parsers.text_cleaner import TextCleaner
from parsers.section_classifier import SectionClassifier
from parsers.section_builder import SectionBuilder
from parsers.resume_skill_extractor import SkillExtractor
from parsers.resume_experience_extractor import ResumeExperienceExtractor

def main():

    input_folder = "data/resumes"

    output_folder = "data/labeled_resumes"

    os.makedirs(output_folder, exist_ok=True)

    pdf_reader = PDFReader()
    docx_reader = DOCXReader()

    cleaner = TextCleaner()

    classifier = SectionClassifier()

    builder = SectionBuilder()

    skill_extractor = SkillExtractor()

    experience_extractor = ResumeExperienceExtractor()

    files = [

        file

        for file in os.listdir(input_folder)

        if file.lower().endswith((".pdf", ".docx"))

    ]

    if not files:

        print("No resumes found.")

        return

    for file_name in files:

        print(f"\nProcessing : {file_name}")

        resume_path = os.path.join(

            input_folder,

            file_name

        )

        # ----------------------------
        # Read Resume
        # ----------------------------

        if file_name.lower().endswith(".pdf"):

            text = pdf_reader.extract_text(

                resume_path

            )

        else:

            text = docx_reader.extract_text(

                resume_path

            )

        # ----------------------------
        # Clean Resume
        # ----------------------------

        text = cleaner.clean(text)

        # ----------------------------
        # Classify Sections
        # ----------------------------

        sections = classifier.classify(text)

        if "Skills" in sections:

            sections["Skills"] = skill_extractor.extract(

                sections["Skills"]

            )

        experience_lines = sections.get("Experience", [])

        companies = experience_extractor.extract_companies(
            experience_lines
        )

        roles = experience_extractor.extract_roles(
            experience_lines
        )

        dates = experience_extractor.extract_dates(
            experience_lines
        )

        durations = experience_extractor.extract_durations(
            experience_lines
        )

        total_experience = experience_extractor.calculate_total_experience(
            dates,
            durations
        )

        gaps = experience_extractor.detect_gaps(
            dates
        )

        overlaps = experience_extractor.detect_overlaps(
            dates
        )

        experience_output = experience_extractor.build_experience_output(
            companies,
            roles,
            dates,
            durations
        )

        experience_output["total_experience"] = total_experience
        experience_output["gaps"] = gaps
        experience_output["overlaps"] = overlaps

        # ----------------------------
        # Save JSON
        # ----------------------------

        output_name = os.path.splitext(

            file_name

        )[0] + ".json"

        output_path = os.path.join(

            output_folder,

            output_name

        )

        sections.pop("Experience", None)
        sections["Experience"] = experience_output

        builder.save(
            sections,
            output_path
        )

        print(

            f"Saved : {output_path}"

        )


if __name__ == "__main__":

    main()