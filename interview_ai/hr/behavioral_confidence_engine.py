class BehavioralConfidenceEngine:
    """
    Combines Day 36 behavioral signals into a transparent
    0-100 behavioral confidence score.

    This is a rule-based behavioral signal.
    It is not a psychological or medical assessment.
    """

    BASE_SCORE = 100

    HESITATION_PENALTY = 5
    CONTRADICTION_PENALTY = 10

    MODERATE_STRESS_PENALTY = 7
    HIGH_STRESS_PENALTY = 15

    NEGATIVE_SENTIMENT_PENALTY = 5
    POSITIVE_SENTIMENT_BONUS = 5

    def calculate(
        self,
        confidence_result=None,
        sentiment_result=None,
        contradiction_result=None,
        stress_result=None
    ):
        if confidence_result is None:
            confidence_result = {}

        if sentiment_result is None:
            sentiment_result = {}

        if contradiction_result is None:
            contradiction_result = {}

        if stress_result is None:
            stress_result = {}

        score = self.BASE_SCORE
        adjustments = []

        hesitation_count = self._safe_int(
            confidence_result.get(
                "hesitation_count",
                0
            )
        )

        if hesitation_count > 0:
            penalty = (
                hesitation_count
                * self.HESITATION_PENALTY
            )

            score -= penalty

            adjustments.append({
                "type": "hesitation",
                "value": -penalty
            })

        contradiction_count = self._safe_int(
            contradiction_result.get(
                "count",
                0
            )
        )

        if contradiction_count > 0:
            penalty = (
                contradiction_count
                * self.CONTRADICTION_PENALTY
            )

            score -= penalty

            adjustments.append({
                "type": "contradiction",
                "value": -penalty
            })

        stress_level = stress_result.get(
            "stress_level",
            "low"
        )

        if stress_level == "moderate":
            score -= self.MODERATE_STRESS_PENALTY

            adjustments.append({
                "type": "moderate_stress",
                "value": -self.MODERATE_STRESS_PENALTY
            })

        elif stress_level == "high":
            score -= self.HIGH_STRESS_PENALTY

            adjustments.append({
                "type": "high_stress",
                "value": -self.HIGH_STRESS_PENALTY
            })

        sentiment = sentiment_result.get(
            "sentiment",
            "neutral"
        )

        if sentiment == "negative":
            score -= self.NEGATIVE_SENTIMENT_PENALTY

            adjustments.append({
                "type": "negative_sentiment",
                "value": -self.NEGATIVE_SENTIMENT_PENALTY
            })

        elif sentiment == "positive":
            score += self.POSITIVE_SENTIMENT_BONUS

            adjustments.append({
                "type": "positive_sentiment",
                "value": self.POSITIVE_SENTIMENT_BONUS
            })

        score = self._bound_score(
            score
        )

        return {
            "behavioral_confidence_score": score,
            "base_score": self.BASE_SCORE,
            "adjustments": adjustments,
            "interpretation": self._interpret(
                score
            )
        }

    def _interpret(self, score):
        if score >= 80:
            return "high_signal"

        if score >= 60:
            return "moderate_signal"

        return "low_signal"

    @staticmethod
    def _safe_int(value):
        try:
            return int(value)
        except (TypeError, ValueError):
            return 0

    @staticmethod
    def _bound_score(score):
        return round(
            max(
                0,
                min(
                    100,
                    score
                )
            ),
            2
        )