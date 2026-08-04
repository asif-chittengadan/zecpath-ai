import json
import re

class RoleExtractor:

    def __init__(self):

        with open(
            "data/roles.json",
            "r",
            encoding="utf-8"
        ) as file:

            self.roles = json.load(file)

        self.roles.sort(
            key=len,
            reverse=True
        )

    def extract(self, text):

        # -----------------------------
        # Search only Job Roles section
        # -----------------------------

        match = re.search(

            r'Job Roles?\s*:?(.*?)(?:Work Location|Number of Positions|Compensation|Preferred Languages|Selection Procedure|\Z)',

            text,

            re.IGNORECASE | re.DOTALL

        )

        if match:

            search_text = match.group(1)

        else:

            search_text = text

        matches = []

        lower_text = search_text.lower()

        for role in self.roles:

            count = lower_text.count(role.lower())

            if count > 0:

                matches.append((count, role))

        if matches:

            matches.sort(reverse=True)

            return matches[0][1]

        return ""