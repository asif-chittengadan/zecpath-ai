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

        self.degree_types = sorted(
            set(data["degree_types"]),
            key=len,
            reverse=True
        )

        self.fields_of_study = sorted(
            set(data["fields_of_study"]),
            key=len,
            reverse=True
        )

    def extract_degree(self, text):

        matches = []

        for degree in self.degree_types:

            pattern = (
                r"(?<![A-Za-z0-9])"
                + re.escape(degree)
                + r"(?![A-Za-z0-9])"
            )

            if re.search(
                pattern,
                text,
                re.IGNORECASE
            ):
                matches.append(degree)

        matches.sort(
            key=len,
            reverse=True
        )

        if not matches:
            return []

        return [matches[0]]
    
    def extract_field_of_study(self, text):

        matches = []

        for field in self.fields_of_study:

            pattern = (
                r"(?<![A-Za-z0-9])"
                + re.escape(field)
                + r"(?![A-Za-z0-9])"
            )

            if re.search(
                pattern,
                text,
                re.IGNORECASE
            ):
                matches.append(field)

        matches.sort(
            key=len,
            reverse=True
        )

        if not matches:
            return []

        return [matches[0]]
    
    def extract_institution(self, text):

        lines = [
            line.strip()
            for line in text.splitlines()
            if line.strip()
        ]

        institutions = []

        for index, line in enumerate(lines):

            # Degree | Institution | Location
            if self.extract_degree(line):

                parts = [
                    part.strip()
                    for part in re.split(
                        r"\s*\|\s*",
                        line
                    )
                    if part.strip()
                ]

                if len(parts) >= 2:

                    institutions.append(parts[1])
                    continue

                # Institution on previous line
                if index > 0:

                    previous_line = lines[index - 1]

                    if (
                        not self.extract_degree(previous_line)
                        and
                        not self.extract_field_of_study(previous_line)
                        and
                        not re.search(
                            r"\b(CGPA|GPA|Percentage|Graduated|"
                            r"Graduation|Grade)\b",
                            previous_line,
                            re.IGNORECASE
                        )
                        and
                        not re.search(
                            r"\b(?:19|20)\d{2}\b",
                            previous_line
                        )
                    ):

                        institutions.append(
                            previous_line
                        )

        return list(dict.fromkeys(institutions))
        
    def extract_graduation_year(self, text):

        match = re.search(
            r"\b(?:graduated|graduation|completed|passed out|passout)"
            r"\s*[:\-]?\s*"
            r"(?:[A-Za-z]+\s+)?"
            r"(19|20)\d{2}\b",
            text,
            re.IGNORECASE
        )

        if match:
            return int(match.group(0)[-4:])

        return None