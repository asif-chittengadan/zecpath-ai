import re


class SalaryExpectationExtractor:
    """Extract expected salary information from candidate answers."""

    LPA_PATTERNS = [
        r"(?:₹|rs\.?|inr)?\s*(\d+(?:\.\d+)?)\s*(?:-|to)\s*(?:₹|rs\.?|inr)?\s*(\d+(?:\.\d+)?)\s*lpa\b",
        r"(?:₹|rs\.?|inr)?\s*(\d+(?:\.\d+)?)\s*lpa\b",
        r"(?:₹|rs\.?|inr)?\s*(\d+(?:\.\d+)?)\s*(?:-|to)\s*(\d+(?:\.\d+)?)\s*lakh(?:s)?\s*(?:per\s*annum|per\s*year|p\.?a\.?)?\b",
        r"(?:₹|rs\.?|inr)?\s*(\d+(?:\.\d+)?)\s*lakh(?:s)?\s*(?:per\s*annum|per\s*year|p\.?a\.?)?\b",
    ]

    MONTHLY_PATTERNS = [
        r"(?:₹|rs\.?|inr)\s*([\d,]+)\s*(?:per\s*month|monthly)\b",
        r"([\d,]+)\s*(?:rupees?)?\s*(?:per\s*month|monthly)\b",
    ]

    def extract(self, text):
        """
        Extract expected salary from a candidate answer.

        Returns:
            dict: Structured salary expectation information.
        """
        if not text or not isinstance(text, str):
            return self._empty_result("")

        normalized_text = " ".join(text.lower().split())

        lpa_result = self._extract_lpa(normalized_text, text.strip())

        if lpa_result:
            return lpa_result

        monthly_result = self._extract_monthly(normalized_text, text.strip())

        if monthly_result:
            return monthly_result

        return self._empty_result(text.strip())

    def _extract_lpa(self, normalized_text, original_text):
        for index, pattern in enumerate(self.LPA_PATTERNS):
            match = re.search(pattern, normalized_text)

            if not match:
                continue

            values = [float(value) for value in match.groups()]

            if len(values) == 2:
                minimum = min(values)
                maximum = max(values)
            else:
                minimum = values[0]
                maximum = values[0]

            return {
                "salary_mentioned": True,
                "currency": "INR",
                "period": "annual",
                "unit": "LPA",
                "minimum_lpa": minimum,
                "maximum_lpa": maximum,
                "text": self._matched_text(
                    normalized_text,
                    match,
                    original_text,
                ),
            }

        return None

    def _extract_monthly(self, normalized_text, original_text):
        for pattern in self.MONTHLY_PATTERNS:
            match = re.search(pattern, normalized_text)

            if not match:
                continue

            amount = float(match.group(1).replace(",", ""))

            return {
                "salary_mentioned": True,
                "currency": "INR",
                "period": "monthly",
                "unit": "INR",
                "minimum_lpa": round((amount * 12) / 100000, 2),
                "maximum_lpa": round((amount * 12) / 100000, 2),
                "monthly_amount": amount,
                "text": self._matched_text(
                    normalized_text,
                    match,
                    original_text,
                ),
            }

        return None

    @staticmethod
    def _matched_text(normalized_text, match, original_text):
        start, end = match.span()

        matched = normalized_text[start:end].strip()

        if matched:
            return matched

        return original_text

    @staticmethod
    def _empty_result(text):
        return {
            "salary_mentioned": False,
            "currency": None,
            "period": None,
            "unit": None,
            "minimum_lpa": None,
            "maximum_lpa": None,
            "text": text,
        }


if __name__ == "__main__":
    extractor = SalaryExpectationExtractor()

    examples = [
        "My expected salary is 8 LPA.",
        "I am expecting 10-12 LPA.",
        "I would expect around 15 lakh per annum.",
        "My expectation is 80000 rupees per month.",
        "I am flexible regarding compensation.",
    ]

    for answer in examples:
        print(answer)
        print(extractor.extract(answer))
        print()