import re
import spacy


class ResumeExperienceExtractor:

    def __init__(self):

        self.nlp = spacy.load("en_core_web_sm")

        self.role_keywords = [

            "intern",
            "internship",
            "engineer",
            "developer",
            "analyst",
            "consultant",
            "manager",
            "designer",
            "associate",
            "executive",
            "lead",
            "tester",
            "administrator"

        ]

    def extract(self, section_lines):

        experiences = []

        current = {

            "company": "",

            "role": "",

            "start_date": "",

            "end_date": "",

            "duration": "",

            "description": []

        }

        text = "\n".join(section_lines)

        doc = self.nlp(text)

        # -------------------------
        # Company
        # -------------------------

        for ent in doc.ents:

            if ent.label_ == "ORG":

                current["company"] = ent.text

                break

        # -------------------------
        # Role
        # -------------------------

        for line in section_lines:

            lower = line.lower()

            if any(keyword in lower for keyword in self.role_keywords):

                current["role"] = line.strip()

                break

        # -------------------------
        # Date Range
        # -------------------------

        date_pattern = re.search(

            r'((Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4})\s*[-–]\s*((Present)|(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4})',

            text,

            re.IGNORECASE

        )

        if date_pattern:

            current["start_date"] = date_pattern.group(1)

            current["end_date"] = date_pattern.group(3)

        # -------------------------
        # Duration
        # -------------------------

        duration = re.search(

            r'(\d+\+?\s*(years?|months?))',

            text,

            re.IGNORECASE

        )

        if duration:

            current["duration"] = duration.group()

        # -------------------------
        # Responsibilities
        # -------------------------

        for line in section_lines:

            if line.startswith("-") or line.startswith("•"):

                current["description"].append(

                    line.lstrip("-• ").strip()

                )

        if (

            current["company"]

            or current["role"]

            or current["description"]

        ):

            experiences.append(current)

        return experiences