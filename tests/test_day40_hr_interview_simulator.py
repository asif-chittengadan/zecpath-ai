import unittest

from interview_ai.hr.hr_interview_simulator import (
    HRInterviewSimulator
)


class TestDay40HRInterviewSimulator(unittest.TestCase):

    def setUp(self):
        self.simulator = HRInterviewSimulator()

    def test_confident_candidate(self):
        result = self.simulator.simulate(
            "confident"
        )

        self.assertEqual(
            result["candidate_type"],
            "confident"
        )

        self.assertGreater(
            result["response_count"],
            0
        )

    def test_hesitant_candidate(self):
        result = self.simulator.simulate(
            "hesitant"
        )

        self.assertEqual(
            result["candidate_type"],
            "hesitant"
        )

    def test_inexperienced_candidate(self):
        result = self.simulator.simulate(
            "inexperienced"
        )

        self.assertEqual(
            result["candidate_type"],
            "inexperienced"
        )

    def test_overqualified_candidate(self):
        result = self.simulator.simulate(
            "overqualified"
        )

        self.assertEqual(
            result["candidate_type"],
            "overqualified"
        )

    def test_all_candidate_types(self):
        sessions = self.simulator.simulate_all()

        self.assertEqual(
            len(sessions),
            4
        )

        candidate_types = {
            session["candidate_type"]
            for session in sessions
        }

        self.assertEqual(
            candidate_types,
            {
                "confident",
                "hesitant",
                "inexperienced",
                "overqualified"
            }
        )

    def test_custom_responses(self):
        responses = [
            "Custom response 1",
            "Custom response 2"
        ]

        result = self.simulator.simulate(
            "confident",
            candidate_name="John",
            responses=responses
        )

        self.assertEqual(
            result["candidate_name"],
            "John"
        )

        self.assertEqual(
            result["responses"],
            responses
        )

        self.assertEqual(
            result["response_count"],
            2
        )

    def test_empty_responses(self):
        result = self.simulator.simulate(
            "confident",
            responses=[]
        )

        self.assertEqual(
            result["response_count"],
            0
        )

    def test_invalid_candidate_type(self):
        with self.assertRaises(ValueError):
            self.simulator.simulate(
                "unknown"
            )


if __name__ == "__main__":
    unittest.main()