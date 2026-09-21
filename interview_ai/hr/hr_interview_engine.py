from interview_ai.hr.interview_state import InterviewState
from interview_ai.hr.interview_flow import HRInterviewFlow
from interview_ai.hr.question_generator import HRQuestionGenerator
from interview_ai.hr.follow_up_engine import HRFollowUpEngine


class HRInterviewEngine:
    """
    Integrated ZECPATH AI V2 HR Interview Engine.

    Connects:
    - Question Generator
    - Interview State
    - Interview Flow
    - Follow-Up Engine
    """

    PHASE_QUESTION_CATEGORIES = {
        "introduction": [
            "self_introduction"
        ],
        "core_hr": [
            "career_journey",
            "strengths_weaknesses",
            "teamwork_culture_fit",
            "career_goals",
            "availability_commitment"
        ]
    }

    def __init__(
        self,
        session_id,
        candidate_id,
        role,
        candidate_type,
        role_type,
        question_bank_path="data/hr_question_bank.json"
    ):
        self.state = InterviewState(
            session_id=session_id,
            candidate_id=candidate_id,
            role=role,
            candidate_type=candidate_type,
            role_type=role_type
        )

        self.flow = HRInterviewFlow(self.state)

        self.question_generator = HRQuestionGenerator(
            question_bank_path
        )

        self.follow_up_engine = HRFollowUpEngine()

        self.category_index = 0
        self.question_index = 0
        self.follow_up_active = False
        self.current_category = None

    def start(self):
        """
        Start the HR interview and prepare the first question.
        """
        self.flow.start()
        return self._prepare_next_question()

    def submit_response(self, response):
        """
        Process the candidate's response.

        Returns information about whether a follow-up is needed
        or the interview should continue.
        """

        if self.state.current_question is None:
            raise RuntimeError(
                "No active question. Start the interview first."
            )

        result = self.follow_up_engine.evaluate(
            self.state.current_question,
            response,
            self.current_category
        )

        self.flow.capture_response(
            response,
            follow_up_eligible=result["eligible"]
        )

        if result["eligible"] and not self.follow_up_active:
            self.follow_up_active = True

            follow_up_question = (
                self.follow_up_engine.generate_follow_up(
                    self.state.current_question,
                    self.current_category
                )
            )

            self.state.set_question(
                f"{self.state.current_question_id}-FOLLOWUP",
                follow_up_question
            )

            return {
                "action": "follow_up",
                "question": follow_up_question,
                "phase": self.state.current_phase,
                "follow_up_eligible": True
            }

        self.follow_up_active = False

        next_question = self._prepare_next_question()

        if next_question is None:
            return {
                "action": "completed",
                "question": None,
                "phase": self.state.current_phase,
                "follow_up_eligible": False
            }

        return {
            "action": "next_question",
            "question": next_question,
            "phase": self.state.current_phase,
            "follow_up_eligible": False
        }

    def _prepare_next_question(self):
        """
        Select and store the next question based on the
        current interview phase.
        """

        phase = self.state.current_phase

        if phase == "introduction":
            categories = self.PHASE_QUESTION_CATEGORIES[
                "introduction"
            ]

        elif phase == "core_hr":
            categories = self.PHASE_QUESTION_CATEGORIES[
                "core_hr"
            ]

        elif phase == "role_based_evaluation":
            return self._prepare_role_question()

        elif phase == "closing":
            self.state.complete_interview()
            return None

        else:
            raise ValueError(
                f"Unknown interview phase: {phase}"
            )

        if self.category_index >= len(categories):
            self.category_index = 0
            self.question_index = 0

            next_phase = self.flow.move_to_next_phase()

            if next_phase == "closing":
                return self._prepare_next_question()

            return self._prepare_next_question()

        category = categories[self.category_index]

        questions = self.question_generator.generate(
            category,
            self.state.candidate_type,
            self.state.role_type
        )

        if self.question_index >= len(questions):
            self.category_index += 1
            self.question_index = 0
            return self._prepare_next_question()

        question = questions[self.question_index]

        question_id = (
            f"{phase.upper()}-"
            f"{self.category_index + 1:02d}-"
            f"{self.question_index + 1:02d}"
        )

        self.current_category = category

        self.state.set_question(
            question_id,
            question
        )

        self.question_index += 1

        return question

    def _prepare_role_question(self):
        """
        Prepare a role-specific evaluation question.

        The first V2 implementation keeps this deterministic so
        the role-specific layer can later be connected to a richer
        role question bank or AI-generated question service.
        """

        role = self.state.role

        if self.state.role_type == "technical":
            question = (
                f"Could you describe a technical challenge "
                f"you would expect to face in a {role} role "
                f"and how you would approach it?"
            )
        else:
            question = (
                f"Could you describe how your experience "
                f"would help you contribute effectively as a {role}?"
            )

        self.current_category = "role_based_evaluation"

        self.state.set_question(
            "ROLE-EVAL-001",
            question
        )

        return question

    def get_state(self):
        """
        Return the complete interview state.
        """
        return self.flow.get_state()