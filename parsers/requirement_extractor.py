import re


class RequirementExtractor:

    def extract(self, text):

        result = {

            "responsibilities": [],

            "preferred_skills": [],

            "location": "",

            "salary": "",

            "employment_type": "",

            "selection_process": []
        }

        lines = text.splitlines()

        # -------------------------
        # Work Location
        # -------------------------

        location_patterns = [

            r'work location\s*[:\-]\s*(.*)',

            r'location\s*[:\-]\s*(.*)'
        ]

        for line in lines:

            for pattern in location_patterns:

                match = re.search(
                    pattern,
                    line,
                    re.IGNORECASE
                )

                if match:

                    result["location"] = match.group(1).strip()

        # -------------------------
        # Salary
        # -------------------------

        salary_patterns = [

            r'compensation\s*[:\-]\s*(.*)',

            r'salary\s*[:\-]\s*(.*)',

            r'package\s*[:\-]\s*(.*)'
        ]

        for line in lines:

            for pattern in salary_patterns:

                match = re.search(
                    pattern,
                    line,
                    re.IGNORECASE
                )

                if match:

                    result["salary"] = match.group(1).strip()

        # -------------------------
        # Employment Type
        # -------------------------

        types = [

            "Full Time",

            "Part Time",

            "Internship",

            "Apprentice",

            "Contract",

            "Remote",

            "Hybrid"

        ]

        lower_text = text.lower()

        for t in types:

            if t.lower() in lower_text:

                result["employment_type"] = t

                break

        # -------------------------
        # Selection Process
        # -------------------------

        selection_keywords = [

            "Aptitude Test",

            "Technical Test",

            "Machine Test",

            "Coding Test",

            "Group Discussion",

            "Interview",

            "Face-to-Face Interview",

            "HR Interview"

        ]

        for keyword in selection_keywords:

            if keyword.lower() in lower_text:

                result["selection_process"].append(keyword)

        # -------------------------
        # Responsibilities
        # -------------------------

        capture = False

        for line in lines:

            line = line.strip()

            if not line:

                continue

            if (

                "responsibilities" in line.lower()

                or

                "key responsibilities" in line.lower()

            ):

                capture = True

                continue

            if capture:

                if any(

                    heading in line.lower()

                    for heading in [

                        "qualification",

                        "education",

                        "eligibility",

                        "skills",

                        "experience"

                    ]

                ):

                    break

                result["responsibilities"].append(line)

        return result