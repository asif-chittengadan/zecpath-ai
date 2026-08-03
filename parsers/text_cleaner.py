import re


class TextCleaner:

    def clean(self, text: str) -> str:
        """
        Cleans extracted resume text while preserving
        useful formatting for ATS processing.
        """

        if not text:
            return ""

        # Normalize line endings
        text = text.replace("\r\n", "\n").replace("\r", "\n")

        # Replace tabs with spaces
        text = text.replace("\t", " ")

        # Normalize bullet symbols
        bullets = ["•", "▪", "●", "◦", "○", "■", "►", "▶", "*"]
        for bullet in bullets:
            text = text.replace(bullet, "-")

        # Remove unwanted characters but keep useful punctuation
        text = re.sub(r"[^\w\s@.,:/()\-+&]", "", text)

        # Remove multiple spaces
        text = re.sub(r"[ ]{2,}", " ", text)

        # Remove spaces before new lines
        text = re.sub(r" +\n", "\n", text)

        # Remove more than two consecutive blank lines
        text = re.sub(r"\n{3,}", "\n\n", text)

        # Strip spaces from every line
        lines = [line.strip() for line in text.split("\n")]

        # Remove empty duplicate lines
        cleaned_lines = []
        previous = ""

        for line in lines:
            if line == previous == "":
                continue
            cleaned_lines.append(line)
            previous = line

        return "\n".join(cleaned_lines).strip()