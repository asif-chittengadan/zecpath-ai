class InterviewDifficultyAdapter:
    """
    Determines the next follow-up difficulty level based on
    the candidate's response classification.

    Levels:
        1 = clarification / basic probe
        2 = deeper or example-based probe
        3 = scenario-based probe
    """

    LEVELS = {
        "incomplete": 1,
        "vague": 1,
        "complete": 2,
        "confident": 3
    }

    def __init__(self):
        self.current_level = 1

    def determine_level(self, classification):
        """
        Determine the appropriate difficulty level.
        """

        classification = self._normalize(classification)

        level = self.LEVELS.get(
            classification,
            1
        )

        self.current_level = level

        return level

    def should_increase_difficulty(self, current_level, classification):
        """
        Determine whether the next question should become harder.
        """

        classification = self._normalize(classification)

        recommended_level = self.LEVELS.get(
            classification,
            1
        )

        return recommended_level > current_level

    def get_strategy(self, level):
        """
        Return the questioning strategy for a difficulty level.
        """

        strategies = {
            1: "clarification",
            2: "deepening",
            3: "scenario_based"
        }

        return strategies.get(
            level,
            "clarification"
        )

    def reset(self):
        """
        Reset difficulty to the initial level.
        """
        self.current_level = 1

    @staticmethod
    def _normalize(value):
        return (
            str(value)
            .strip()
            .lower()
            .replace("-", "_")
            .replace(" ", "_")
        )