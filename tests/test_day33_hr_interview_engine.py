import unittest

from interview_ai.hr.hr_interview_engine import HRInterviewEngine


class TestDay33HRInterviewEngine(unittest.TestCase):

    def setUp(self):
        self.engine = HRInterviewEngine(
            session_id="DAY33-INTEGRATION-001",
            candidate_id="CAND-001",
            role="Software Developer",
            candidate_type="fresher",
            role_type="technical"
        )

    def test_start_interview(self):
        question = self.engine.start()

        self.assertIsNotNone(question)

        self.assertEqual(
            self.engine.get_state()["current_phase"],
            "introduction"
        )

    def test_short_response_creates_follow_up(self):
        self.engine.start()

        result = self.engine.submit_response(
            "I am a graduate."
        )

        self.assertEqual(
            result["action"],
            "follow_up"
        )

        self.assertTrue(
            result["follow_up_eligible"]
        )

    def test_detailed_response_moves_forward(self):
        self.engine.start()

        result = self.engine.submit_response(
            (
                "I completed my degree in Information Technology "
                "and worked on several software development projects "
                "using Python, Django and SQL."
            )
        )

        self.assertEqual(
            result["action"],
            "next_question"
        )

    def test_response_is_stored(self):
        self.engine.start()

        self.engine.submit_response(
            (
                "I completed my degree in Information Technology "
                "and worked on several software development projects."
            )
        )

        state = self.engine.get_state()

        self.assertGreaterEqual(
            state["questions_answered"],
            1
        )

        self.assertGreaterEqual(
            len(state["response_history"]),
            1
        )

    def test_role_based_phase(self):
        self.engine.start()

        # Complete the interview until the role-based phase is reached.
        for _ in range(20):
            state = self.engine.get_state()

            if state["current_phase"] == "role_based_evaluation":
                break

            if state["interview_completed"]:
                break

            self.engine.submit_response(
                (
                    "I completed my degree in Information Technology "
                    "and worked on meaningful projects, collaborated "
                    "with teammates, solved problems and continuously "
                    "improved my technical and professional skills."
                )
            )

        self.assertEqual(
            self.engine.get_state()["current_phase"],
            "role_based_evaluation"
        )

    def test_engine_state_contains_candidate_information(self):
        self.engine.start()

        state = self.engine.get_state()

        self.assertEqual(
            state["candidate_id"],
            "CAND-001"
        )

        self.assertEqual(
            state["role"],
            "Software Developer"
        )

        self.assertEqual(
            state["candidate_type"],
            "fresher"
        )

        self.assertEqual(
            state["role_type"],
            "technical"
        )


if __name__ == "__main__":
    unittest.main()