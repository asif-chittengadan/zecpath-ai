import re
import unicodedata


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

        # -----------------------------
        # Unicode normalization
        # -----------------------------

        text = unicodedata.normalize(
            "NFKC",
            str(text)
        )

        # -----------------------------
        # Normalize common PDF artifacts
        # -----------------------------

        text = text.replace(
            "\u00a0",
            " "
        )

        text = text.replace(
            "\u200b",
            ""
        )

        text = text.replace(
            "\u200c",
            ""
        )

        text = text.replace(
            "\u200d",
            ""
        )

        text = text.replace(
            "\ufeff",
            ""
        )

        # -----------------------------
        # Normalize dash variations
        # -----------------------------

        text = re.sub(
            r"[‐-‒–—―]",
            "-",
            text
        )

        # -----------------------------
        # Normalize bullet characters
        # -----------------------------

        text = re.sub(
            r"[•●▪◦‣⁃]",
            "-",
            text
        )

        # -----------------------------
        # Remove control characters
        # while preserving newlines/tabs
        # -----------------------------

        text = "".join(
            character
            for character in text
            if character in "\n\t"
            or unicodedata.category(character)[0] != "C"
        )

        # -----------------------------
        # Process lines
        # -----------------------------

        lines = text.splitlines()

        normalized_lines = []

        for line in lines:

            # Replace tabs with spaces
            line = line.replace(
                "\t",
                " "
            )

            # Collapse repeated whitespace
            cleaned_line = re.sub(
                r"[ ]+",
                " ",
                line
            ).strip()

            # Preserve blank lines temporarily
            if not cleaned_line:

                normalized_lines.append("")

                continue

            # Normalize section headings
            normalized_heading = (
                self.__normalize_heading(
                    cleaned_line
                )
            )

            normalized_lines.append(
                normalized_heading
            )

        # -----------------------------
        # Remove excessive blank lines
        # -----------------------------

        result_lines = []

        previous_blank = False

        for line in normalized_lines:

            is_blank = not line.strip()

            if is_blank:

                if previous_blank:
                    continue

                previous_blank = True

            else:

                previous_blank = False

            result_lines.append(
                line
            )

        return "\n".join(
            result_lines
        ).strip()

    def __normalize_heading(
        self,
        line
    ):

        for pattern, replacement in (
            self.compiled_replacements
        ):

            if pattern.match(line):

                return replacement

        return line