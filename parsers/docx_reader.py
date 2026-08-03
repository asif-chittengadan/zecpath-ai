from docx import Document


class DOCXReader:

    def extract_text(self, file_path):

        document = Document(file_path)

        text = ""

        for paragraph in document.paragraphs:

            text += paragraph.text + "\n"

        return text