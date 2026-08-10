import os

from parsers.pdf_reader import PDFReader
from parsers.docx_reader import DOCXReader
from parsers.text_cleaner import TextCleaner
from parsers.section_classifier import SectionClassifier
from parsers.section_builder import SectionBuilder
from parsers.resume_skill_extractor import SkillExtractor
from parsers.resume_experience_extractor import ResumeExperienceExtractor
from parsers.resume_education_extractor import EducationExtractor
from parsers.resume_certification_extractor import CertificationExtractor


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

    education_extractor = EducationExtractor()

    certification_extractor = CertificationExtractor()

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

        # ----------------------------
        # Education Extraction
        # ----------------------------

        education_lines = sections.get(
            "Education",
            []
        )

        education_text = "\n".join(
            education_lines
        )

        degree_types = education_extractor.extract_degree(
            education_text
        )

        fields_of_study = education_extractor.extract_field_of_study(
            education_text
        )

        institutions = education_extractor.extract_institution(
            education_text
        )

        graduation_year = education_extractor.extract_graduation_year(
            education_text
        )

        education_output = {
            "degree": degree_types[0] if degree_types else "",
            "field_of_study": fields_of_study[0] if fields_of_study else "",
            "institution": institutions[0] if institutions else "",
            "graduation_year": graduation_year
        }


        # ----------------------------
        # Certification Extraction
        # ----------------------------

        certification_lines = sections.get(
            "Certifications",
            []
        )

        certification_output = certification_extractor.extract(
            certification_lines
        )

        if "Skills" in sections:

            sections["Skills"] = skill_extractor.extract(

                sections["Skills"]

            )

        experience_lines = sections.get("Experience", [])

        print("\n===== EXPERIENCE INPUT =====")

        for line in experience_lines:
            print(repr(line))

        companies = experience_extractor.extract_companies(
            experience_lines
        )

        roles = experience_extractor.extract_roles(
            experience_lines
        )

        dates = experience_extractor.extract_dates(
            experience_lines
        )
        print("\n===== EXTRACTED DATES =====")
        print(dates)

        durations = experience_extractor.extract_durations(
            experience_lines
        )
        print("\n===== EXTRACTED DURATIONS =====")
        print(durations)

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


        sections.pop("Education", None)
        sections["Education"] = education_output

        sections.pop("Certifications", None)
        sections["Certifications"] = certification_output

        sections.pop("Experience", None)
        sections["Experience"] = experience_output

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

        builder.save(
            sections,
            output_path
        )

        print(

            f"Saved : {output_path}"

        )


if __name__ == "__main__":

    main()