from parsers.pdf_reader import PDFReader
from parsers.docx_reader import DOCXReader
from parsers.text_cleaner import TextCleaner

from parsers.section_splitter import SectionSplitter

from parsers.personal_info_extractor import PersonalInfoExtractor
from parsers.resume_skill_extractor import SkillExtractor
from parsers.resume_education_extractor import EducationExtractor
from parsers.resume_experience_extractor import ResumeExperienceExtractor
from parsers.project_extractor import ProjectExtractor
from parsers.certification_extractor import CertificationExtractor
from parsers.language_extractor import LanguageExtractor
from parsers.resume_errors import (
    ResumeExtractionError,
    ResumeParsingError,
    validate_resume_path,
)


class ResumeSectionParser:

    def __init__(self):

        self.pdf_reader = PDFReader()

        self.docx_reader = DOCXReader()

        self.cleaner = TextCleaner()

        self.splitter = SectionSplitter()

        self.personal = PersonalInfoExtractor()

        self.skills = SkillExtractor()

        self.education = EducationExtractor()

        self.experience = ResumeExperienceExtractor()

        self.projects = ProjectExtractor()

        self.certifications = CertificationExtractor()

        self.languages = LanguageExtractor()

    def parse(self, resume_path):
        path = validate_resume_path(resume_path)
        try:
            if path.suffix.lower() == ".pdf":
                raw_text = self.pdf_reader.extract_text(str(path))
            else:
                raw_text = self.docx_reader.extract_text(str(path))
        except Exception as exc:
            raise ResumeExtractionError(
                f"Could not read resume '{path.name}'. Check that the file is valid and accessible."
            ) from exc

        if not isinstance(raw_text, str) or not raw_text.strip():
            raise ResumeExtractionError(
                f"No readable text was found in '{path.name}'. "
                "The file may be empty, damaged, or image-only."
            )

        try:
            text = self.cleaner.clean(raw_text)
            if not text.strip():
                raise ResumeParsingError(
                    f"Resume '{path.name}' did not contain usable text after cleanup."
                )
            sections = self.splitter.split(text)
        except ResumeParsingError:
            raise
        except Exception as exc:
            raise ResumeParsingError(
                f"Could not parse sections from resume '{path.name}'."
            ) from exc

        # -----------------------------------
        # Header
        # -----------------------------------

        header = sections.get(

            "Header",

            []

        )

        # -----------------------------------
        # Extract
        # -----------------------------------

        try:
            result = {
                "personal_information": self.personal.extract(header),
                "summary": sections.get("Summary", []),
                "skills": self.skills.extract(sections.get("Skills", [])),
                "education": self.education.extract(
                    sections.get("Education", [])
                ),
                "experience": self.experience.extract(
                    sections.get("Experience", [])
                ),
                "projects": self.projects.extract(
                    sections.get("Projects", [])
                ),
                "certifications": self.certifications.extract(
                    sections.get("Certifications", [])
                ),
                "languages": self.languages.extract(
                    sections.get("Languages", [])
                ),
                "achievements": sections.get("Achievements", []),
                "interests": sections.get("Interests", []),
            }
        except Exception as exc:
            raise ResumeParsingError(
                f"Could not extract structured fields from resume '{path.name}'."
            ) from exc

        return result
