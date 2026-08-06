import json
import re


class SkillExtractor:

    def __init__(self):

        with open(
            "data/skills.json",
            "r",
            encoding="utf-8"
        ) as file:

            self.skills = json.load(file)

        # Longer skills first
        self.skills.sort(
            key=len,
            reverse=True
        )

    def extract(self, section_lines):

        detected = []

        text = "\n".join(section_lines)

        text = text.lower()

        for skill in self.skills:

            pattern = r'(?<![A-Za-z0-9])' + \
                      re.escape(skill.lower()) + \
                      r'(?![A-Za-z0-9])'

            if re.search(pattern, text):

                detected.append(skill)

        return sorted(set(detected))