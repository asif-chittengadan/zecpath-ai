from screening_ai.communication import CommunicationAnalyzer
from screening_ai.sentiment_analyzer import SentimentAnalyzer


class BehavioralIndicatorAnalyzer:
    """Combine communication and sentiment signals into behavioral indicators."""

    def __init__(
        self,
        communication_analyzer=None,
        sentiment_analyzer=None
    ):
        self.communication_analyzer = (
            communication_analyzer
            or CommunicationAnalyzer()
        )

        self.sentiment_analyzer = (
            sentiment_analyzer
            or SentimentAnalyzer()
        )

    def analyze(
        self,
        response,
        duration_seconds=None
    ):
        communication = self.communication_analyzer.analyze(
            response=response,
            duration_seconds=duration_seconds
        )

        sentiment = self.sentiment_analyzer.analyze(
            response=response
        )

        communication_strength = (
            communication[
                "communication_strength"
            ]["score"]
        )

        if not communication["response"]:
            behavioral_strength = 0.0
        else:
            behavioral_strength = self._calculate_behavioral_strength(
                communication_strength,
                sentiment
            )

        return {
            "communication": communication,
            "sentiment": sentiment,
            "behavioral_indicators": {
                "hesitation_detected": communication[
                    "hesitation"
                ]["detected"],
                "uncertainty_detected": communication[
                    "uncertainty"
                ]["detected"],
                "contradiction_detected": communication[
                    "contradictions"
                ]["detected"],
                "response_length": communication[
                    "response_length"
                ]["category"],
                "response_pace_wpm": communication[
                    "response_pace_wpm"
                ],
                "sentiment": sentiment[
                    "sentiment"
                ]
            },
            "communication_strength": {
                "score": behavioral_strength,
                "scale": "0-100"
            }
        }

    @staticmethod
    def _calculate_behavioral_strength(
        communication_strength,
        sentiment
    ):
        sentiment_score = sentiment["score"]

        # Sentiment is treated as a secondary signal.
        # It must not dominate the communication score.
        sentiment_adjustment = sentiment_score * 0.10

        strength = (
            communication_strength * 0.90
            + (50 + sentiment_adjustment) * 0.10
        )

        return round(
            max(0.0, min(100.0, strength * 10)),
            2
        )