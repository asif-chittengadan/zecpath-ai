import unittest

from interview_ai.hr.interview_risk_analyzer import (
    InterviewRiskAnalyzer
)


class TestDay39InterviewRiskAnalyzer(unittest.TestCase):

    def setUp(self):
        self.analyzer = InterviewRiskAnalyzer()

    def test_detects_inconsistencies(self):
        result = self.analyzer.analyze(
            inconsistencies=[
                "Experience mismatch",
                "Availability mismatch"
            ]
        )

        self.assertTrue(
            result["has_inconsistencies"]
        )

        self.assertEqual(
            result["inconsistency_count"],
            2
        )

    def test_detects_risk_flags(self):
        result = self.analyzer.analyze(
            risk_flags=[
                "Availability concern",
                "Communication concern"
            ]
        )

        self.assertTrue(
            result["has_risk_flags"]
        )

        self.assertEqual(
            result["risk_flag_count"],
            2
        )

    def test_duplicate_items_are_removed(self):
        result = self.analyzer.analyze(
            inconsistencies=[
                "Experience mismatch",
                "Experience mismatch",
                "Availability mismatch"
            ],
            risk_flags=[
                "Availability concern",
                "Availability concern"
            ]
        )

        self.assertEqual(
            result["inconsistency_count"],
            2
        )

        self.assertEqual(
            result["risk_flag_count"],
            1
        )

    def test_empty_analysis(self):
        result = self.analyzer.analyze()

        self.assertFalse(
            result["has_inconsistencies"]
        )

        self.assertFalse(
            result["has_risk_flags"]
        )

        self.assertEqual(
            result["inconsistency_count"],
            0
        )

        self.assertEqual(
            result["risk_flag_count"],
            0
        )

    def test_invalid_input_is_safe(self):
        result = self.analyzer.analyze(
            inconsistencies="invalid",
            risk_flags=None
        )

        self.assertEqual(
            result["inconsistencies"],
            []
        )

        self.assertEqual(
            result["risk_flags"],
            []
        )


if __name__ == "__main__":
    unittest.main()