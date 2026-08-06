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

        # -----------------------------------
        # Read Resume
        # -----------------------------------

        if resume_path.lower().endswith(".pdf"):

            text = self.pdf_reader.extract_text(
                resume_path
            )

        elif resume_path.lower().endswith(".docx"):

            text = self.docx_reader.extract_text(
                resume_path
            )

        else:

            raise Exception(
                "Unsupported Resume Format"
            )

        # -----------------------------------
        # Clean Resume
        # -----------------------------------

        text = self.cleaner.clean(text)

        # -----------------------------------
        # Split Resume
        # -----------------------------------

        sections = self.splitter.split(text)

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

        result = {

            "personal_information":

                self.personal.extract(

                    header

                ),

            "summary":

                sections.get(

                    "Summary",

                    []

                ),

            "skills":

                self.skills.extract(

                    sections.get(

                        "Skills",

                        []

                    )

                ),

            "education":

                self.education.extract(

                    sections.get(

                        "Education",

                        []

                    )

                ),

            "experience":

                self.experience.extract(

                    sections.get(

                        "Experience",

                        []

                    )

                ),

            "projects":

                self.projects.extract(

                    sections.get(

                        "Projects",

                        []

                    )

                ),

            "certifications":

                self.certifications.extract(

                    sections.get(

                        "Certifications",

                        []

                    )

                ),

            "languages":

                self.languages.extract(

                    sections.get(

                        "Languages",

                        []

                    )

                ),

            "achievements":

                sections.get(

                    "Achievements",

                    []

                ),

            "interests":

                sections.get(

                    "Interests",

                    []

                )

        }

        return result