class ProblemSolvingClarityAnalyzer:
    """
    Analyzes how clearly a candidate explains a problem-solving approach.
    """

    INDICATORS = {
        "problem_identification": [
            "identify the problem",
            "understand the problem",
            "identify the issue",
            "understand the issue",
            "find the problem",
            "find the issue",
            "define the problem",
            "root cause"
        ],
        "approach_present": [
            "first",
            "then",
            "next",
            "step",
            "approach",
            "analyze",
            "check",
            "investigate",
            "debug",
            "test"
        ],
        "alternatives_present": [
            "alternative",
            "alternatives",
            "option",
            "options",
            "another approach",
            "different approach",
            "compare",
            "consider"
        ],
        "solution_present": [
            "solution",
            "solve",
            "fix",
            "resolve",
            "implement",
            "conclusion",
            "finally",
            "result"
        ]
    }

    def analyze(self, response):
        """
        Analyze a candidate response.

        Returns:
            dict: Problem-solving clarity analysis.
        """

        if not isinstance(response, str):
            response = ""

        text = response.lower().strip()

        indicators = {}

        for name, keywords in self.INDICATORS.items():
            indicators[name] = any(
                keyword in text
                for keyword in keywords
            )

        detected_count = sum(
            indicators.values()
        )

        clarity_score = detected_count * 25

        if clarity_score >= 75:
            clarity_level = "high"
        elif clarity_score >= 50:
            clarity_level = "moderate"
        elif clarity_score >= 25:
            clarity_level = "low"
        else:
            clarity_level = "very_low"

        return {
            **indicators,
            "detected_indicators": detected_count,
            "clarity_score": clarity_score,
            "clarity_level": clarity_level
        }