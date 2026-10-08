"""
ZECPATH AI - Technical Interview Difficulty Adapter

Day 46:
Determines technical interview difficulty based on
candidate experience and answer progression.
"""


from interview_ai.technical.technical_interview import (
    TechnicalInterviewConfig,
)


class TechnicalDifficultyAdapter:
    """
    Determines and adjusts technical interview difficulty.
    """

    @classmethod
    def get_initial_difficulty(cls, experience_years):
        experience = (
            TechnicalInterviewConfig.get_experience_level(
                experience_years
            )
        )

        return experience["label"]

    @classmethod
    def increase_difficulty(cls, current_difficulty):
        return (
            TechnicalInterviewConfig
            .get_next_difficulty(current_difficulty)
        )

    @classmethod
    def decrease_difficulty(cls, current_difficulty):
        levels = (
            TechnicalInterviewConfig
            .get_difficulty_levels()
        )

        if current_difficulty not in levels:
            raise ValueError(
                f"Unknown difficulty level: "
                f"{current_difficulty}"
            )

        current_index = levels.index(
            current_difficulty
        )

        if current_index == 0:
            return levels[0]

        return levels[current_index - 1]

    @classmethod
    def adapt_to_answer(
        cls,
        current_difficulty,
        answer_quality,
    ):
        if answer_quality not in {
            "weak",
            "acceptable",
            "strong",
        }:
            raise ValueError(
                "Answer quality must be "
                "'weak', 'acceptable', or 'strong'."
            )

        if answer_quality == "strong":
            return cls.increase_difficulty(
                current_difficulty
            )

        if answer_quality == "weak":
            return cls.decrease_difficulty(
                current_difficulty
            )

        return current_difficulty