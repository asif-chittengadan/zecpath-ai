import unittest

from interview_ai.hr.hr_interview_engine import (
    HRInterviewEngine
)


class TestDay34HRInterviewIntegration(unittest.TestCase):

    def setUp(self):
        self.engine = HRInterviewEngine(
            session_id="DAY34-INTEGRATION-001",
            candidate_id="CAND-034",
            role="Software Developer",
            candidate_type="fresher",
            role_type="technical"
        )

    def test_start_interview(self):
        question = self.engine.start()

        self.assertIsNotNone(question)

        state = self.engine.get_state()

        self.assertEqual(
            state["current_phase"],
            "introduction"
        )

    def test_incomplete_response_triggers_clarification(self):
        self.engine.start()

        result = self.engine.submit_response(
            "I am a graduate."
        )

        self.assertEqual(
            result["classification"],
            "incomplete"
        )

        self.assertEqual(
            result["follow_up_type"],
            "clarification"
        )

        self.assertTrue(
            result["follow_up_required"]
        )

    def test_vague_response_triggers_deepening(self):
        self.engine.start()

        result = self.engine.submit_response(
            (
                "Maybe I worked on something like that "
                "during my project and things like that."
            )
        )

        self.assertEqual(
            result["classification"],
            "vague"
        )

        self.assertEqual(
            result["follow_up_type"],
            "deepening"
        )

    def test_complete_introduction_moves_forward(self):
        self.engine.start()

        result = self.engine.submit_response(
            (
                "I completed my degree in Information Technology "
                "and worked on several software development projects "
                "using Python, Django and SQL."
            )
        )

        self.assertEqual(
            result["classification"],
            "complete"
        )

        self.assertEqual(
            result["action"],
            "next_question"
        )

    def test_confident_response_uses_scenario_follow_up(self):
        self.engine.start()

        result = self.engine.submit_response(
            (
                "I successfully implemented the backend using Python "
                "and Django and I was responsible for the database "
                "integration and API development."
            )
        )

        self.assertEqual(
            result["classification"],
            "confident"
        )

        self.assertEqual(
            result["follow_up_type"],
            "scenario_based"
        )

        self.assertEqual(
            result["difficulty_level"],
            3
        )

    def test_dynamic_state_is_updated(self):
        self.engine.start()

        self.engine.submit_response(
            "I am a graduate."
        )

        state = self.engine.get_dynamic_state()

        self.assertEqual(
            state["last_classification"],
            "incomplete"
        )

        self.assertEqual(
            state["difficulty_level"],
            1
        )

        self.assertGreaterEqual(
            state["follow_up_count"],
            1
        )

    def test_repetition_guard_is_active(self):
        self.engine.start()

        result = self.engine.submit_response(
            "I am a graduate."
        )

        follow_up_question = result["question"]

        dynamic_state = self.engine.get_dynamic_state()

        self.assertIn(
            follow_up_question,
            dynamic_state["asked_questions"]
        )

    def test_day33_candidate_state_remains_available(self):
        self.engine.start()

        self.engine.submit_response(
            "I am a graduate."
        )

        state = self.engine.get_state()

        self.assertEqual(
            state["candidate_id"],
            "CAND-034"
        )

        self.assertGreaterEqual(
            state["questions_answered"],
            1
        )


if __name__ == "__main__":
    unittest.main()