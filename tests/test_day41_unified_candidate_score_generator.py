import json
import tempfile
import unittest
from pathlib import Path

from scoring.unified_candidate_score_generator import (
    UnifiedCandidateScoreGenerator
)


class TestDay41UnifiedCandidateScoreGenerator(
    unittest.TestCase
):

    def test_generate_returns_unified_object(self):

        with tempfile.TemporaryDirectory() as temp_dir:

            output_path = (
                Path(temp_dir)
                / "unified_score.json"
            )

            generator = (
                UnifiedCandidateScoreGenerator(
                    output_path=output_path
                )
            )

            result = generator.generate(
                candidate_name="Test Candidate",
                role="Test Role",
                ats_score=80,
                screening_score=8,
                hr_interview_score=90
            )

            self.assertEqual(
                result["candidate"],
                "Test Candidate"
            )

            self.assertEqual(
                result["role"],
                "Test Role"
            )

            self.assertEqual(
                result["unified_score"],
                83.5
            )

            self.assertEqual(
                result["hiring_fit_percentage"],
                83.5
            )

            self.assertEqual(
                result["score_type"],
                "unified_candidate_score"
            )

            self.assertEqual(
                result["round_count"],
                3
            )

    def test_output_file_is_created(self):

        with tempfile.TemporaryDirectory() as temp_dir:

            output_path = (
                Path(temp_dir)
                / "unified_score.json"
            )

            generator = (
                UnifiedCandidateScoreGenerator(
                    output_path=output_path
                )
            )

            generator.generate(
                candidate_name="Test Candidate",
                role="Test Role",
                ats_score=80,
                screening_score=8,
                hr_interview_score=90
            )

            self.assertTrue(
                output_path.exists()
            )

    def test_saved_data_matches_result(self):

        with tempfile.TemporaryDirectory() as temp_dir:

            output_path = (
                Path(temp_dir)
                / "unified_score.json"
            )

            generator = (
                UnifiedCandidateScoreGenerator(
                    output_path=output_path
                )
            )

            result = generator.generate(
                candidate_name="Test Candidate",
                role="Test Role",
                ats_score=80,
                screening_score=8,
                hr_interview_score=90
            )

            with output_path.open(
                "r",
                encoding="utf-8"
            ) as file:
                saved_data = json.load(file)

            self.assertEqual(
                saved_data,
                result
            )

    def test_role_based_weights_are_stored(self):

        with tempfile.TemporaryDirectory() as temp_dir:

            output_path = (
                Path(temp_dir)
                / "unified_score.json"
            )

            generator = (
                UnifiedCandidateScoreGenerator(
                    output_path=output_path
                )
            )

            result = generator.generate(
                candidate_name="Developer",
                role="Software Developer",
                ats_score=80,
                screening_score=8,
                hr_interview_score=90
            )

            self.assertEqual(
                result["weights"]["ats"],
                0.45
            )

            self.assertEqual(
                result["weights"]["screening"],
                0.20
            )

            self.assertEqual(
                result["weights"]["hr_interview"],
                0.35
            )


if __name__ == "__main__":
    unittest.main()