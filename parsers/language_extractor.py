import json
import re


class LanguageExtractor:

    def __init__(self):

        with open(
            "data/languages.json",
            "r",
            encoding="utf-8"
        ) as file:

            self.languages = json.load(file)

        self.languages.sort(
            key=len,
            reverse=True
        )

    def extract(self, section_lines):

        detected = []

        text = "\n".join(section_lines)

        text = text.lower()

        for language in self.languages:

            pattern = r'(?<![A-Za-z0-9])' + re.escape(language.lower()) + r'(?![A-Za-z0-9])'

            if re.search(pattern, text):

                detected.append(language)

        return sorted(set(detected))