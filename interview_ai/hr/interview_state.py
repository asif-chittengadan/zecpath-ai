from dataclasses import dataclass, field
from typing import List, Dict, Optional


@dataclass
class InterviewState:
    """
    Stores the current state of an AI HR interview.
    """

    session_id: str
    candidate_id: str

    role: str
    candidate_type: str
    role_type: str

    current_phase: str = "introduction"

    current_question_id: Optional[str] = None
    current_question: Optional[str] = None

    response: Optional[str] = None

    response_history: List[Dict] = field(default_factory=list)

    follow_up_eligible: bool = False

    questions_answered: int = 0

    interview_completed: bool = False

    def set_question(self, question_id, question):
        """
        Set the question currently being asked.
        """
        self.current_question_id = question_id
        self.current_question = question
        self.response = None
        self.follow_up_eligible = False

    def capture_response(self, response, follow_up_eligible=False):
        """
        Store the candidate response for the current question.
        """

        self.response = response
        self.follow_up_eligible = follow_up_eligible

        self.response_history.append({
            "question_id": self.current_question_id,
            "question": self.current_question,
            "response": response,
            "follow_up_eligible": follow_up_eligible
        })

        self.questions_answered += 1

    def change_phase(self, phase):
        """
        Change the current interview phase.
        """
        self.current_phase = phase

    def complete_interview(self):
        """
        Mark the interview as completed.
        """
        self.interview_completed = True
        self.current_phase = "closing"

    def get_state(self):
        """
        Return the current interview state as a dictionary.
        """
        return {
            "session_id": self.session_id,
            "candidate_id": self.candidate_id,
            "role": self.role,
            "candidate_type": self.candidate_type,
            "role_type": self.role_type,
            "current_phase": self.current_phase,
            "current_question_id": self.current_question_id,
            "current_question": self.current_question,
            "response": self.response,
            "response_history": self.response_history,
            "follow_up_eligible": self.follow_up_eligible,
            "questions_answered": self.questions_answered,
            "interview_completed": self.interview_completed
        }