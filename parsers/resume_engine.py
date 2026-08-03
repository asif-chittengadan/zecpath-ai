import os

from parsers.pdf_reader import PDFReader
from parsers.docx_reader import DOCXReader
from parsers.text_cleaner import TextCleaner
from parsers.normalizer import Normalizer
from parsers.output_writer import OutputWriter


class ResumeEngine:

    def process(self, file_path):

        extension = os.path.splitext(file_path)[1].lower()

        if extension == ".pdf":

            raw = PDFReader().extract_text(file_path)

        elif extension == ".docx":

            raw = DOCXReader().extract_text(file_path)

        else:

            raise Exception("Unsupported File")

        cleaned = TextCleaner().clean(raw)

        normalized = Normalizer().normalize(cleaned)

        output_name = os.path.basename(file_path).split('.')[0] + ".txt"

        OutputWriter().save(output_name, normalized)

        return normalized