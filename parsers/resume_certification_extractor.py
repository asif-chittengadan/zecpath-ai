import json
import re


class CertificationExtractor:

    def __init__(self):

        with open(
            "data/certifications.json",
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(file)

        self.certifications = sorted(
            set(data.get("certifications", [])),
            key=len,
            reverse=True
        )

        self.course_platforms = sorted(
            set(data.get("course_platforms", [])),
            key=len,
            reverse=True
        )

        self.categories = data.get(
            "categories",
            {}
        )

    def extract(self, section_lines):

        certifications = []

        for line in section_lines:

            line = line.strip()

            if not line:
                continue

            line = re.sub(
                r"^[•●▪◦*-]\s*",
                "",
                line
            ).strip()

            if not line:
                continue

            # -----------------------------
            # Find certification
            # -----------------------------

            certification = self.__find_certification(line)

            if certification:
                name = certification
            else:
                name = line

            current = {
                "name": self.normalize_name(name),
                "issuer": "",
                "platform": "",
                "date": "",
                "credential_id": "",
                "categories": []
            }

            # -----------------------------
            # Credential ID
            # -----------------------------

            credential = re.search(
                r"(Credential ID|Credential No|Certificate ID|Certification ID)"
                r"\s*[:\-]?\s*([A-Za-z0-9\-]+)",
                line,
                re.IGNORECASE
            )

            if credential:

                current["credential_id"] = (
                    credential.group(2).strip()
                )

            # -----------------------------
            # Date
            # -----------------------------

            date = re.search(
                r"\b(?:19|20)\d{2}\b",
                line
            )

            if date:

                current["date"] = date.group()

            # -----------------------------
            # Platform
            # -----------------------------

            platform = self.__find_platform(line)

            if platform:

                current["platform"] = platform

            # -----------------------------
            # Issuer
            # -----------------------------

            remaining = line

            if certification:
                remaining = re.sub(
                    re.escape(certification),
                    "",
                    remaining,
                    count=1,
                    flags=re.IGNORECASE
                )

            if credential:
                remaining = remaining.replace(
                    credential.group(0),
                    ""
                )

            if date:
                remaining = remaining.replace(
                    date.group(0),
                    ""
                )

            if platform:
                remaining = re.sub(
                    re.escape(platform),
                    "",
                    remaining,
                    flags=re.IGNORECASE
                )

            remaining = re.sub(
                r"\s+",
                " ",
                remaining
            ).strip(" |-,:;")

            if remaining:
                current["issuer"] = remaining

            # -----------------------------
            # Categories
            # -----------------------------

            current["categories"] = self.categorize(
                current["name"]
            )

            certifications.append(current)

        return self.__remove_duplicates(
            certifications
        )
    def __find_certification(self, line):

        for certification in self.certifications:

            pattern = (
                r"(?<![A-Za-z0-9])"
                + re.escape(certification)
                + r"(?![A-Za-z0-9])"
            )

            if re.search(
                pattern,
                line,
                re.IGNORECASE
            ):

                return certification

        return None

    def __find_platform(self, line):

        for platform in self.course_platforms:

            pattern = (
                r"(?<![A-Za-z0-9])"
                + re.escape(platform)
                + r"(?![A-Za-z0-9])"
            )

            if re.search(
                pattern,
                line,
                re.IGNORECASE
            ):

                return platform

        return None

    def __looks_like_certification(self, line):

        keywords = [
            "certified",
            "certificate",
            "certification",
            "professional certificate",
            "professional certification"
        ]

        lower_line = line.lower()

        return any(
            keyword in lower_line
            for keyword in keywords
        )

    def __remove_duplicates(self, certifications):

        unique = {}

        for certification in certifications:

            key = (
                certification["name"].lower(),
                certification["issuer"].lower(),
                certification["platform"].lower()
            )

            if key not in unique:

                unique[key] = certification

        return list(unique.values())

    def normalize_name(self, name):

        if not name:
            return ""

        name = name.strip()

        name = re.sub(
            r"\s+",
            " ",
            name
        )

        name = re.sub(
            r"\s*([,:;|])\s*",
            r"\1 ",
            name
        ).strip()

        for certification in self.certifications:

            if name.lower() == certification.lower():

                return certification

        return name

    def categorize(self, certification):

        if not certification:
            return []

        categories = []

        certification_lower = certification.lower()

        for category, keywords in self.categories.items():

            for keyword in keywords:

                if keyword.lower() in certification_lower:

                    categories.append(category)

                    break

        return categories