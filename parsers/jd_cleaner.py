import re


class JDCleaner:
    """
    Cleans raw Job Description text.
    """

    def clean(self, text: str) -> str:

        if not text:
            return ""

        # Normalize line endings
        text = text.replace("\r\n", "\n").replace("\r", "\n")

        # Replace tabs with spaces
        text = text.replace("\t", " ")

        # Remove multiple spaces
        text = re.sub(r"[ ]{2,}", " ", text)

        # Remove multiple blank lines
        text = re.sub(r"\n{3,}", "\n\n", text)

        # Remove unwanted characters
        text = re.sub(r"[^\w\s@.,:/()\-+&]", "", text)

        return text.strip()