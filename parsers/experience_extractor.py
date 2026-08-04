import re


class ExperienceExtractor:

    def extract(self, text):

        text = text.lower()

        result = {
            "minimum": None,
            "maximum": None,
            "text": ""
        }

        # ----------------------------------
        # Detect Fresher / Graduate Roles
        # ----------------------------------

        fresher_keywords = [
            "fresher",
            "freshers",
            "final year",
            "recent graduate",
            "recent graduates",
            "2024 batch",
            "2025 batch",
            "2026 batch",
            "2027 batch",
            "passout",
            "passouts",
            "graduate trainee",
            "apprentice"
        ]

        for keyword in fresher_keywords:

            if keyword in text:

                result["minimum"] = 0
                result["maximum"] = 0
                result["text"] = "Freshers"

                return result

        # ----------------------------------
        # Ignore academic year references
        # ----------------------------------

        academic_keywords = [

            "curriculum",

            "semester",

            "student",

            "students",

            "academic",

            "course",

            "degree",

            "education"

        ]

        for word in academic_keywords:

            if word in text:

                return result

        # ----------------------------------
        # Experience Range
        # ----------------------------------

        match = re.search(

            r'(\d+)\s*-\s*(\d+)\s*years?',

            text

        )

        if match:

            result["minimum"] = int(match.group(1))

            result["maximum"] = int(match.group(2))

            result["text"] = match.group(0)

            return result

        # ----------------------------------
        # Single Experience
        # ----------------------------------

        match = re.search(

            r'(\d+)\+?\s*years?',

            text

        )

        if match:

            result["minimum"] = int(match.group(1))

            result["text"] = match.group(0)

            return result

        return result