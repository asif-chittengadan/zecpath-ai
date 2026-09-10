import re


class AvailabilityExtractor:
    """Extract candidate availability and notice-period information."""

    IMMEDIATE_PATTERNS = [
        r"\bavailable immediately\b",
        r"\bcan join immediately\b",
        r"\bjoin immediately\b",
        r"\bimmediate joining\b",
        r"\bimmediate joiner\b",
        r"\bavailable to start immediately\b",
        r"\bcan start immediately\b",
    ]

    UNAVAILABLE_PATTERNS = [
        r"\bnot available\b",
        r"\bnot currently available\b",
        r"\bcan't join\b",
        r"\bcannot join\b",
        r"\bunable to join\b",
    ]

    NOTICE_PERIOD_PATTERNS = [
        r"\b(\d+)\s*[-]?\s*(?:day|days)\s*(?:notice period|notice)\b",
        r"\bnotice period\s*(?:is|of)?\s*(\d+)\s*[-]?\s*(?:day|days)?\b",
        r"\bserving\s+(?:a\s+)?(\d+)\s*[-]?\s*(?:day|days)?\s*notice\b",
        r"\bafter\s+(\d+)\s*[-]?\s*(?:day|days)\b",
        r"\bin\s+(\d+)\s*[-]?\s*(?:day|days)\b",
    ]

    FUTURE_PATTERNS = [
        r"\bnext month\b",
        r"\bnext week\b",
        r"\bfrom next month\b",
        r"\bfrom next week\b",
        r"\bstarting next month\b",
        r"\bstarting next week\b",
    ]

    def extract(self, text):
        """
        Extract availability information from a candidate answer.

        Returns:
            dict: Structured availability information.
        """
        if not text or not isinstance(text, str):
            return {
                "available": None,
                "availability_type": "unknown",
                "notice_period_days": None,
                "text": "",
            }

        normalized_text = " ".join(text.lower().split())

        if self._matches(normalized_text, self.UNAVAILABLE_PATTERNS):
            return {
                "available": False,
                "availability_type": "unavailable",
                "notice_period_days": None,
                "text": text.strip(),
            }

        if self._matches(normalized_text, self.IMMEDIATE_PATTERNS):
            return {
                "available": True,
                "availability_type": "immediate",
                "notice_period_days": 0,
                "text": text.strip(),
            }

        notice_days = self._extract_notice_period(normalized_text)

        if notice_days is not None:
            return {
                "available": True,
                "availability_type": "notice_period",
                "notice_period_days": notice_days,
                "text": text.strip(),
            }

        if self._matches(normalized_text, self.FUTURE_PATTERNS):
            return {
                "available": True,
                "availability_type": "future",
                "notice_period_days": None,
                "text": text.strip(),
            }

        return {
            "available": None,
            "availability_type": "unknown",
            "notice_period_days": None,
            "text": text.strip(),
        }

    @staticmethod
    def _matches(text, patterns):
        return any(re.search(pattern, text) for pattern in patterns)

    @staticmethod
    def _extract_notice_period(text):
        for pattern in AvailabilityExtractor.NOTICE_PERIOD_PATTERNS:
            match = re.search(pattern, text)

            if match:
                return int(match.group(1))

        return None


if __name__ == "__main__":
    extractor = AvailabilityExtractor()

    examples = [
        "I can join immediately.",
        "I am currently serving a 30-day notice period.",
        "I can start after 15 days.",
        "I can join next month.",
        "I am not available right now.",
    ]

    for answer in examples:
        print(answer)
        print(extractor.extract(answer))
        print()