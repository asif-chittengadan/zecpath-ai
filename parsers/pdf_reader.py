import fitz


class PDFReader:

    def extract_text(self, file_path):
        with fitz.open(file_path) as document:
            return "\n".join(
                page.get_text("text")
                for page in document
            )
