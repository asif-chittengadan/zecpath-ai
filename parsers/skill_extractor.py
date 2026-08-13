import json
import re


class SkillExtractor:

    def __init__(self):

        with open(
            "data/skills.json",
            "r",
            encoding="utf-8"
        ) as f:

            data = json.load(f)

        if isinstance(data, dict):

            self.skills = []

            for category_skills in data.values():

                if isinstance(category_skills, list):

                    self.skills.extend(
                        category_skills
                    )

        else:

            self.skills = data

        self.skills = sorted(
            set(self.skills),
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