from rapidfuzz import process


class SectionNormalizer:

    def __init__(self):

        self.standard_sections = {

            "Skills": [

                "skills",
                "technical skills",
                "core skills",
                "professional skills",
                "programming skills",
                "technical expertise",
                "skill set",
                "competencies"

            ],

            "Experience": [

                "experience",
                "work experience",
                "professional experience",
                "employment history",
                "career history",
                "internships",
                "internship"

            ],

            "Education": [

                "education",
                "academics",
                "academic qualifications",
                "educational qualification",
                "qualification"

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

            ]

        }

    def normalize(self, heading):

        heading = heading.strip().lower()

        best_section = None

        best_score = 0

        for standard, variations in self.standard_sections.items():

            match = process.extractOne(
                heading,
                variations
            )

            if match:

                _, score, _ = match

                if score > best_score:

                    best_score = score

                    best_section = standard

        if best_score >= 85:

            return best_section

        return heading.title()