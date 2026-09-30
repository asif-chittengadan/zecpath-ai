class HRScoringInconsistencyAnalyzer:
    """
    Analyzes differences between AI and manual HR interview
    evaluations and produces improvement recommendations.
    """

    def analyze(self, comparison_result):
        inconsistent_parameters = comparison_result.get(
            "inconsistent_parameters",
            []
        )

        average_difference = comparison_result.get(
            "average_difference",
            0
        )

        inconsistency_count = comparison_result.get(
            "inconsistency_count",
            0
        )

        recommendations = []

        for parameter in inconsistent_parameters:
            recommendations.append(
                self._recommendation_for(parameter)
            )

        if average_difference == 0:
            accuracy_level = "exact_match"
        elif average_difference <= 5:
            accuracy_level = "high_alignment"
        elif average_difference <= 10:
            accuracy_level = "moderate_alignment"
        else:
            accuracy_level = "low_alignment"

        return {
            "accuracy_level": accuracy_level,
            "average_difference": average_difference,
            "inconsistency_count": inconsistency_count,
            "inconsistent_parameters": (
                inconsistent_parameters
            ),
            "recommendations": recommendations,
        }

    @staticmethod
    def _recommendation_for(parameter):
        recommendations = {
            "answer_relevance": (
                "Review relevance scoring criteria and "
                "improve alignment between AI scoring and "
                "manual assessment."
            ),
            "communication": (
                "Review communication indicators and "
                "ensure AI scoring reflects the same "
                "criteria used by manual evaluators."
            ),
            "confidence": (
                "Review confidence-related signals and "
                "calibration against manual evaluations."
            ),
            "consistency": (
                "Review consistency detection and "
                "compare AI evidence with manual judgments."
            ),
        }

        return recommendations.get(
            parameter,
            "Review the scoring criteria for this parameter."
        )