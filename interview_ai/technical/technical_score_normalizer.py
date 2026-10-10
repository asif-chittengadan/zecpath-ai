"""
ZECPATH AI - Technical Score Normalizer
Day 47: Normalizes technical scores across difficulty levels.
"""


class TechnicalScoreNormalizer:

    DIFFICULTY_FACTORS = {
        "basic": 1.00,
        "intermediate": 1.10,
        "advanced": 1.20,
    }

    @classmethod
    def normalize(cls, score, difficulty):
        if (
            not isinstance(score, (int, float))
            or isinstance(score, bool)
        ):
            raise TypeError("Score must be numeric.")

        if not 0 <= score <= 100:
            raise ValueError("Score must be between 0 and 100.")

        if difficulty not in cls.DIFFICULTY_FACTORS:
            raise ValueError(
                f"Unknown difficulty level: {difficulty}"
            )

        factor = cls.DIFFICULTY_FACTORS[difficulty]

        normalized_score = min(100.0, score * factor)

        return {
            "raw_score": round(float(score), 2),
            "difficulty": difficulty,
            "difficulty_factor": factor,
            "normalized_score": round(normalized_score, 2),
        }
