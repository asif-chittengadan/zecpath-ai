import json
import re


class ProjectExtractor:

    def __init__(self):

        with open(
            "data/skills.json",
            "r",
            encoding="utf-8"
        ) as file:

            self.skills = json.load(file)

        self.skills.sort(
            key=len,
            reverse=True
        )

    def extract(self, section_lines):

        projects = []

        current = None

        for line in section_lines:

            line = line.strip()

            if not line:

                continue

            # ----------------------------------
            # GitHub
            # ----------------------------------

            github = re.search(

                r'(https?://)?(www\.)?github\.com/[^\s]+',

                line,

                re.IGNORECASE

            )

            # ----------------------------------
            # Live Demo
            # ----------------------------------

            website = re.search(

                r'https?://[^\s]+',

                line

            )

            # ----------------------------------
            # New Project Title
            # ----------------------------------

            if current is None:

                current = {

                    "title": line,

                    "technologies": [],

                    "github": "",

                    "live_demo": "",

                    "description": []

                }

                continue

            # ----------------------------------
            # GitHub URL
            # ----------------------------------

            if github:

                current["github"] = github.group()

                continue

            # ----------------------------------
            # Live URL
            # ----------------------------------

            if website:

                url = website.group()

                if "github" not in url.lower():

                    current["live_demo"] = url

                continue

            # ----------------------------------
            # Technologies
            # ----------------------------------

            lower = line.lower()

            for skill in self.skills:

                pattern = r'(?<![A-Za-z0-9])' + re.escape(skill.lower()) + r'(?![A-Za-z0-9])'

                if re.search(pattern, lower):

                    if skill not in current["technologies"]:

                        current["technologies"].append(skill)

            # ----------------------------------
            # Description
            # ----------------------------------

            current["description"].append(line)

        if current:

            projects.append(current)

        return projects