
import json
import tempfile
import unittest
from pathlib import Path

from scoring.unified_candidate_score_generator import (
    UnifiedCandidateScoreGenerator,
)


class TestUnifiedCandidateScoreGenerator(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.output_path = Path(self.temp_dir.name) / "score.json"
        self.generator = UnifiedCandidateScoreGenerator(
            output_path=self.output_path
        )

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_generates_five_round_score(self):
        result = self.generator.generate(
            candidate_name="Test Candidate",
            role="Software Developer",
            ats_score=80,
            screening_score=8,
            hr_interview_score=90,
            technical_interview_score=85,
            machine_test_score=95,
            candidate_id="CAND-001",
        )

        self.assertEqual(result["round_count"], 5)
        self.assertEqual(result["unified_score"], 86.75)
        self.assertEqual(result["candidate_id"], "CAND-001")

    def test_saves_valid_json(self):
        self.generator.generate(
            candidate_name="Test Candidate",
            role="Software Developer",
            ats_score=80,
            screening_score=8,
            hr_interview_score=90,
            technical_interview_score=85,
            machine_test_score=95,
            candidate_id="CAND-001",
        )

        with self.output_path.open(encoding="utf-8") as file:
            saved = json.load(file)

        self.assertEqual(saved["round_count"], 5)
        self.assertEqual(saved["unified_score"], 86.75)

    def test_legacy_three_round_generation(self):
        result = self.generator.generate(
            candidate_name="Legacy Candidate",
            role="Software Developer",
            ats_score=80,
            screening_score=8,
            hr_interview_score=90,
            candidate_id="CAND-002",
        )

        self.assertEqual(result["round_count"], 3)
        self.assertEqual(result["unified_score"], 83.5)


if __name__ == "__main__":
    unittest.main()
