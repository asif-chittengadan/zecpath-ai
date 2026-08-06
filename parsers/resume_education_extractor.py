import re
import spacy


class EducationExtractor:

    def __init__(self):

        self.nlp = spacy.load("en_core_web_sm")

        self.degree_patterns = [

            r"\bb\.?tech\b",
            r"\bb\.?e\b",
            r"\bm\.?tech\b",
            r"\bm\.?e\b",
            r"\bbachelor(?:'s)?\b",
            r"\bmaster(?:'s)?\b",
            r"\bbsc\b",
            r"\bmsc\b",
            r"\bbca\b",
            r"\bmca\b",
            r"\bph\.?d\b",
            r"\bdiploma\b"

        ]

    def extract(self, section_lines):

        education = []

        current = {

            "degree": "",

            "institution": "",

            "cgpa": "",

            "graduation_year": ""

        }

        text = "\n".join(section_lines)

        lower = text.lower()

        # -------------------------
        # Degree
        # -------------------------

        for pattern in self.degree_patterns:

            match = re.search(pattern, lower)

            if match:

                current["degree"] = match.group()

                break

        # -------------------------
        # CGPA
        # -------------------------

        cgpa = re.search(

            r'(cgpa|gpa)\s*[:\-]?\s*([0-9]+\.[0-9]+)',

            text,

            re.IGNORECASE

        )

        if cgpa:

            current["cgpa"] = cgpa.group(2)

        # -------------------------
        # Graduation Year
        # -------------------------

        year = re.search(

            r'(20\d{2}|19\d{2})',

            text

        )

        if year:

            current["graduation_year"] = year.group()

        # -------------------------
        # Institution
        # -------------------------

        doc = self.nlp(text)

        for ent in doc.ents:

            if ent.label_ == "ORG":

                current["institution"] = ent.text

                break

        if any(current.values()):

            education.append(current)

        return education