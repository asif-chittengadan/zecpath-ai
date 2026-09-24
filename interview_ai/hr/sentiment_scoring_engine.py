class SentimentScoringEngine:
    """
    Deterministic sentiment scoring for interview responses.

    Returns:
        positive / negative / neutral sentiment
        and a 0-100 sentiment score.
    """

    POSITIVE_WORDS = {
        "confident",
        "comfortable",
        "excited",
        "motivated",
        "enjoy",
        "enjoyed",
        "love",
        "interested",
        "successful",
        "achieved",
        "improved",
        "learned",
        "strong",
        "good",
        "great",
        "positive",
        "effective",
        "happy",
        "proud",
        "excellent"
    }

    NEGATIVE_WORDS = {
        "worried",
        "afraid",
        "nervous",
        "confused",
        "difficult",
        "failure",
        "failed",
        "bad",
        "poor",
        "hate",
        "dislike",
        "frustrated",
        "stress",
        "stressed",
        "uncertain",
        "problem",
        "problems",
        "weak",
        "negative",
        "unable"
    }

    def analyze(self, response):
        """
        Analyze sentiment from an interview response.
        """

        if response is None:
            response = ""

        normalized = self._normalize(response)

        if not normalized:
            return {
                "sentiment": "neutral",
                "score": 50.0,
                "positive_words": [],
                "negative_words": [],
                "positive_count": 0,
                "negative_count": 0
            }

        words = normalized.split()

        positive_words = self._find_matches(
            words,
            self.POSITIVE_WORDS
        )

        negative_words = self._find_matches(
            words,
            self.NEGATIVE_WORDS
        )

        positive_count = len(positive_words)
        negative_count = len(negative_words)

        score = self._calculate_score(
            positive_count,
            negative_count
        )

        sentiment = self._classify(
            positive_count,
            negative_count
        )

        return {
            "sentiment": sentiment,
            "score": score,
            "positive_words": positive_words,
            "negative_words": negative_words,
            "positive_count": positive_count,
            "negative_count": negative_count
        }

    def _calculate_score(
        self,
        positive_count,
        negative_count
    ):
        total = (
            positive_count
            + negative_count
        )

        if total == 0:
            return 50.0

        positive_ratio = (
            positive_count / total
        )

        return round(
            positive_ratio * 100,
            2
        )

    def _classify(
        self,
        positive_count,
        negative_count
    ):
        if positive_count > negative_count:
            return "positive"

        if negative_count > positive_count:
            return "negative"

        return "neutral"

    @staticmethod
    def _find_matches(words, vocabulary):
        detected = []

        for word in words:
            if word in vocabulary and word not in detected:
                detected.append(word)

        return sorted(detected)

    @staticmethod
    def _normalize(value):
        value = str(value).strip().lower()

        punctuation = ",.!?;:()[]{}\""

        for character in punctuation:
            value = value.replace(
                character,
                " "
            )

        return " ".join(
            value.split()
        )