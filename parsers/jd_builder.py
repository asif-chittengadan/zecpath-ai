import json


class JDBuilder:

    def build(
        self,
        role,
        skills,
        experience,
        education
    ):

        return {
            "role": role,
            "skills": skills,
            "experience": experience,
            "education": education
        }

    def save(self, jd, output_file):

        with open(
            output_file,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                jd,
                file,
                indent=4,
                ensure_ascii=False
            )