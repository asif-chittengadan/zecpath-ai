import unittest

from interview_ai.hr.problem_solving_clarity_analyzer import (
    ProblemSolvingClarityAnalyzer
)


class TestDay38ProblemSolvingClarity(unittest.TestCase):

    def setUp(self):
        self.analyzer = ProblemSolvingClarityAnalyzer()

    def test_all_indicators_detected(self):
        response = (
            "First, I would identify the root cause. "
            "Then I would analyze the issue and consider "
            "different approaches. Finally, I would implement "
            "the solution and test the result."
        )

        result = self.analyzer.analyze(response)

        self.assertTrue(result["problem_identification"])
        self.assertTrue(result["approach_present"])
        self.assertTrue(result["alternatives_present"])
        self.assertTrue(result["solution_present"])
        self.assertEqual(result["clarity_score"], 100)
        self.assertEqual(result["clarity_level"], "high")

    def test_problem_identification(self):
        result = self.analyzer.analyze(
            "I would first identify the problem."
        )

        self.assertTrue(result["problem_identification"])
        self.assertEqual(result["clarity_score"], 50)

    def test_approach_detection(self):
        result = self.analyzer.analyze(
            "First I would analyze the issue and debug it."
        )

        self.assertTrue(result["approach_present"])

    def test_alternative_detection(self):
        result = self.analyzer.analyze(
            "I would consider different approaches and options."
        )

        self.assertTrue(result["alternatives_present"])

    def test_solution_detection(self):
        result = self.analyzer.analyze(
            "Finally, I would implement the solution."
        )

        self.assertTrue(result["solution_present"])

    def test_empty_response(self):
        result = self.analyzer.analyze("")

        self.assertEqual(result["clarity_score"], 0)
        self.assertEqual(result["detected_indicators"], 0)
        self.assertEqual(result["clarity_level"], "very_low")

    def test_invalid_response_is_safe(self):
        result = self.analyzer.analyze(None)

        self.assertEqual(result["clarity_score"], 0)

    def test_score_is_bounded(self):
        result = self.analyzer.analyze(
            "identify the problem approach alternatives solution"
        )

        self.assertGreaterEqual(result["clarity_score"], 0)
        self.assertLessEqual(result["clarity_score"], 100)


if __name__ == "__main__":
    unittest.main()