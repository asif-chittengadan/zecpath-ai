import re


class SectionExtractor:

    def __init__(self):

        self.section_map = {

            # Role
            "job role": "roles",
            "job roles": "roles",
            "role": "roles",
            "position": "roles",
            "positions": "roles",

            # Skills
            "required skills": "skills",
            "technical skills": "skills",
            "preferred skills": "skills",
            "preferred languages": "skills",
            "core knowledge": "skills",
            "skills": "skills",

            # Education
            "education": "education",
            "courses": "education",
            "eligibility": "education",
            "who can apply": "education",
            "academic requirement": "education",
            "academic requirements": "education",

            # Experience
            "experience": "experience",
            "work experience": "experience",

            # Requirements
            "requirements": "requirements",
            "qualifications": "requirements",

            # Other
            "job summary": "summary",
            "about": "summary",
            "job details": "job_details",
            "responsibilities": "responsibilities",
            "key responsibilities": "responsibilities",
            "selection procedure": "selection_process",
            "benefits": "benefits",
            "compensation": "compensation"
        }

    def extract(self, text):

        sections = {}

        current_section = "general"

        sections[current_section] = []

        for line in text.splitlines():

            line = line.strip()

            if not line:
                continue

            found = False

            for heading, section_name in self.section_map.items():

                pattern = rf"^\s*{re.escape(heading)}\s*:?"

                if re.search(pattern, line, re.IGNORECASE):

                    current_section = section_name

                    if current_section not in sections:
                        sections[current_section] = []

                    # Keep text after the heading
                    remaining = re.sub(
                        pattern,
                        "",
                        line,
                        flags=re.IGNORECASE
                    ).strip()

                    if remaining:
                        sections[current_section].append(remaining)

                    found = True
                    break

            if not found:

                sections.setdefault(current_section, []).append(line)

        # Convert lists to text
        for key in sections:

            sections[key] = "\n".join(sections[key])

        return sections