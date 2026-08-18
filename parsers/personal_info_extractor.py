import re
import spacy


class PersonalInfoExtractor:

    def __init__(self):

        self.nlp = spacy.load("en_core_web_sm")

    def extract(self, header_lines):

        result = {

            "name": "",

            "email": "",

            "phone": "",

            "linkedin": "",

            "github": "",

            "portfolio": "",

            "location": ""

        }

        text = "\n".join(header_lines)

        # -------------------------
        # Email
        # -------------------------

        email = re.search(

            r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}',

            text

        )

        if email:

            result["email"] = email.group()

        # -------------------------
        # Phone
        # -------------------------

        phone = re.search(

            r'(\+?\d[\d\s\-]{8,15}\d)',

            text

        )

        if phone:

            result["phone"] = phone.group().strip()

        # -------------------------
        # LinkedIn
        # -------------------------

        linkedin = re.search(

            r'(https?://)?(www\.)?linkedin\.com/[^\s]+',

            text,

            re.IGNORECASE

        )

        if linkedin:

            result["linkedin"] = linkedin.group().rstrip(
                ".,;:)]}"
            )

        # -------------------------
        # GitHub
        # -------------------------

        github = re.search(

            r'(https?://)?(www\.)?github\.com/[^\s]+',

            text,

            re.IGNORECASE

        )

        if github:

            result["github"] = github.group().rstrip(
                ".,;:)]}"
            )

        # -------------------------
        # Portfolio
        # -------------------------

        urls = re.findall(

            r'https?://[^\s]+',

            text

        )

        for url in urls:

            if (

                "linkedin" not in url.lower()

                and

                "github" not in url.lower()

            ):

                result["portfolio"] = url.rstrip(
                    ".,;:)]}"
                )

                break

        # -------------------------
        # Name using spaCy
        # -------------------------

        first_lines = "\n".join(
            header_lines[:5]
        )

        doc = self.nlp(first_lines)

        for ent in doc.ents:

            if ent.label_ == "PERSON":

                result["name"] = ent.text.strip()

                break


        # -------------------------
        # Name fallback
        # -------------------------

        if not result["name"]:

            for line in header_lines[:5]:

                candidate = line.strip()

                if not candidate:
                    continue

                # Remove common separators
                candidate = re.sub(
                    r"^[•●▪◦\-–—]+",
                    "",
                    candidate
                ).strip()

                # Skip obvious contact/header lines
                if "@" in candidate:
                    continue

                if re.search(
                    r"\d{3,}",
                    candidate
                ):
                    continue

                if any(
                    keyword in candidate.lower()
                    for keyword in [
                        "resume",
                        "curriculum vitae",
                        "cv",
                        "linkedin",
                        "github",
                        "portfolio",
                        "email",
                        "phone",
                        "mobile"
                    ]
                ):
                    continue

                words = candidate.split()

                if 2 <= len(words) <= 4:

                    if all(
                        re.match(
                            r"^[A-Za-z][A-Za-z.'-]*$",
                            word
                        )
                        for word in words
                    ):

                        result["name"] = candidate.title()

                        break
        # -------------------------
        # Location
        # -------------------------

        for ent in doc.ents:

            if ent.label_ in [

                "GPE",

                "LOC"

            ]:

                result["location"] = ent.text

                break

        return result