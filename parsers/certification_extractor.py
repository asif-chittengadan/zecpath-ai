import re

class CertificationExtractor:

    def normalize_name(self, name):
        """
        Normalize a certification name for consistent comparison.

        - Converts text to lowercase
        - Removes leading/trailing whitespace
        - Collapses repeated whitespace
        """
        if name is None:
            return ""

        normalized = str(name).strip().lower()

        normalized = re.sub(
            r"\s+",
            " ",
            normalized
        )

        return normalized

    def extract(self, section_lines):

        certifications = []

        current = None

        for line in section_lines:

            line = line.strip()

            if not line:

                continue

            # -----------------------------
            # New Certification
            # -----------------------------

            if current is None:

                current = {

                    "name": line,

                    "issuer": "",

                    "date": "",

                    "credential_id": ""

                }

                continue

            # -----------------------------
            # Credential ID
            # -----------------------------

            credential = re.search(

                r'(Credential ID|Credential No|Certificate ID)\s*[:\-]?\s*(.+)',

                line,

                re.IGNORECASE

            )

            if credential:

                current["credential_id"] = credential.group(2).strip()

                continue

            # -----------------------------
            # Year
            # -----------------------------

            year = re.search(

                r'(19|20)\d{2}',

                line

            )

            if year:

                current["date"] = year.group()

                continue

            # -----------------------------
            # Issuer
            # -----------------------------

            if current["issuer"] == "":

                current["issuer"] = line

                continue

        if current:

            certifications.append(current)

        return certifications