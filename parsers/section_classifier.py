import re
from rapidfuzz import fuzz


class SectionClassifier:

    def __init__(self):

        self.section_headers = {

            "Skills": [
                "skills",
                "technical skills",
                "core competencies",
                "technical expertise",
                "key skills",
                "technologies"
            ],

            "Experience": [
                "experience",
                "work experience",
                "professional experience",
                "employment",
                "employment history",
                "career history",
                "internship",
                "internships"
            ],

            "Education": [
                "education",
                "academic background",
                "academic qualification",
                "qualifications"
            ],

            "Projects": [
                "projects",
                "academic projects",
                "personal projects",
                "major projects"
            ],

            "Certifications": [
                "certifications",
                "certificates",
                "licenses"
            ],

            "Summary": [
                "summary",
                "professional summary",
                "profile",
                "objective",
                "career objective",
                "about me"
            ]

        }

    def classify(self, text):

        sections = {

            "Summary": [],
            "Skills": [],
            "Experience": [],
            "Education": [],
            "Projects": [],
            "Certifications": [],
            "Others": []

        }

        current = "Others"

        lines = text.splitlines()

        for line in lines:

            line = line.strip()

            if not line:
                continue

            heading = self.__detect_heading(line)

            if heading:

                current = heading

                continue

            sections[current].append(line)

        return sections

    def __detect_heading(self, line):

        clean = re.sub(r'[^a-zA-Z ]', '', line).lower().strip()

        for section, headings in self.section_headers.items():

            for heading in headings:

                if fuzz.ratio(clean, heading) >= 90:

                    return section

        return None