import unittest

from interview_ai.hr.aptitude_logic_scoring_engine import (
    AptitudeLogicScoringEngine
)


class TestDay38ClarityIntegration(unittest.TestCase):

    def setUp(self):
        self.engine = AptitudeLogicScoringEngine(
            "config/aptitude_scoring_rules.json"
        )

    def test_clarity_analysis(self):
        response = (
            "First, I would identify the root cause. "
            "Then I would analyze the issue and consider "
            "different approaches. Finally, I would implement "
            "the solution and test the result."
        )

        result = self.engine.analyze_problem_solving_clarity(
            response
        )

        self.assertEqual(
            result["clarity_score"],
            100
        )

        self.assertEqual(
            result["clarity_level"],
            "high"
        )

    def test_clarity_score(self):
        response = (
            "I would identify the problem and then "
            "find a solution."
        )

        score = self.engine.get_clarity_score(
            response
        )

        self.assertGreaterEqual(score, 0)
        self.assertLessEqual(score, 100)

    def test_empty_response(self):
        score = self.engine.get_clarity_score("")

        self.assertEqual(score, 0)

    def test_invalid_response(self):
        score = self.engine.get_clarity_score(None)

        self.assertEqual(score, 0)

    def test_partial_clarity(self):
        response = (
            "I would identify the problem."
        )

        result = self.engine.analyze_problem_solving_clarity(
            response
        )

        self.assertGreater(
            result["clarity_score"],
            0
        )

        self.assertLessEqual(
            result["clarity_score"],
            100
        )


if __name__ == "__main__":
    unittest.main()