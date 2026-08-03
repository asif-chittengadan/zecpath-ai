import os


class OutputWriter:

    def save(self, filename, text):

        os.makedirs("data/cleaned", exist_ok=True)

        path = os.path.join("data/cleaned", filename)

        with open(path, "w", encoding="utf-8") as file:

            file.write(text)

        return path