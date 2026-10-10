"""
ZECPATH AI - Technical Scoring Rubric
Day 47: Scoring criteria for different question types.
"""


class TechnicalScoringRubric:

    RUBRICS = {
        "conceptual": {
            "accuracy": 0.45,
            "depth": 0.30,
            "logical_reasoning": 0.15,
            "real_world_applicability": 0.10,
        },
        "experience_based": {
            "accuracy": 0.25,
            "depth": 0.25,
            "logical_reasoning": 0.20,
            "real_world_applicability": 0.30,
        },
        "scenario_based": {
            "accuracy": 0.25,
            "depth": 0.20,
            "logical_reasoning": 0.30,
            "real_world_applicability": 0.25,
        },
        "introduction": {
            "accuracy": 0.30,
            "depth": 0.20,
            "logical_reasoning": 0.20,
            "real_world_applicability": 0.30,
        },
    }

    @classmethod
    def get_rubric(cls, question_type):
        if question_type not in cls.RUBRICS:
            raise ValueError(
                f"Unknown question type: {question_type}"
            )

        return dict(cls.RUBRICS[question_type])

    @classmethod
    def calculate_score(cls, question_type, scores):
        rubric = cls.get_rubric(question_type)

        if set(scores) != set(rubric):
            raise ValueError(
                "Scores must contain all four scoring parameters."
            )

        for name, score in scores.items():
            if (
                not isinstance(score, (int, float))
                or isinstance(score, bool)
                or not 0 <= score <= 100
            ):
                raise ValueError(
                    f"{name} must be a number between 0 and 100."
                )

        return round(
            sum(
                scores[name] * weight
                for name, weight in rubric.items()
            ),
            2,
        )
