class HRScoreNormalizer:
    """
    Normalizes HR interview component scores
    across different interview lengths.
    """

    PARAMETERS = [
        "answer_relevance",
        "communication",
        "confidence",
        "consistency"
    ]

    def normalize(self, question_scores):
        """
        Calculate average component scores across
        all answered interview questions.
        """

        if not question_scores:
            return {
                "answered_questions": 0,
                "normalized_scores": {
                    parameter: 0.0
                    for parameter in self.PARAMETERS
                },
                "completion_ratio": 0.0
            }

        totals = {
            parameter: 0.0
            for parameter in self.PARAMETERS
        }

        answered_questions = 0

        for question in question_scores:
            if not isinstance(question, dict):
                continue

            answered_questions += 1

            for parameter in self.PARAMETERS:
                try:
                    score = float(
                        question.get(parameter, 0)
                    )
                except (TypeError, ValueError):
                    score = 0.0

                score = max(
                    0.0,
                    min(100.0, score)
                )

                totals[parameter] += score

        if answered_questions == 0:
            return {
                "answered_questions": 0,
                "normalized_scores": {
                    parameter: 0.0
                    for parameter in self.PARAMETERS
                },
                "completion_ratio": 0.0
            }

        normalized_scores = {
            parameter: round(
                totals[parameter] / answered_questions,
                2
            )
            for parameter in self.PARAMETERS
        }

        return {
            "answered_questions": answered_questions,
            "normalized_scores": normalized_scores,
            "completion_ratio": 1.0
        }