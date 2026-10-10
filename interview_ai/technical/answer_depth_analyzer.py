"""
ZECPATH AI - Answer Depth Analyzer
Day 47: Classifies technical answers as shallow or deep.
"""


class AnswerDepthAnalyzer:

    SHALLOW_INDICATORS = [
        "i don't know",
        "not sure",
        "just because",
        "it is simple",
    ]

    DEEP_INDICATORS = [
        "because",
        "for example",
        "trade-off",
        "tradeoff",
        "therefore",
        "in practice",
        "the reason",
        "implementation",
        "performance",
    ]

    @classmethod
    def analyze(cls, answer):
        if not isinstance(answer, str):
            raise TypeError("Answer must be a string.")

        text = answer.strip().lower()
        words = text.split()

        if not words:
            return {
                "classification": "shallow",
                "word_count": 0,
                "reason": "The answer is empty.",
            }

        shallow_matches = [
            phrase
            for phrase in cls.SHALLOW_INDICATORS
            if phrase in text
        ]

        deep_matches = [
            phrase
            for phrase in cls.DEEP_INDICATORS
            if phrase in text
        ]

        if len(words) < 8 or (
            shallow_matches and not deep_matches
        ):
            classification = "shallow"
            reason = "The answer has limited explanation or detail."
        elif len(words) >= 20 and len(deep_matches) >= 2:
            classification = "deep"
            reason = "The answer includes extended explanation and reasoning indicators."
        else:
            classification = "moderate"
            reason = "The answer contains some explanation but does not meet the deep-answer criteria."

        return {
            "classification": classification,
            "word_count": len(words),
            "shallow_indicators": shallow_matches,
            "deep_indicators": deep_matches,
            "reason": reason,
        }
