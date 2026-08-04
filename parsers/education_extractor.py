import json
import re


class EducationExtractor:

    def __init__(self):

        with open("data/education.json", "r", encoding="utf-8") as f:
            self.education = json.load(f)

    def extract(self, text):

        education = []

        match = re.search(
            r"(Courses|Education).*?:?(.*?)(?:Academic Requirement|Job Details|\Z)",
            text,
            re.IGNORECASE | re.DOTALL
        )

        search_text = match.group(2) if match else text

        for item in self.education:

            pattern = r"\b" + re.escape(item) + r"\b"

            if re.search(pattern, search_text, re.IGNORECASE):
                education.append(item)

        return sorted(set(education))