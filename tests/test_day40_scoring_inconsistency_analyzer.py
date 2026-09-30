import unittest

from interview_ai.hr.hr_scoring_inconsistency_analyzer import (
    HRScoringInconsistencyAnalyzer
)


class TestDay40ScoringInconsistencyAnalyzer(unittest.TestCase):

    def setUp(self):
        self.analyzer = HRScoringInconsistencyAnalyzer()

    def test_exact_match(self):
        comparison = {
            "average_difference": 0,
            "inconsistency_count": 0,
            "inconsistent_parameters": []
        }

        result = self.analyzer.analyze(
            comparison
        )

        self.assertEqual(
            result["accuracy_level"],
            "exact_match"
        )

        self.assertEqual(
            result["recommendations"],
            []
        )

    def test_high_alignment(self):
        comparison = {
            "average_difference": 4,
            "inconsistency_count": 0,
            "inconsistent_parameters": []
        }

        result = self.analyzer.analyze(
            comparison
        )

        self.assertEqual(
            result["accuracy_level"],
            "high_alignment"
        )

    def test_moderate_alignment(self):
        comparison = {
            "average_difference": 8,
            "inconsistency_count": 1,
            "inconsistent_parameters": [
                "communication"
            ]
        }

        result = self.analyzer.analyze(
            comparison
        )

        self.assertEqual(
            result["accuracy_level"],
            "moderate_alignment"
        )

        self.assertEqual(
            result["inconsistency_count"],
            1
        )

        self.assertEqual(
            len(result["recommendations"]),
            1
        )

    def test_low_alignment(self):
        comparison = {
            "average_difference": 15,
            "inconsistency_count": 2,
            "inconsistent_parameters": [
                "confidence",
                "answer_relevance"
            ]
        }

        result = self.analyzer.analyze(
            comparison
        )

        self.assertEqual(
            result["accuracy_level"],
            "low_alignment"
        )

        self.assertEqual(
            len(result["recommendations"]),
            2
        )

    def test_parameter_specific_recommendation(self):
        comparison = {
            "average_difference": 12,
            "inconsistency_count": 1,
            "inconsistent_parameters": [
                "confidence"
            ]
        }

        result = self.analyzer.analyze(
            comparison
        )

        self.assertIn(
            "confidence",
            result["recommendations"][0]
        )


if __name__ == "__main__":
    unittest.main()