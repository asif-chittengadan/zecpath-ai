import json
import tempfile
import unittest
from pathlib import Path

from interview_ai.hr.interview_summary_pipeline import (
    InterviewSummaryPipeline
)


class TestInterviewSummaryStorage(unittest.TestCase):

    def test_output_is_saved_automatically(self):

        with tempfile.TemporaryDirectory() as temp_dir:

            output_path = (
                Path(temp_dir)
                / "interview_summaries"
                / "interview_summary.json"
            )

            pipeline = InterviewSummaryPipeline(
                output_path=output_path
            )

            result = pipeline.generate(
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

            self.assertTrue(
                output_path.exists()
            )

            with output_path.open(
                "r",
                encoding="utf-8"
            ) as file:
                saved_data = json.load(file)

            self.assertEqual(
                saved_data["candidate_name"],
                "John"
            )

            self.assertEqual(
                saved_data["structured_summary"][
                    "overall_hr_performance"
                ]["overall_score"],
                82
            )

            self.assertIn(
                "natural_language_report",
                saved_data
            )

            self.assertEqual(
                result,
                saved_data
            )


if __name__ == "__main__":
    unittest.main()