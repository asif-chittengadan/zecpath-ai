"""
ZECPATH AI - Technical Interview Flow

Day 46:
Controls technical interview stage transitions.
"""


from interview_ai.technical.technical_interview import (
    TechnicalInterviewConfig,
)


class TechnicalInterviewFlow:
    """
    Manages the progression of a technical interview.
    """

    def __init__(self):
        self.current_stage = (
            TechnicalInterviewConfig.get_initial_stage()
        )

    def get_current_stage(self):
        return self.current_stage

    def move_to_next_stage(self):
        self.current_stage = (
            TechnicalInterviewConfig.get_next_stage(
                self.current_stage
            )
        )

        return self.current_stage

    def is_completed(self):
        return self.current_stage == "completed"

    def reset(self):
        self.current_stage = (
            TechnicalInterviewConfig.get_initial_stage()
        )