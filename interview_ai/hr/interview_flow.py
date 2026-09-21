from interview_ai.hr.interview_state import InterviewState


class HRInterviewFlow:
    """
    Controls the phases and question progression
    of the V2 AI HR interview.
    """

    PHASES = [
        "introduction",
        "core_hr",
        "role_based_evaluation",
        "closing"
    ]

    def __init__(self, interview_state):
        if not isinstance(interview_state, InterviewState):
            raise TypeError(
                "interview_state must be an InterviewState instance"
            )

        self.state = interview_state

    def start(self):
        """
        Start the interview in the introduction phase.
        """
        self.state.change_phase("introduction")
        return self.state.current_phase

    def move_to_next_phase(self):
        """
        Move the interview to the next phase.
        """

        current_phase = self.state.current_phase

        if current_phase not in self.PHASES:
            raise ValueError(
                f"Unknown interview phase: {current_phase}"
            )

        current_index = self.PHASES.index(current_phase)

        if current_index == len(self.PHASES) - 1:
            self.state.complete_interview()
            return self.state.current_phase

        next_phase = self.PHASES[current_index + 1]

        self.state.change_phase(next_phase)

        return next_phase

    def set_question(self, question_id, question):
        """
        Set the current question for the active phase.
        """
        self.state.set_question(
            question_id,
            question
        )

    def capture_response(
        self,
        response,
        follow_up_eligible=False
    ):
        """
        Capture the candidate's response.
        """
        self.state.capture_response(
            response,
            follow_up_eligible
        )

    def is_completed(self):
        """
        Check whether the interview has completed.
        """
        return self.state.interview_completed

    def get_current_phase(self):
        """
        Return the current interview phase.
        """
        return self.state.current_phase

    def get_state(self):
        """
        Return the complete interview state.
        """
        return self.state.get_state()