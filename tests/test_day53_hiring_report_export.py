
import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from scoring.reports import HiringIntelligenceReportGenerator


class TestDay53HiringReportExport(unittest.TestCase):
    def setUp(self):
        self.generator = HiringIntelligenceReportGenerator()

    def test_exports_report_as_json(self):
        report = self.generator.generate_report(
            candidate_id="CAND-053",
            candidate_name="Demo Candidate",
            role="Software Developer",
            ats_summary={"score": 85},
            final_recommendation={
                "decision": "Hold / Review",
                "unified_score": 84.0,
                "human_review_required": True,
            },
        )

        with TemporaryDirectory() as directory:
            path = Path(directory) / "candidate_report.json"
            saved_path = self.generator.export_json(report, path)

            self.assertTrue(saved_path.exists())

            with saved_path.open(encoding="utf-8") as file:
                saved = json.load(file)

            self.assertEqual(saved["report_type"], "hiring_intelligence_report")
            self.assertEqual(
                saved["final_recommendation"]["decision"],
                "Hold / Review",
            )

    def test_creates_output_directory(self):
        report = self.generator.generate_report(
            candidate_id="CAND-053",
            candidate_name="Demo Candidate",
            role="Software Developer",
        )

        with TemporaryDirectory() as directory:
            path = Path(directory) / "nested" / "report.json"
            self.generator.export_json(report, path)
            self.assertTrue(path.exists())

    def test_rejects_non_dictionary_report(self):
        with TemporaryDirectory() as directory:
            with self.assertRaises(TypeError):
                self.generator.export_json("invalid", Path(directory) / "report.json")


if __name__ == "__main__":
    unittest.main()
