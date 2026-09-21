import unittest

from interview_ai.hr.interview_state import InterviewState
from interview_ai.hr.interview_flow import HRInterviewFlow


class TestDay33InterviewFlow(unittest.TestCase):

    def setUp(self):
        state = InterviewState(
            session_id="DAY33-FLOW-001",
            candidate_id="CAND-001",
            role="Software Developer",
            candidate_type="fresher",
            role_type="technical"
        )

        self.flow = HRInterviewFlow(state)

    def test_start_interview(self):
        phase = self.flow.start()

        self.assertEqual(
            phase,
            "introduction"
        )

    def test_move_from_introduction_to_core_hr(self):
        self.flow.start()

        phase = self.flow.move_to_next_phase()

        self.assertEqual(
            phase,
            "core_hr"
        )

    def test_move_to_role_based_evaluation(self):
        self.flow.start()

        self.flow.move_to_next_phase()

        phase = self.flow.move_to_next_phase()

        self.assertEqual(
            phase,
            "role_based_evaluation"
        )

    def test_move_to_closing(self):
        self.flow.start()

        self.flow.move_to_next_phase()
        self.flow.move_to_next_phase()

        phase = self.flow.move_to_next_phase()

        self.assertEqual(
            phase,
            "closing"
        )

    def test_complete_after_closing(self):
        self.flow.start()

        self.flow.move_to_next_phase()
        self.flow.move_to_next_phase()
        self.flow.move_to_next_phase()

        self.assertEqual(
            self.flow.get_current_phase(),
            "closing"
        )

        self.flow.move_to_next_phase()

        self.assertTrue(
            self.flow.is_completed()
        )

    def test_question_and_response_flow(self):
        self.flow.start()

        self.flow.set_question(
            "INTRO-001",
            "Could you please introduce yourself?"
        )

        self.flow.capture_response(
            "I am a B.Tech graduate in Information Technology.",
            follow_up_eligible=True
        )

        state = self.flow.get_state()

        self.assertEqual(
            state["current_question_id"],
            "INTRO-001"
        )

        self.assertEqual(
            state["questions_answered"],
            1
        )

        self.assertTrue(
            state["follow_up_eligible"]
        )

    def test_invalid_state_type(self):
        with self.assertRaises(TypeError):
            HRInterviewFlow("invalid-state")


if __name__ == "__main__":
    unittest.main()