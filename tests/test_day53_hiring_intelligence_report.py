
import unittest

from scoring.reports import HiringIntelligenceReportGenerator


class TestDay53HiringIntelligenceReport(unittest.TestCase):

    def setUp(self):
        self.generator = HiringIntelligenceReportGenerator()

    def test_generates_report_with_all_sections(self):
        result = self.generator.generate_report(
            candidate_id="CAND-053",
            candidate_name="Demo Candidate",
            role="Software Developer",
            ats_summary={"score": 85},
            screening_results={"score": 8},
            hr_insights={"communication_score": 80},
            technical_performance={"score": 90},
            behavioral_flags={"risk_flags": ["Manual review"]},
            final_recommendation={"decision": "Hold / Review"},
        )

        self.assertEqual(
            result["report_type"],
            "hiring_intelligence_report",
        )

        self.assertEqual(
            set(result["evaluation"].keys()),
            {
                "ats_summary",
                "screening_results",
                "hr_insights",
                "technical_performance",
                "behavioral_flags",
            },
        )

        self.assertTrue(
            all(result["data_completeness"].values())
        )

    def test_collects_strengths_weaknesses_and_risks(self):
        result = self.generator.generate_report(
            candidate_id="CAND-053",
            candidate_name="Demo Candidate",
            role="Software Developer",
            ats_summary={
                "strengths": ["Strong skill match"],
            },
            screening_results={
                "weaknesses": ["Needs SQL practice"],
            },
            behavioral_flags={
                "risk_flags": ["Manual review requested"],
            },
        )

        self.assertIn(
            "Strong skill match",
            result["summary"]["strengths"],
        )

        self.assertIn(
            "Needs SQL practice",
            result["summary"]["weaknesses"],
        )

        self.assertIn(
            "Manual review requested",
            result["summary"]["risk_indicators"],
        )

    def test_missing_sections_are_not_treated_as_zero(self):
        result = self.generator.generate_report(
            candidate_id="CAND-053",
            candidate_name="Demo Candidate",
            role="Software Developer",
            ats_summary={"score": 75},
        )

        self.assertTrue(
            result["data_completeness"]["ats_summary"]
        )

        self.assertFalse(
            result["data_completeness"]["screening_results"]
        )

        self.assertEqual(
            result["evaluation"]["screening_results"],
            {},
        )

        self.assertIn(
            "Missing sections are not interpreted as zero scores.",
            result["limitations"],
        )

    def test_preserves_final_recommendation(self):
        recommendation = {
            "decision": "Hold / Review",
            "unified_score": 84.0,
            "confidence_score": 60.0,
            "reasons": ["Manual review required"],
            "human_review_required": True,
        }

        result = self.generator.generate_report(
            candidate_id="CAND-053",
            candidate_name="Demo Candidate",
            role="Software Developer",
            final_recommendation=recommendation,
        )

        self.assertEqual(
            result["final_recommendation"]["decision"],
            "Hold / Review",
        )

        self.assertEqual(
            result["final_recommendation"]["unified_score"],
            84.0,
        )

        self.assertTrue(
            result["final_recommendation"]["human_review_required"]
        )

    def test_unknown_candidate_name_uses_fallback(self):
        result = self.generator.generate_report(
            candidate_id="CAND-053",
            candidate_name=None,
            role=None,
        )

        self.assertEqual(
            result["candidate"]["candidate_name"],
            "Unknown",
        )

        self.assertEqual(
            result["candidate"]["role"],
            "Unknown",
        )
    
    def test_recruiter_summary_explains_existing_decision(self):
        result = self.generator.generate_report(
            candidate_id="CAND-053",
            candidate_name="Demo Candidate",
            role="Software Developer",
            ats_summary={"strengths": ["Strong skill match"]},
            final_recommendation={
                "decision": "Hold / Review",
                "reasons": ["Manual review required"],
                "human_review_required": True,
            },
        )

        summary = result["recruiter_summary"]

        self.assertEqual(summary["decision"], "Hold / Review")
        self.assertIn(
            "Manual review required",
            summary["explanation"],
        )
        self.assertTrue(summary["human_review_required"])
        self.assertGreaterEqual(len(summary["missing_sections"]), 1)

    def test_report_does_not_change_recommendation_score(self):
        result = self.generator.generate_report(
            candidate_id="CAND-053",
            candidate_name="Demo Candidate",
            role="Software Developer",
            final_recommendation={
                "decision": "Selected",
                "unified_score": 90.0,
                "confidence_score": 87.4,
                "human_review_required": False,
            },
        )

        self.assertEqual(
            result["final_recommendation"]["unified_score"],
            90.0,
        )
        self.assertEqual(
            result["recruiter_summary"]["decision"],
            "Selected",
        )

    def test_risk_indicators_are_explained_without_accusations(self):
        result = self.generator.generate_report(
            candidate_id="CAND-053",
            candidate_name="Demo Candidate",
            role="Software Developer",
            behavioral_flags={
                "risk_flags": ["Manual review requested"],
            },
        )

        summary = result["recruiter_summary"]

        self.assertIn(
            "Manual review requested",
            result["summary"]["risk_indicators"],
        )
        self.assertTrue(
            any("risk indicators require review" in item
                for item in summary["explanation"])
        )
        self.assertTrue(
            any("not proof of misconduct" in item
                for item in result["limitations"])
        )
    
    def test_missing_candidate_id_is_preserved(self):
        result = self.generator.generate_report(
            candidate_id=None,
            candidate_name="Demo Candidate",
            role="Software Developer",
        )

        self.assertIsNone(result["candidate"]["candidate_id"])

    def test_non_dictionary_evaluation_data_is_handled(self):
        result = self.generator.generate_report(
            candidate_id="CAND-053",
            candidate_name="Demo Candidate",
            role="Software Developer",
            ats_summary="invalid data",
            screening_results=None,
        )

        self.assertEqual(result["evaluation"]["ats_summary"], {})
        self.assertEqual(result["evaluation"]["screening_results"], {})
        self.assertFalse(result["data_completeness"]["ats_summary"])

    def test_duplicate_summary_items_are_removed(self):
        result = self.generator.generate_report(
            candidate_id="CAND-053",
            candidate_name="Demo Candidate",
            role="Software Developer",
            ats_summary={"strengths": ["Strong Python", "Strong Python"]},
            hr_insights={"strengths": ["Strong Python"]},
            behavioral_flags={"risk_flags": ["Manual review", "Manual review"]},
        )

        self.assertEqual(
            result["summary"]["strengths"],
            ["Strong Python"],
        )
        self.assertEqual(
            result["summary"]["risk_indicators"],
            ["Manual review"],
        )

    def test_missing_recommendation_defaults_to_review(self):
        result = self.generator.generate_report(
            candidate_id="CAND-053",
            candidate_name="Demo Candidate",
            role="Software Developer",
        )

        self.assertEqual(
            result["final_recommendation"]["decision"],
            "Not available",
        )
        self.assertTrue(
            result["final_recommendation"]["human_review_required"]
        )




    def test_markdown_scores_show_scale_and_confidence_is_qualified(self):
        report = self.generator.generate_report(
            candidate_id="CAND-053",
            candidate_name="Demo Candidate",
            role="Software Developer",
            final_recommendation={
                "decision": "Hold / Review",
                "unified_score": 81.3,
                "confidence_score": 60.0,
                "human_review_required": True,
            },
        )

        markdown = self.generator.render_markdown(report)

        self.assertIn("- **Unified score:** 81.30 / 100", markdown)
        self.assertIn("- **Decision confidence:** 60.00 / 100", markdown)
        self.assertIn(
            "Decision confidence is a heuristic indicator, not a probability "
            "of candidate success.",
            markdown,
        )


if __name__ == "__main__":
    unittest.main()
