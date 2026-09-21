import unittest

from interview_ai.hr.interview_state import InterviewState


class TestDay33InterviewState(unittest.TestCase):

    def setUp(self):
        self.state = InterviewState(
            session_id="DAY33-SESSION-001",
            candidate_id="CAND-001",
            role="Software Developer",
            candidate_type="fresher",
            role_type="technical"
        )

    def test_initial_state(self):
        self.assertEqual(
            self.state.current_phase,
            "introduction"
        )

        self.assertEqual(
            self.state.questions_answered,
            0
        )

        self.assertFalse(
            self.state.interview_completed
        )

    def test_set_question(self):
        self.state.set_question(
            "Q001",
            "Could you please introduce yourself?"
        )

        self.assertEqual(
            self.state.current_question_id,
            "Q001"
        )

        self.assertEqual(
            self.state.current_question,
            "Could you please introduce yourself?"
        )

    def test_capture_response(self):
        self.state.set_question(
            "Q001",
            "Could you please introduce yourself?"
        )

        self.state.capture_response(
            "I am a B.Tech graduate with a background in IT.",
            follow_up_eligible=True
        )

        self.assertEqual(
            self.state.response,
            "I am a B.Tech graduate with a background in IT."
        )

        self.assertTrue(
            self.state.follow_up_eligible
        )

        self.assertEqual(
            self.state.questions_answered,
            1
        )

        self.assertEqual(
            len(self.state.response_history),
            1
        )

    def test_change_phase(self):
        self.state.change_phase("core_hr")

        self.assertEqual(
            self.state.current_phase,
            "core_hr"
        )

    def test_complete_interview(self):
        self.state.complete_interview()

        self.assertTrue(
            self.state.interview_completed
        )

        self.assertEqual(
            self.state.current_phase,
            "closing"
        )

    def test_get_state(self):
        self.state.set_question(
            "Q001",
            "Tell me about yourself."
        )

        result = self.state.get_state()

        self.assertEqual(
            result["session_id"],
            "DAY33-SESSION-001"
        )

        self.assertEqual(
            result["current_question_id"],
            "Q001"
        )

        self.assertIn(
            "response_history",
            result
        )


if __name__ == "__main__":
    unittest.main()