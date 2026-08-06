import json
import os


class SectionBuilder:

    def save(self, sections, output_path):

        os.makedirs(
            os.path.dirname(output_path),
            exist_ok=True
        )

        with open(
            output_path,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(

                sections,

                file,

                indent=4,

                ensure_ascii=False

            )

    def load(self, input_path):

        with open(

            input_path,

            "r",

            encoding="utf-8"

        ) as file:

            return json.load(file)