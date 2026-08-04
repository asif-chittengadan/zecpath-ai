class JDNormalizer:
    """
    Normalizes Job Description headings
    into a standard format.
    """

    def __init__(self):

        self.heading_map = {

            "work experience": "Experience",
            "professional experience": "Experience",
            "experience": "Experience",

            "technical skills": "Skills",
            "core skills": "Skills",
            "required skills": "Skills",
            "Preferred Languages": "Skills",
            "Required Skills": "Skills",
            "Technical Skills": "Skills",
            "key skills": "Skills",
            "skills": "Skills",

            "qualification": "Education",
            "qualifications": "Education",
            "education": "Education",
            "education required": "Education",
            "Courses": "Education",
            "Education": "Education",
            "Who Can Apply": "Education",

            "job title": "Role",
            "role": "Role",
            "position": "Role",
            "Job Roles": "Role",

            "job location": "Location",
            "location": "Location",

            "employment type": "Employment Type"
        }

    def normalize(self, text: str):

        lines = []

        for line in text.split("\n"):

            key = line.strip().lower()

            if key in self.heading_map:
                lines.append(self.heading_map[key])
            else:
                lines.append(line)

        return "\n".join(lines)