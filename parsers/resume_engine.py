from parsers.pdf_reader import PDFReader
from parsers.docx_reader import DOCXReader
from parsers.text_cleaner import TextCleaner
from parsers.normalizer import Normalizer
from parsers.output_writer import OutputWriter
from parsers.resume_errors import (
    ResumeExtractionError,
    ResumeOutputError,
    ResumeParsingError,
    validate_resume_path,
)


class ResumeEngine:

    def process(self, file_path):
        path = validate_resume_path(file_path)

        try:
            if path.suffix.lower() == ".pdf":
                raw = PDFReader().extract_text(str(path))
            else:
                raw = DOCXReader().extract_text(str(path))
        except Exception as exc:
            raise ResumeExtractionError(
                f"Could not read resume '{path.name}'. Check that the file is valid and accessible."
            ) from exc

        if not isinstance(raw, str) or not raw.strip():
            raise ResumeExtractionError(
                f"No readable text was found in '{path.name}'. "
                "The file may be empty, damaged, or image-only."
            )

        try:
            cleaned = TextCleaner().clean(raw)
            normalized = Normalizer().normalize(cleaned)
        except Exception as exc:
            raise ResumeParsingError(
                f"Could not clean or normalize resume '{path.name}'."
            ) from exc

        if not normalized.strip():
            raise ResumeParsingError(
                f"Resume '{path.name}' did not contain usable text after cleanup."
            )

        output_name = f"{path.stem}.txt"
        try:
            OutputWriter().save(output_name, normalized)
        except Exception as exc:
            raise ResumeOutputError(
                f"Could not save processed resume output for '{path.name}'."
            ) from exc

        return normalized
