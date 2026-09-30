import json
import tempfile
import unittest
from pathlib import Path

from interview_ai.hr.hr_interview_test_report_generator import (
    HRInterviewTestReportGenerator
)


class TestDay40HRInterviewTestReportGenerator(
    unittest.TestCase
):

    def test_generates_four_candidate_reports(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = (
                Path(temp_dir)
                / "report.json"
            )

            generator = HRInterviewTestReportGenerator(
                output_path=output_path
            )

            report = generator.generate()

            self.assertEqual(
                report["candidate_count"],
                4
            )

            self.assertEqual(
                len(report["candidate_reports"]),
                4
            )

    def test_accuracy_evaluation_available(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = (
                Path(temp_dir)
                / "report.json"
            )

            generator = HRInterviewTestReportGenerator(
                output_path=output_path
            )

            report = generator.generate()

            self.assertIn(
                "overall_accuracy_evaluation",
                report
            )

            self.assertIn(
                "average_difference",
                report[
                    "overall_accuracy_evaluation"
                ]
            )

    def test_recommendations_available(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = (
                Path(temp_dir)
                / "report.json"
            )

            generator = HRInterviewTestReportGenerator(
                output_path=output_path
            )

            report = generator.generate()

            self.assertIn(
                "improvement_recommendations",
                report
            )

            self.assertIsInstance(
                report[
                    "improvement_recommendations"
                ],
                list
            )

    def test_report_is_saved(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = (
                Path(temp_dir)
                / "report.json"
            )

            generator = HRInterviewTestReportGenerator(
                output_path=output_path
            )

            report = generator.generate()

            self.assertTrue(
                output_path.exists()
            )

            with output_path.open(
                "r",
                encoding="utf-8"
            ) as file:
                saved_report = json.load(file)

            self.assertEqual(
                report,
                saved_report
            )

    def test_candidate_types_are_present(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = (
                Path(temp_dir)
                / "report.json"
            )

            generator = HRInterviewTestReportGenerator(
                output_path=output_path
            )

            report = generator.generate()

            candidate_types = {
                candidate["candidate_type"]
                for candidate in report[
                    "candidate_reports"
                ]
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


if __name__ == "__main__":
    unittest.main()