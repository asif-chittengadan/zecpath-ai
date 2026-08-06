import os

from parsers.pdf_reader import PDFReader
from parsers.docx_reader import DOCXReader
from parsers.text_cleaner import TextCleaner
from parsers.section_classifier import SectionClassifier
from parsers.section_builder import SectionBuilder


def main():

    input_folder = "data/resumes"

    output_folder = "data/labeled_resumes"

    os.makedirs(output_folder, exist_ok=True)

    pdf_reader = PDFReader()
    docx_reader = DOCXReader()

    cleaner = TextCleaner()

    classifier = SectionClassifier()

    builder = SectionBuilder()

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