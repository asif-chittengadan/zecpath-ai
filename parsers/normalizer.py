class Normalizer:

    def normalize(self, text):

        replacements = {

            "educational qualification": "Education",
            "academic details": "Education",
            "professional experience": "Experience",
            "technical skills": "Skills"

        }

        normalized = text

        for old, new in replacements.items():

            normalized = normalized.replace(old, new)

            normalized = normalized.replace(old.title(), new)

        return normalized