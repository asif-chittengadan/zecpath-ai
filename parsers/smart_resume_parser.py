import re

from parsers.resume_section_parser import ResumeSectionParser


class SmartResumeParser:

    def __init__(self):

        self.parser = ResumeSectionParser()

    def parse(self, resume_path):

        sections = self.parser.parse(resume_path)

        sections = self.__clean_sections(sections)

        sections = self.__merge_duplicate_lines(sections)

        sections = self.__remove_noise(sections)

        return sections

    def __clean_sections(self, sections):

        cleaned = {}

        for section, values in sections.items():

            # -----------------------------
            # String
            # -----------------------------
            if isinstance(values, str):

                cleaned[section] = re.sub(
                    r"\s+",
                    " ",
                    values
                ).strip()

            # -----------------------------
            # Dictionary
            # -----------------------------
            elif isinstance(values, dict):

                cleaned[section] = values

            # -----------------------------
            # List
            # -----------------------------
            elif isinstance(values, list):

                new_values = []

                for value in values:

                    if isinstance(value, str):

                        value = re.sub(
                            r"\s+",
                            " ",
                            value
                        ).strip()

                        if value:

                            new_values.append(value)

                    else:

                        new_values.append(value)

                cleaned[section] = new_values

            else:

                cleaned[section] = values

        return cleaned

    def __merge_duplicate_lines(self, sections):

        for section, values in sections.items():

            if not isinstance(values, list):

                continue

            seen = set()

            merged = []

            for value in values:

                if not isinstance(value, str):

                    merged.append(value)

                    continue

                key = value.lower()

                if key not in seen:

                    merged.append(value)

                    seen.add(key)

            sections[section] = merged

        return sections

    def __remove_noise(self, sections):

        noise = {

            "page",

            "resume",

            "curriculum vitae",

            "cv"

        }

        for section, values in sections.items():

            if not isinstance(values, list):

                continue

            cleaned = []

            for value in values:

                if not isinstance(value, str):

                    cleaned.append(value)

                    continue

                if value.lower() not in noise:

                    cleaned.append(value)

            sections[section] = cleaned

        return sections