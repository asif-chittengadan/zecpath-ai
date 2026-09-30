class HRManualEvaluationComparator:
    """
    Compares AI-generated HR interview scores with
    manually evaluated scores.
    """

    PARAMETERS = (
        "answer_relevance",
        "communication",
        "confidence",
        "consistency",
    )

    def compare(
        self,
        ai_scores,
        manual_scores,
        tolerance=5
    ):
        """
        Compare AI and manual component scores.

        tolerance:
            Maximum acceptable absolute difference.
        """

        comparison = {}
        total_difference = 0.0
        inconsistent_parameters = []

        for parameter in self.PARAMETERS:
            ai_score = float(
                ai_scores.get(parameter, 0)
            )

            manual_score = float(
                manual_scores.get(parameter, 0)
            )

            difference = round(
                abs(ai_score - manual_score),
                2
            )

            within_tolerance = (
                difference <= tolerance
            )

            comparison[parameter] = {
                "ai_score": ai_score,
                "manual_score": manual_score,
                "difference": difference,
                "within_tolerance": within_tolerance,
            }

            total_difference += difference

            if not within_tolerance:
                inconsistent_parameters.append(
                    parameter
                )

        parameter_count = len(self.PARAMETERS)

        average_difference = round(
            total_difference / parameter_count,
            2
        )

        return {
            "comparison": comparison,
            "average_difference": average_difference,
            "inconsistent_parameters":
                inconsistent_parameters,
            "inconsistency_count":
                len(inconsistent_parameters),
            "all_within_tolerance":
                len(inconsistent_parameters) == 0,
            "tolerance": tolerance,
        }