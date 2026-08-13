import json
import re

class RoleExtractor:

    def __init__(self):

        with open(
            "data/roles.json",
            "r",
            encoding="utf-8"
        ) as file:

            self.roles = json.load(file)

        self.roles.sort(
            key=len,
            reverse=True
        )

    def extract(self, text, full_text=None):

        if not text:
            text = ""

        if not full_text:
            full_text = text

        # Normalize whitespace
        text = re.sub(
            r"\s+",
            " ",
            text
        ).strip()

        full_text = re.sub(
            r"\s+",
            " ",
            full_text
        ).strip()

        # --------------------------------
        # 1. Search job title
        # --------------------------------

        title_patterns = [
            r"Job Description\s*[-–—:]\s*(.*?)(?:Job Summary|Role Overview|$)",
            r"Job Title\s*[:\-–—]\s*(.*?)(?:Job Summary|Role Overview|$)",
            r"Position\s*[:\-–—]\s*(.*?)(?:Job Summary|Role Overview|$)",
            r"Role\s*[:\-–—]\s*(.*?)(?:Job Summary|Role Overview|$)"
        ]

        for pattern in title_patterns:

            match = re.search(
                pattern,
                full_text,
                re.IGNORECASE
            )

            if not match:
                continue

            title = match.group(1).strip()

            title_matches = []

            for role in self.roles:

                if re.search(
                    r"(?<![A-Za-z0-9])"
                    + re.escape(role)
                    + r"(?![A-Za-z0-9])",
                    title,
                    re.IGNORECASE
                ):

                    title_matches.append(role)

            if title_matches:

                return max(
                    title_matches,
                    key=len
                )

        # --------------------------------
        # 2. Search Job Roles section
        # --------------------------------

        match = re.search(
            r"Job Roles?\s*:?(.*?)(?:Work Location|"
            r"Number of Positions|Compensation|"
            r"Preferred Languages|Selection Procedure|\Z)",
            text,
            re.IGNORECASE | re.DOTALL
        )

        if match:

            search_text = match.group(1)

            section_matches = []

            for role in self.roles:

                if re.search(
                    r"(?<![A-Za-z0-9])"
                    + re.escape(role)
                    + r"(?![A-Za-z0-9])",
                    search_text,
                    re.IGNORECASE
                ):

                    section_matches.append(role)

            if section_matches:

                return max(
                    section_matches,
                    key=len
                )

        # --------------------------------
        # 3. Fallback: search full document
        # --------------------------------

        full_matches = []

        for role in self.roles:

            if re.search(
                r"(?<![A-Za-z0-9])"
                + re.escape(role)
                + r"(?![A-Za-z0-9])",
                full_text,
                re.IGNORECASE
            ):

                full_matches.append(role)

        if full_matches:

            return max(
                full_matches,
                key=len
            )

        return ""