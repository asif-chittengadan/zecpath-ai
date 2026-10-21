import unittest

from interview_ai.hr.unified_scoring_config import (
    UnifiedScoringConfig
)

from scoring.unified_scoring_engine import (
    UnifiedScoringEngine
)


class TestDay41RoleBasedScoring(
    unittest.TestCase
):

    def setUp(self):
        self.config = UnifiedScoringConfig(
            "config/unified_scoring_rules.json"
        )

        self.engine = UnifiedScoringEngine()

    def test_software_developer_weights(self):

        weights = self.config.get_role_weights(
            "Software Developer"
        )

        self.assertEqual(
            weights["ats"],
            0.45
        )

        self.assertEqual(
            weights["screening"],
            0.20
        )

        self.assertEqual(
            weights["hr_interview"],
            0.35
        )

    def test_sales_executive_weights(self):

        weights = self.config.get_role_weights(
            "Sales Executive"
        )

        self.assertEqual(
            weights["ats"],
            0.30
        )

        self.assertEqual(
            weights["screening"],
            0.30
        )

        self.assertEqual(
            weights["hr_interview"],
            0.40
        )

    def test_unknown_role_uses_default(self):

        weights = self.config.get_role_weights(
            "Unknown Role"
        )

        self.assertEqual(
            weights,
            {
                "ats": 0.40,
                "screening": 0.25,
                "hr_interview": 0.35
            }
        )

    def test_role_weights_total_one(self):

        for role in [
            "default",
            "software_developer",
            "data_scientist",
            "sales_executive",
            "hr_manager"
        ]:

            weights = self.config.get_role_weights(
                role
            )

            self.assertEqual(
                round(sum(weights.values()), 6),
                1.0
            )

    def test_legacy_default_weights_come_from_shared_config(self):
        for name, expected in {
            "ats": 0.40,
            "screening": 0.25,
            "hr_interview": 0.35,
        }.items():
            with self.subTest(round=name):
                self.assertEqual(
                    self.config.get_weight(name),
                    expected,
                )

    def test_engine_uses_role_weights(self):

        result = self.engine.calculate_score(
            candidate_name="Test Candidate",
            role="Software Developer",
            ats_score=80,
            screening_score=80,
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

        self.assertEqual(
            result["weighted_scores"]["ats"],
            36.0
        )

        self.assertEqual(
            result["weighted_scores"]["screening"],
            16.0
        )

        self.assertEqual(
            result["weighted_scores"]["hr_interview"],
            31.5
        )

        self.assertEqual(
            result["unified_score"],
            83.5
        )

    def test_engine_uses_configured_legacy_weights_for_each_role(self):
        for role in (
            "Unknown Role",
            "Software Developer",
            "Data Scientist",
            "Sales Executive",
            "HR Manager",
        ):
            with self.subTest(role=role):
                result = self.engine.calculate_score(
                    candidate_name="Test Candidate",
                    role=role,
                    ats_score=80,
                    screening_score=80,
                    hr_interview_score=90,
                )

                self.assertEqual(
                    result["weights"],
                    self.config.get_role_weights(role),
                )


if __name__ == "__main__":
    unittest.main()
