import unittest

from scoring.unified_scoring_engine import (
    UnifiedScoringEngine
)


class TestDay41UnifiedScoringEngine(
    unittest.TestCase
):

    def setUp(self):

        self.engine = UnifiedScoringEngine()

    def test_perfect_scores(self):

        result = self.engine.calculate_score(
            candidate_name="Test Candidate",
            role="Software Developer",
            ats_score=100,
            screening_score=10,
            hr_interview_score=100
        )

        self.assertEqual(
            result["unified_score"],
            100.0
        )

        self.assertEqual(
            result["hiring_fit_percentage"],
            100.0
        )

    def test_zero_scores(self):

        result = self.engine.calculate_score(
            candidate_name="Test Candidate",
            role="Software Developer",
            ats_score=0,
            screening_score=0,
            hr_interview_score=0
        )

        self.assertEqual(
            result["unified_score"],
            0.0
        )

    def test_screening_normalization(self):

        result = self.engine.calculate_score(
            candidate_name="Test Candidate",
            role="Software Developer",
            ats_score=80,
            screening_score=8,
            hr_interview_score=90
        )

        self.assertEqual(
            result["normalized_scores"]["screening"],
            80.0
        )

    def test_weighted_calculation(self):

        result = self.engine.calculate_score(
            candidate_name="Test Candidate",
            role="Test Role",
            ats_score=80,
            screening_score=8,
            hr_interview_score=90
        )

        self.assertEqual(
            result["weighted_scores"]["ats"],
            32.0
        )

        self.assertEqual(
            result["weighted_scores"]["screening"],
            20.0
        )

        self.assertEqual(
            result["weighted_scores"]["hr_interview"],
            31.5
        )

        self.assertEqual(
            result["unified_score"],
            83.5
        )

    def test_candidate_information(self):

        result = self.engine.calculate_score(
            candidate_name="Asif",
            role="Data Scientist",
            ats_score=75,
            screening_score=7,
            hr_interview_score=85
        )

        self.assertEqual(
            result["candidate"],
            "Asif"
        )

        self.assertEqual(
            result["role"],
            "Data Scientist"
        )

    def test_invalid_ats_score(self):

        with self.assertRaises(ValueError):

            self.engine.calculate_score(
                candidate_name="Test",
                role="Developer",
                ats_score=101,
                screening_score=8,
                hr_interview_score=80
            )

    def test_invalid_screening_score(self):

        with self.assertRaises(ValueError):

            self.engine.calculate_score(
                candidate_name="Test",
                role="Developer",
                ats_score=80,
                screening_score=11,
                hr_interview_score=80
            )

    def test_invalid_hr_score(self):

        with self.assertRaises(ValueError):

            self.engine.calculate_score(
                candidate_name="Test",
                role="Developer",
                ats_score=80,
                screening_score=8,
                hr_interview_score=101
            )


if __name__ == "__main__":
    unittest.main()