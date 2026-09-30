import unittest

from interview_ai.hr.interview_summary_pipeline import (
    InterviewSummaryPipeline
)


class TestDay39InterviewSummaryPipeline(unittest.TestCase):

    def setUp(self):
        self.pipeline = InterviewSummaryPipeline()

    def test_generates_complete_pipeline(self):
        result = self.pipeline.generate(
            candidate_name="John",
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
            overall_score=82,
            component_scores={
                "answer_relevance": 85,
                "communication": 80,
                "confidence": 78,
                "consistency": 86
            }
        )

        self.assertEqual(
            result["candidate_name"],
            "John"
        )

        self.assertIn(
            "structured_summary",
            result
        )

        self.assertIn(
            "natural_language_report",
            result
        )

        self.assertEqual(
            result["structured_summary"][
                "overall_hr_performance"
            ]["overall_score"],
            82
        )

        self.assertTrue(
            result["structured_summary"][
                "risk_analysis"
            ]["has_risk_flags"]
        )

        self.assertTrue(
            result["structured_summary"][
                "risk_analysis"
            ]["has_inconsistencies"]
        )

    def test_pipeline_without_optional_data(self):
        result = self.pipeline.generate(
            candidate_name="John"
        )

        summary = result["structured_summary"]

        self.assertEqual(
            summary["candidate_strengths"],
            []
        )

        self.assertEqual(
            summary["candidate_weaknesses"],
            []
        )

        self.assertEqual(
            summary["risk_flags"],
            []
        )

        self.assertEqual(
            summary["inconsistencies"],
            []
        )

        self.assertIsNone(
            summary["overall_hr_performance"][
                "overall_score"
            ]
        )

    def test_duplicate_risk_items_are_cleaned(self):
        result = self.pipeline.generate(
            candidate_name="John",
            risk_flags=[
                "Availability concern",
                "Availability concern"
            ],
            inconsistencies=[
                "Experience mismatch",
                "Experience mismatch"
            ]
        )

        risk_analysis = result[
            "structured_summary"
        ]["risk_analysis"]

        self.assertEqual(
            risk_analysis["risk_flag_count"],
            1
        )

        self.assertEqual(
            risk_analysis["inconsistency_count"],
            1
        )

    def test_report_contains_candidate_information(self):
        result = self.pipeline.generate(
            candidate_name="John",
            strengths=[
                "Good communication"
            ],
            overall_score=80
        )

        report = result[
            "natural_language_report"
        ]

        self.assertIn(
            "Candidate: John",
            report
        )

        self.assertIn(
            "Good communication",
            report
        )

        self.assertIn(
            "80.00/100",
            report
        )


if __name__ == "__main__":
    unittest.main()