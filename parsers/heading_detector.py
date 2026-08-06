import re
from rapidfuzz import process


class HeadingDetector:

    def __init__(self):

        self.section_map = {

            "Summary": [
                "summary",
                "professional summary",
                "profile",
                "career objective",
                "objective",
                "about me",
                "professional profile"
            ],

            "Skills": [
                "skills",
                "technical skills",
                "core skills",
                "technical expertise",
                "competencies",
                "skill set",
                "programming skills"
            ],

            "Experience": [
                "experience",
                "professional experience",
                "work experience",
                "employment history",
                "career history",
                "internship",
                "internships"
            ],

            "Education": [
                "education",
                "academic qualification",
                "academic qualifications",
                "qualification",
                "qualifications",
                "academics"
            ],

            "Projects": [
                "projects",
                "academic projects",
                "personal projects",
                "major projects",
                "minor projects"
            ],

            "Certifications": [
                "certifications",
                "certificates",
                "licenses",
                "professional certifications"
            ],

            "Achievements": [
                "achievements",
                "awards",
                "honours",
                "honors"
            ],

            "Languages": [
                "languages",
                "language proficiency"
            ],

            "Interests": [
                "interests",
                "hobbies"
            ],

            "Personal Information": [
                "personal information",
                "contact",
                "contact information"
            ]
        }

    def detect(self, line):

        line = line.strip()

        if not line:
            return None

        clean = re.sub(r'[:•\-]', '', line).strip().lower()

        best_section = None
        best_score = 0

        for section, headings in self.section_map.items():

            result = process.extractOne(clean, headings)

            if result:

                _, score, _ = result

                if score > best_score:

                    best_score = score
                    best_section = section

        if best_score >= 90:

            return best_section

        return None