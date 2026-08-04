from parsers.pdf_reader import PDFReader
from parsers.jd_cleaner import JDCleaner
from parsers.jd_normalizer import JDNormalizer
from parsers.section_extractor import SectionExtractor

from parsers.role_extractor import RoleExtractor
from parsers.skill_extractor import SkillExtractor
from parsers.experience_extractor import ExperienceExtractor
from parsers.education_extractor import EducationExtractor

from parsers.jd_builder import JDBuilder


class JobParser:

    def __init__(self):

        self.reader = PDFReader()

        self.cleaner = JDCleaner()

        self.normalizer = JDNormalizer()

        self.section_extractor = SectionExtractor()

        self.role_extractor = RoleExtractor()

        self.skill_extractor = SkillExtractor()

        self.experience_extractor = ExperienceExtractor()

        self.education_extractor = EducationExtractor()

        self.builder = JDBuilder()

    def parse(self, pdf_path):

        # Read PDF
        text = self.reader.extract_text(pdf_path)

        # Clean JD
        text = self.cleaner.clean(text)

        # Normalize JD
        text = self.normalizer.normalize(text)

        # Extract Information
        sections = self.section_extractor.extract(text)

        role_text = (
            sections.get("roles", "") +
            "\n" +
            sections.get("job_details", "")
        )

        role = self.role_extractor.extract(role_text)

        skills = self.skill_extractor.extract(
            sections.get("skills", text)
        )

        experience_text = (
            sections.get("experience", "") +
            "\n" +
            sections.get("education", "")
        )

        experience = self.experience_extractor.extract(
            experience_text
        )

        education = self.education_extractor.extract(
            sections.get("education", text)
        )

        # Build JSON
        return self.builder.build(

            role,

            skills,

            experience,

            education

        )