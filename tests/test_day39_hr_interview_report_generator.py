import unittest

from interview_ai.hr.hr_interview_report_generator import (
    HRInterviewReportGenerator
)


class TestDay39HRInterviewReportGenerator(unittest.TestCase):

    def setUp(self):
        self.generator = HRInterviewReportGenerator()

        self.summary = {
            "candidate_strengths": [
                "Strong communication",
                "Good problem solving"
            ],
            "candidate_weaknesses": [
                "Limited experience"
            ],
            "cultural_fit_indicators": [
                "Team oriented"
            ],
            "risk_flags": [
                "Availability concern"
            ],
            "inconsistencies": [
                "Experience mismatch"
            ],
            "overall_hr_performance": {
                "score": 82,
                "level": "high"
            }
        }

    def test_generates_report(self):
        report = self.generator.generate_report(
            candidate_name="John",
            summary=self.summary
        )

        self.assertIn(
            "HR Interview Report",
            report
        )

        self.assertIn(
            "Candidate: John",
            report
        )

        self.assertIn(
            "Strong communication",
            report
        )

        self.assertIn(
            "Limited experience",
            report
        )

        self.assertIn(
            "Availability concern",
            report
        )

        self.assertIn(
            "Experience mismatch",
            report
        )

    def test_includes_score(self):
        report = self.generator.generate_report(
            candidate_name="John",
            summary=self.summary
        )

        self.assertIn(
            "82.00/100",
            report
        )

        self.assertIn(
            "Performance Level: high",
            report
        )

    def test_external_score_can_be_used(self):
        report = self.generator.generate_report(
            candidate_name="John",
            summary=self.summary,
            overall_score=91
        )

        self.assertIn(
            "91.00/100",
            report
        )

    def test_empty_summary(self):
        report = self.generator.generate_report(
            candidate_name="John",
            summary={}
        )

        self.assertIn(
            "No specific strengths were recorded.",
            report
        )

        self.assertIn(
            "No specific weaknesses were recorded.",
            report
        )

        self.assertIn(
            "No risk flags were recorded.",
            report
        )

        self.assertIn(
            "No inconsistencies were identified.",
            report
        )

    def test_invalid_summary_is_safe(self):
        report = self.generator.generate_report(
            candidate_name="John",
            summary=None
        )

        self.assertIn(
            "Candidate: John",
            report
        )

        self.assertIn(
            "Not available",
            report
        )

    def test_empty_candidate_name(self):
        report = self.generator.generate_report(
            candidate_name="",
            summary=self.summary
        )

        self.assertIn(
            "Candidate: Candidate",
            report
        )


if __name__ == "__main__":
    unittest.main()