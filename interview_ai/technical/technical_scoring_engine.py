"""
ZECPATH AI - Technical Scoring Engine
Day 47: Technical answer scoring and weighted evaluation.
"""


class TechnicalScoringEngine:

    DEFAULT_WEIGHTS = {
        "accuracy": 0.40,
        "depth": 0.25,
        "logical_reasoning": 0.20,
        "real_world_applicability": 0.15,
    }

    PARAMETER_NAMES = tuple(DEFAULT_WEIGHTS.keys())

    MAX_SCORE = 100

    @classmethod
    def score_answer(
        cls,
        accuracy,
        depth,
        logical_reasoning,
        real_world_applicability,
        question_type=None,
    ):
        scores = {
            "accuracy": accuracy,
            "depth": depth,
            "logical_reasoning": logical_reasoning,
            "real_world_applicability": real_world_applicability,
        }

        for name, score in scores.items():
            if (
                not isinstance(score, (int, float))
                or isinstance(score, bool)
            ):
                raise TypeError(f"{name} must be numeric.")

            if not 0 <= score <= cls.MAX_SCORE:
                raise ValueError(
                    f"{name} must be between 0 and 100."
                )

        # Use question-specific weights when a question type is supplied.
        if question_type is None:
            weights = dict(cls.DEFAULT_WEIGHTS)
        else:
            from interview_ai.technical.technical_scoring_rubric import (
                TechnicalScoringRubric,
            )

            weights = TechnicalScoringRubric.get_rubric(
                question_type
            )

        if set(weights) != set(scores):
            raise ValueError(
                "The scoring rubric must contain all four parameters."
            )

        if abs(sum(weights.values()) - 1.0) > 1e-9:
            raise ValueError(
                "Scoring weights must add up to 1.0."
            )

        breakdown = {}

        for name, score in scores.items():
            weight = weights[name]

            breakdown[name] = {
                "score": round(float(score), 2),
                "weight": weight,
                "weighted_score": round(score * weight, 2),
            }

        final_score = round(
            sum(item["weighted_score"] for item in breakdown.values()),
            2,
        )

        return {
            "question_type": question_type or "default",
            "final_score": final_score,
            "maximum_score": cls.MAX_SCORE,
            "breakdown": breakdown,
        }
