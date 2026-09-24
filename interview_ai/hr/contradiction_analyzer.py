import re

class ContradictionAnalyzer:
    """
    Detects basic contradictions between a current interview
    response and previously known candidate information.

    This is a deterministic rule-based analyzer.
    """

    def analyze(self, response, previous_data=None):
        """
        Compare the current response with previous candidate data.

        previous_data may contain:
            experience_years
            availability_days
            skills
        """

        if response is None:
            response = ""

        response = str(response).strip()

        if previous_data is None:
            previous_data = {}

        contradictions = []

        current_experience = self._extract_experience(
            response
        )

        previous_experience = self._safe_number(
            previous_data.get(
                "experience_years"
            )
        )

        if (
            current_experience is not None
            and previous_experience is not None
            and current_experience != previous_experience
        ):
            contradictions.append(
                "experience_conflict"
            )

        current_availability = (
            self._extract_availability(response)
        )

        previous_availability = self._safe_integer(
            previous_data.get(
                "availability_days"
            )
        )

        if (
            current_availability is not None
            and previous_availability is not None
            and current_availability != previous_availability
        ):
            contradictions.append(
                "availability_conflict"
            )

        current_skills = self._extract_skills(
            response
        )

        previous_skills = previous_data.get(
            "skills",
            []
        )

        skill_conflict = self._detect_skill_conflict(
            current_skills,
            previous_skills
        )

        if skill_conflict:
            contradictions.append(
                "skill_conflict"
            )

        return {
            "contradiction_detected": bool(
                contradictions
            ),
            "contradictions": contradictions,
            "count": len(contradictions)
        }

    def _safe_number(self, value):
        if value is None:
            return None

        try:
            return float(value)
        except (TypeError, ValueError):
            return None


    def _safe_integer(self, value):
        if value is None:
            return None

        try:
            return int(value)
        except (TypeError, ValueError):
            return None

    def _extract_experience(self, text):
        normalized = str(text).lower()

        number_words = {
            "zero": 0,
            "one": 1,
            "two": 2,
            "three": 3,
            "four": 4,
            "five": 5,
            "six": 6,
            "seven": 7,
            "eight": 8,
            "nine": 9,
            "ten": 10
        }

        numeric_match = re.search(
            r"\b(\d+(?:\.\d+)?)\s+years?\b",
            normalized
        )

        if numeric_match:
            return float(
                numeric_match.group(1)
            )

        for word, value in number_words.items():
            pattern = rf"\b{word}\s+years?\b"

            if re.search(pattern, normalized):
                return float(value)

        return None
    def _extract_availability(self, text):
        normalized = str(text).lower()

        numeric_match = re.search(
            r"\b(\d+)\s+days?\b",
            normalized
        )

        if numeric_match:
            return int(
                numeric_match.group(1)
            )

        return None
    def _extract_skills(self, text):
        known_skills = {
            "python",
            "java",
            "javascript",
            "sql",
            "django",
            "flask",
            "react",
            "tensorflow",
            "pytorch",
            "machine learning"
        }

        normalized = text.lower()

        return [
            skill
            for skill in known_skills
            if skill in normalized
        ]

    def _detect_skill_conflict(
        self,
        current_skills,
        previous_skills
    ):
        if not previous_skills:
            return False

        return False