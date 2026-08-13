import json
import re


class EducationExtractor:

    def __init__(self):

        with open(
            "data/education.json",
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(file)

        if isinstance(data, dict):

            self.degree_types = data.get(
                "degree_types",
                []
            )

            self.fields_of_study = data.get(
                "fields_of_study",
                []
            )

        else:

            self.degree_types = data
            self.fields_of_study = []

        self.degree_types = sorted(
            set(self.degree_types),
            key=len,
            reverse=True
        )

        self.fields_of_study = sorted(
            set(self.fields_of_study),
            key=len,
            reverse=True
        )

        self.aliases = {
            "be": "B.E",
            "b e": "B.E",
            "b.e.": "B.E",
            "btech": "B.Tech",
            "b tech": "B.Tech",
            "b.tech.": "B.Tech",
            "me": "M.E",
            "m e": "M.E",
            "m.e.": "M.E",
            "mtech": "M.Tech",
            "m tech": "M.Tech",
            "m.tech.": "M.Tech"
        }

    def extract(self, text):

        if not text:
            return []

        education = []

        # --------------------------------
        # Education-related text
        # --------------------------------

        match = re.search(
            r"(Education|Educational Qualification|"
            r"Eligibility & Qualifications|Academic Requirement)"
            r"\s*:?(.*?)(?:\n[A-Z][^\n:]*:|\Z)",
            text,
            re.IGNORECASE | re.DOTALL
        )

        search_text = (
            match.group(2)
            if match
            else text
        )

        # --------------------------------
        # Normalize common degree aliases
        # --------------------------------

        normalized_text = search_text

        for alias, canonical in sorted(
            self.aliases.items(),
            key=lambda item: len(item[0]),
            reverse=True
        ):

            normalized_text = re.sub(
                r"(?<![A-Za-z0-9])"
                + re.escape(alias)
                + r"(?![A-Za-z0-9])",
                canonical,
                normalized_text,
                flags=re.IGNORECASE
            )

        # --------------------------------
        # Extract degree types
        # --------------------------------

        for degree in self.degree_types:

            pattern = (
                r"(?<![A-Za-z0-9])"
                + re.escape(degree)
                + r"(?![A-Za-z0-9])"
            )

            if re.search(
                pattern,
                normalized_text,
                re.IGNORECASE
            ):

                education.append(degree)

        # --------------------------------
        # Extract fields of study
        # --------------------------------

        for field in self.fields_of_study:

            pattern = (
                r"(?<![A-Za-z0-9])"
                + re.escape(field)
                + r"(?![A-Za-z0-9])"
            )

            if re.search(
                pattern,
                normalized_text,
                re.IGNORECASE
            ):

                education.append(field)

        return sorted(
            set(education),
            key=len,
            reverse=True
        )