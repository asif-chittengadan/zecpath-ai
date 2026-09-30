class HRPerformanceSummary:
    """
    Builds a structured summary of overall HR interview performance.
    """

    def generate(
        self,
        overall_score,
        component_scores=None
    ):
        component_scores = (
            component_scores
            if isinstance(component_scores, dict)
            else {}
        )

        score = self._normalize_score(
            overall_score
        )

        return {
            "overall_score": score,
            "performance_level": self._get_level(
                score
            ),
            "component_scores": component_scores,
            "component_count": len(
                component_scores
            )
        }

    def _normalize_score(self, score):
        try:
            score = float(score)
        except (TypeError, ValueError):
            return None

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

    def _get_level(self, score):
        if score is None:
            return "not_available"

        if score >= 75:
            return "high"

        if score >= 50:
            return "moderate"

        if score >= 25:
            return "low"

        return "very_low"