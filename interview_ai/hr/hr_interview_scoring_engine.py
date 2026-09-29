from interview_ai.hr.hr_scoring_config import (
    HRScoringConfig
)


class HRInterviewScoringEngine:
    """
    Calculates a weighted HR interview score from:

    - Answer relevance
    - Communication
    - Confidence
    - Consistency
    """

    def __init__(self, config_path):
        self.config = HRScoringConfig(
            config_path
        )

    def calculate_score(
        self,
        answer_relevance,
        communication,
        confidence,
        consistency
    ):
        scores = {
            "answer_relevance": self._normalize_score(
                answer_relevance
            ),
            "communication": self._normalize_score(
                communication
            ),
            "confidence": self._normalize_score(
                confidence
            ),
            "consistency": self._normalize_score(
                consistency
            )
        }

        weighted_scores = {}

        for parameter, score in scores.items():
            weight = self.config.get_weight(
                parameter
            )

            weighted_scores[parameter] = round(
                score * weight,
                2
            )

        final_score = round(
            sum(weighted_scores.values()),
            2
        )

        return {
            "final_score": final_score,
            "component_scores": scores,
            "weighted_scores": weighted_scores
        }

    def get_score_breakdown(
        self,
        answer_relevance,
        communication,
        confidence,
        consistency
    ):
        """
        Return an explainable breakdown of the HR score.
        """

        result = self.calculate_score(
            answer_relevance=answer_relevance,
            communication=communication,
            confidence=confidence,
            consistency=consistency
        )

        breakdown = []

        for parameter in [
            "answer_relevance",
            "communication",
            "confidence",
            "consistency"
        ]:
            score = result[
                "component_scores"
            ][parameter]

            weight = self.config.get_weight(
                parameter
            )

            contribution = result[
                "weighted_scores"
            ][parameter]

            breakdown.append({
                "parameter": parameter,
                "score": score,
                "weight": weight,
                "weight_percentage": round(
                    weight * 100,
                    2
                ),
                "contribution": contribution
            })

        return {
            "final_score": result["final_score"],
            "breakdown": breakdown
        }

    def _normalize_score(self, score):
        try:
            score = float(score)
        except (TypeError, ValueError):
            score = 0.0

        return round(
            max(
                0.0,
                min(
                    100.0,
                    score
                )
            ),
            2
        )