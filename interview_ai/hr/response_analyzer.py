class HRResponseAnalyzer:
    """
    Classifies HR interview responses for dynamic follow-up logic.

    Possible classifications:
        - incomplete
        - vague
        - complete
        - confident
    """

    VAGUE_PHRASES = {
        "i don't know",
        "i do not know",
        "not sure",
        "maybe",
        "something like that",
        "and things like that",
        "etc",
        "etcetera",
        "i guess",
        "probably"
    }

    CONFIDENT_PHRASES = {
        "i am confident",
        "i'm confident",
        "definitely",
        "certainly",
        "i successfully",
        "i successfully implemented",
        "i led",
        "i implemented",
        "i was responsible for"
    }

    def __init__(self, minimum_words=8):
        self.minimum_words = minimum_words

    def analyze(self, response):
        """
        Classify a candidate response.

        Returns:
            {
                "classification": str,
                "word_count": int,
                "reason": str
            }
        """

        normalized = self._normalize(response)

        if not normalized:
            return {
                "classification": "incomplete",
                "word_count": 0,
                "reason": "No response was provided."
            }

        word_count = len(normalized.split())

        if word_count < 3:
            return {
                "classification": "incomplete",
                "word_count": word_count,
                "reason": "Response is too short."
            }

        if self._contains_vague_phrase(normalized):
            return {
                "classification": "vague",
                "word_count": word_count,
                "reason": "Response contains vague or uncertain language."
            }

        if word_count < self.minimum_words:
            return {
                "classification": "incomplete",
                "word_count": word_count,
                "reason": "Response does not contain enough detail."
            }

        if self._contains_confident_phrase(normalized):
            return {
                "classification": "confident",
                "word_count": word_count,
                "reason": "Response contains sufficient detail and confident language."
            }

        return {
            "classification": "complete",
            "word_count": word_count,
            "reason": "Response contains sufficient detail."
        }

    def _contains_vague_phrase(self, response):
        return any(
            phrase in response
            for phrase in self.VAGUE_PHRASES
        )

    def _contains_confident_phrase(self, response):
        return any(
            phrase in response
            for phrase in self.CONFIDENT_PHRASES
        )

    @staticmethod
    def _normalize(value):
        return " ".join(
            str(value).strip().lower().split()
        )