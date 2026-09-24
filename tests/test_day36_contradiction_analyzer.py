import unittest

from interview_ai.hr.contradiction_analyzer import (
    ContradictionAnalyzer
)


class TestDay36ContradictionAnalyzer(unittest.TestCase):

    def setUp(self):
        self.analyzer = ContradictionAnalyzer()

    def test_no_previous_data(self):
        result = self.analyzer.analyze(
            "I have two years of experience."
        )

        self.assertFalse(
            result["contradiction_detected"]
        )

    def test_matching_experience_has_no_conflict(self):
        result = self.analyzer.analyze(
            "I have two years of experience.",
            {
                "experience_years": 2
            }
        )

        self.assertFalse(
            result["contradiction_detected"]
        )

    def test_different_experience_is_detected(self):
        result = self.analyzer.analyze(
            "I have three years of experience.",
            {
                "experience_years": 2
            }
        )

        self.assertTrue(
            result["contradiction_detected"]
        )

        self.assertIn(
            "experience_conflict",
            result["contradictions"]
        )

    def test_matching_availability_has_no_conflict(self):
        result = self.analyzer.analyze(
            "I can join in 30 days.",
            {
                "availability_days": 30
            }
        )

        self.assertFalse(
            result["contradiction_detected"]
        )

    def test_different_availability_is_detected(self):
        result = self.analyzer.analyze(
            "I can join in 60 days.",
            {
                "availability_days": 30
            }
        )

        self.assertTrue(
            result["contradiction_detected"]
        )

        self.assertIn(
            "availability_conflict",
            result["contradictions"]
        )

    def test_multiple_contradictions(self):
        result = self.analyzer.analyze(
            (
                "I have five years of experience "
                "and I can join in 60 days."
            ),
            {
                "experience_years": 2,
                "availability_days": 30
            }
        )

        self.assertTrue(
            result["contradiction_detected"]
        )

        self.assertEqual(
            result["count"],
            2
        )

    def test_empty_response_is_safe(self):
        result = self.analyzer.analyze(
            "",
            {
                "experience_years": 2
            }
        )

        self.assertFalse(
            result["contradiction_detected"]
        )

    def test_invalid_previous_data_is_safe(self):
        result = self.analyzer.analyze(
            "I have two years of experience.",
            {
                "experience_years": "invalid"
            }
        )

        self.assertFalse(
            result["contradiction_detected"]
        )

    def test_result_structure(self):
        result = self.analyzer.analyze(
            "I worked on Python."
        )

        self.assertIn(
            "contradiction_detected",
            result
        )

        self.assertIn(
            "contradictions",
            result
        )

        self.assertIn(
            "count",
            result
        )


if __name__ == "__main__":
    unittest.main()