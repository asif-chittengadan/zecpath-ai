import os
import json

from parsers.pdf_reader import PDFReader
from parsers.docx_reader import DOCXReader
from parsers.text_cleaner import TextCleaner
from parsers.section_classifier import SectionClassifier


pdf_reader = PDFReader()
docx_reader = DOCXReader()
cleaner = TextCleaner()
classifier = SectionClassifier()

folder = "data/resumes"

files = [

    file

    for file in os.listdir(folder)

    if file.lower().endswith((".pdf", ".docx"))

]

for file_name in files:

    print("=" * 70)
    print(file_name)
    print("=" * 70)

    path = os.path.join(folder, file_name)

    if file_name.lower().endswith(".pdf"):

        text = pdf_reader.extract_text(path)

    else:

        text = docx_reader.extract_text(path)

    text = cleaner.clean(text)

    sections = classifier.classify(text)

    print(json.dumps(sections, indent=4, ensure_ascii=False))