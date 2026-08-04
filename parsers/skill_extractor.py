import json
import re


class SkillExtractor:

    def __init__(self):

        with open("data/skills.json", "r", encoding="utf-8") as f:
            self.skills = json.load(f)

        # Search longer skills first
        self.skills.sort(
            key=len,
            reverse=True
        )

    def extract(self, text):

        skills = []

        match = re.search(
            r"(Preferred Languages|Required Skills|Technical Skills)\s*:?(.*?)(?:\n[A-Z][^\n]*:|\Z)",
            text,
            re.IGNORECASE | re.DOTALL
        )

        search_text = match.group(2) if match else text

        for skill in self.skills:

            pattern = rf'(?<!\w){re.escape(skill)}(?!\w)'

            if re.search(pattern, search_text, re.IGNORECASE):

                skills.append(skill)

        return sorted(set(skills))