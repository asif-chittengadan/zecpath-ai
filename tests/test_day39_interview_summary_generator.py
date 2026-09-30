import unittest

from interview_ai.hr.interview_summary_generator import (
    InterviewSummaryGenerator
)


class TestDay39InterviewSummaryGenerator(unittest.TestCase):

    def setUp(self):
        self.generator = InterviewSummaryGenerator()

    def test_generate_complete_summary(self):
        result = self.generator.generate_summary(
            strengths=[
                "Strong communication",
                "Good problem solving"
            ],
            weaknesses=[
                "Limited experience"
            ],
            cultural_fit_indicators=[
                "Team oriented"
            ],
            risk_flags=[
                "Availability concern"
            ],
            inconsistencies=[
                "Experience mismatch"
            ],
            overall_hr_score=82
        )

        self.assertEqual(
            result["candidate_strengths"],
            ["Strong communication", "Good problem solving"]
        )

        self.assertEqual(
            result["candidate_weaknesses"],
            ["Limited experience"]
        )

        self.assertEqual(
            result["cultural_fit_indicators"],
            ["Team oriented"]
        )

        self.assertEqual(
            result["risk_flags"],
            ["Availability concern"]
        )

        self.assertEqual(
            result["inconsistencies"],
            ["Experience mismatch"]
        )

        self.assertEqual(
            result["overall_hr_performance"]["score"],
            82
        )

        self.assertEqual(
            result["overall_hr_performance"]["level"],
            "high"
        )

    def test_empty_summary(self):
        result = self.generator.generate_summary()

        self.assertEqual(
            result["candidate_strengths"],
            []
        )

        self.assertEqual(
            result["candidate_weaknesses"],
            []
        )

        self.assertEqual(
            result["risk_flags"],
            []
        )

        self.assertEqual(
            result["inconsistencies"],
            []

        )

    def test_score_levels(self):
        self.assertEqual(
            self.generator.generate_summary(
                overall_hr_score=90
            )["overall_hr_performance"]["level"],
            "high"
        )

        self.assertEqual(
            self.generator.generate_summary(
                overall_hr_score=60
            )["overall_hr_performance"]["level"],
            "moderate"
        )

        self.assertEqual(
            self.generator.generate_summary(
                overall_hr_score=30
            )["overall_hr_performance"]["level"],
            "low"
        )

        self.assertEqual(
            self.generator.generate_summary(
                overall_hr_score=10
            )["overall_hr_performance"]["level"],
            "very_low"
        )

    def test_score_is_bounded(self):
        high = self.generator.generate_summary(
            overall_hr_score=150
        )

        low = self.generator.generate_summary(
            overall_hr_score=-20
        )

        self.assertEqual(
            high["overall_hr_performance"]["score"],
            100
        )

        self.assertEqual(
            low["overall_hr_performance"]["score"],
            0
        )

    def test_invalid_score_is_safe(self):
        result = self.generator.generate_summary(
            overall_hr_score="invalid"
        )

        self.assertIsNone(
            result["overall_hr_performance"]["score"]
        )

        self.assertEqual(
            result["overall_hr_performance"]["level"],
            "not_available"
        )


if __name__ == "__main__":
    unittest.main()