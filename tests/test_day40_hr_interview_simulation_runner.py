import unittest

from interview_ai.hr.hr_interview_simulation_runner import (
    HRInterviewSimulationRunner
)


class TestDay40HRInterviewSimulationRunner(unittest.TestCase):

    def setUp(self):
        self.runner = HRInterviewSimulationRunner()

    def test_confident_candidate(self):
        result = self.runner.run_candidate(
            "confident"
        )

        self.assertEqual(
            result["candidate_type"],
            "confident"
        )

        self.assertIn(
            "hr_score",
            result
        )

        self.assertGreaterEqual(
            result["hr_score"]["final_score"],
            0
        )

        self.assertLessEqual(
            result["hr_score"]["final_score"],
            100
        )

    def test_hesitant_candidate(self):
        result = self.runner.run_candidate(
            "hesitant"
        )

        self.assertEqual(
            result["candidate_type"],
            "hesitant"
        )

        self.assertIn(
            "hr_score",
            result
        )

    def test_inexperienced_candidate(self):
        result = self.runner.run_candidate(
            "inexperienced"
        )

        self.assertEqual(
            result["candidate_type"],
            "inexperienced"
        )

    def test_overqualified_candidate(self):
        result = self.runner.run_candidate(
            "overqualified"
        )

        self.assertEqual(
            result["candidate_type"],
            "overqualified"
        )

    def test_run_all_candidates(self):
        results = self.runner.run_all()

        self.assertEqual(
            len(results),
            4
        )

        candidate_types = {
            result["candidate_type"]
            for result in results
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

    def test_normalized_scores_are_available(self):
        result = self.runner.run_candidate(
            "confident"
        )

        scores = result["normalized_scores"]

        self.assertIn(
            "answer_relevance",
            scores
        )

        self.assertIn(
            "communication",
            scores
        )

        self.assertIn(
            "confidence",
            scores
        )

        self.assertIn(
            "consistency",
            scores
        )

    def test_custom_scores(self):
        scores = {
            "answer_relevance": [80, 80],
            "communication": [70, 70],
            "confidence": [60, 60],
            "consistency": [90, 90]
        }

        result = self.runner.run_candidate(
            "confident",
            question_scores=scores
        )

        self.assertEqual(
            result["normalized_scores"]["answer_relevance"],
            80
        )

        self.assertEqual(
            result["normalized_scores"]["communication"],
            70
        )


if __name__ == "__main__":
    unittest.main()