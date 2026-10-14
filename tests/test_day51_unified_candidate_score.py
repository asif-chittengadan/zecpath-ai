
import unittest

from scoring.unified_candidate_score import UnifiedCandidateScore


class TestUnifiedCandidateScore(unittest.TestCase):
    def setUp(self):
        self.score = UnifiedCandidateScore(
            candidate_id="CAND-001",
            candidate_name="Test Candidate",
            role="Software Developer",
            round_scores={
                "ats": 80,
                "screening": 8,
                "hr_interview": 90,
                "technical_interview": 85,
                "machine_test": 95,
            },
            normalized_scores={
                "ats": 80,
                "screening": 80,
                "hr_interview": 90,
                "technical_interview": 85,
                "machine_test": 95,
            },
            weights={
                "ats": 0.20,
                "screening": 0.10,
                "hr_interview": 0.15,
                "technical_interview": 0.30,
                "machine_test": 0.25,
            },
            weighted_scores={
                "ats": 16,
                "screening": 8,
                "hr_interview": 13.5,
                "technical_interview": 25.5,
                "machine_test": 23.75,
            },
            unified_score=86.75,
        )

    def test_serialization(self):
        result = self.score.to_dict()
        self.assertEqual(result["candidate_id"], "CAND-001")
        self.assertEqual(result["round_count"], 5)
        self.assertEqual(result["hiring_fit_percentage"], 86.75)

    def test_human_review_required(self):
        self.assertTrue(self.score.to_dict()["human_review_required"])

    def test_invalid_score_rejected(self):
        with self.assertRaises(ValueError):
            UnifiedCandidateScore(
                "C1", "Candidate", "Developer",
                {}, {}, {}, {}, 101
            )


if __name__ == "__main__":
    unittest.main()
