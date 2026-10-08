"""
ZECPATH AI - Technical Interview State

Day 46:
Maintains the current state of a technical interview session.
"""


class TechnicalInterviewState:
    """
    Stores candidate and interview progression information.
    """

    def __init__(
        self,
        candidate_id,
        role,
        experience_years,
    ):
        self.candidate_id = candidate_id
        self.role = role
        self.experience_years = experience_years

        self.current_stage = "introduction"
        self.current_difficulty = None
        self.current_question = None

        self.questions_answered = 0
        self.questions_asked = []

        self.interview_completed = False

    def set_question(
        self,
        question,
        difficulty,
    ):
        self.current_question = question
        self.current_difficulty = difficulty

        self.questions_asked.append(
            {
                "question": question,
                "difficulty": difficulty,
                "stage": self.current_stage,
            }
        )

    def record_answer(self):
        self.questions_answered += 1

    def move_to_stage(self, stage):
        self.current_stage = stage
        self.current_question = None
        self.current_difficulty = None

    def complete_interview(self):
        self.current_stage = "completed"
        self.current_question = None
        self.current_difficulty = None
        self.interview_completed = True

    def get_progress(self):
        return {
            "candidate_id": self.candidate_id,
            "role": self.role,
            "experience_years": self.experience_years,
            "current_stage": self.current_stage,
            "current_difficulty": self.current_difficulty,
            "questions_answered": self.questions_answered,
            "questions_asked": len(self.questions_asked),
            "interview_completed": self.interview_completed,
        }