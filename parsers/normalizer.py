import re


class Normalizer:

    def __init__(self):

        self.replacements = {
            # -----------------------------
            # Summary
            # -----------------------------
            "professional summary": "Summary",
            "career summary": "Summary",
            "profile summary": "Summary",
            "career profile": "Summary",
            "professional profile": "Summary",
            "career objective": "Summary",
            "objective": "Summary",

            # -----------------------------
            # Skills
            # -----------------------------
            "technical skills": "Skills",
            "technical skill": "Skills",
            "key skills": "Skills",
            "core skills": "Skills",
            "core competencies": "Skills",
            "technical expertise": "Skills",
            "skills & expertise": "Skills",
            "skills and expertise": "Skills",

            # -----------------------------
            # Experience
            # -----------------------------
            "professional experience": "Experience",
            "work experience": "Experience",
            "employment history": "Experience",
            "work history": "Experience",
            "career history": "Experience",
            "professional background": "Experience",
            "employment experience": "Experience",

            # -----------------------------
            # Education
            # -----------------------------
            "educational qualification": "Education",
            "educational qualifications": "Education",
            "education qualification": "Education",
            "academic details": "Education",
            "academic background": "Education",
            "academic qualifications": "Education",
            "academic qualification": "Education",
            "educational background": "Education",

            # -----------------------------
            # Projects
            # -----------------------------
            "project experience": "Projects",
            "academic projects": "Projects",
            "academic project": "Projects",
            "personal projects": "Projects",
            "personal project": "Projects",
            "key projects": "Projects",
            "major projects": "Projects",

            # -----------------------------
            # Certifications
            # -----------------------------
            "certificates": "Certifications",
            "certificate": "Certifications",
            "professional certifications": "Certifications",
            "professional certificates": "Certifications",
            "certification": "Certifications",

            # -----------------------------
            # Other Information
            # -----------------------------
            "additional information": "Others",
            "additional details": "Others",
            "other information": "Others",
            "personal information": "Others",
            "personal details": "Others"
        }

        self.compiled_replacements = [
            (
                re.compile(
                    r"^\s*" + re.escape(old) + r"\s*"
                    r"[:\-–—]*\s*$",
                    re.IGNORECASE
                ),
                new
            )
            for old, new in self.replacements.items()
        ]

    def normalize(self, text):

        if not text:
            return ""

        lines = text.splitlines()
        normalized_lines = []

        for line in lines:

            cleaned_line = re.sub(
                r"\s+",
                " ",
                line
            ).strip()

            if not cleaned_line:
                normalized_lines.append("")
                continue

            normalized_heading = self.__normalize_heading(
                cleaned_line
            )

            normalized_lines.append(
                normalized_heading
            )

        return "\n".join(
            normalized_lines
        )

    def __normalize_heading(self, line):

        for pattern, replacement in self.compiled_replacements:

            if pattern.match(line):

                return replacement

        return line