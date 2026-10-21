
import unittest

from scoring.unified_scoring_engine import UnifiedScoringEngine


class TestCrossRoundAggregation(unittest.TestCase):
    def setUp(self):
        self.engine = UnifiedScoringEngine()

    def test_five_round_aggregation(self):
        result = self.engine.calculate_score(
            candidate_name="Test Candidate",
            role="Software Developer",
            ats_score=80,
            screening_score=80,
            hr_interview_score=90,
            technical_interview_score=85,
            machine_test_score=95,
        )

        self.assertEqual(result["round_count"], 5)
        self.assertEqual(result["normalized_scores"]["screening"], 80.0)
        self.assertAlmostEqual(result["unified_score"], 86.75)
        self.assertEqual(result["hiring_fit_percentage"], result["unified_score"])

    def test_perfect_five_round_scores(self):
        result = self.engine.calculate_score(
            candidate_name="Test Candidate",
            role="Software Developer",
            ats_score=100,
            screening_score=100,
            hr_interview_score=100,
            technical_interview_score=100,
            machine_test_score=100,
        )

        self.assertEqual(result["unified_score"], 100.0)

    def test_zero_five_round_scores(self):
        result = self.engine.calculate_score(
            candidate_name="Test Candidate",
            role="Software Developer",
            ats_score=0,
            screening_score=0,
            hr_interview_score=0,
            technical_interview_score=0,
            machine_test_score=0,
        )

        self.assertEqual(result["unified_score"], 0.0)

    def test_missing_required_score_is_rejected(self):
        with self.assertRaises(ValueError):
            self.engine.calculate_score(
                candidate_name="Test Candidate",
                role="Software Developer",
                ats_score=80,
                screening_score=None,
                hr_interview_score=90,
                technical_interview_score=85,
                machine_test_score=95,
            )

    def test_invalid_technical_score_is_rejected(self):
        with self.assertRaises(ValueError):
            self.engine.calculate_score(
                candidate_name="Test Candidate",
                role="Software Developer",
                ats_score=80,
                screening_score=80,
                hr_interview_score=90,
                technical_interview_score=101,
                machine_test_score=95,
            )

    def test_invalid_machine_test_score_is_rejected(self):
        with self.assertRaises(ValueError):
            self.engine.calculate_score(
                candidate_name="Test Candidate",
                role="Software Developer",
                ats_score=80,
                screening_score=80,
                hr_interview_score=90,
                technical_interview_score=85,
                machine_test_score=-1,
            )


if __name__ == "__main__":
    unittest.main()
