import json
import unittest
from pathlib import Path


class TestDay38SituationalScenarios(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        project_root = Path(__file__).resolve().parent.parent

        cls.file_path = (
            project_root
            / "data"
            / "situational_scenarios.json"
        )

        with open(
            cls.file_path,
            "r",
            encoding="utf-8"
        ) as file:
            cls.data = json.load(file)

    def test_scenario_bank_exists(self):
        self.assertTrue(
            self.file_path.exists()
        )

    def test_scenarios_exist(self):
        self.assertIn(
            "scenarios",
            self.data
        )

        self.assertGreater(
            len(self.data["scenarios"]),
            0
        )

    def test_scenario_types_exist(self):
        expected_types = {
            "incident_handling",
            "task_prioritization",
            "team_conflict",
            "deadline_management",
            "technical_problem_solving",
            "decision_making"
        }

        self.assertEqual(
            set(self.data["scenario_types"]),
            expected_types
        )

    def test_each_scenario_has_required_fields(self):
        required_fields = {
            "scenario_id",
            "category",
            "scenario",
            "options",
            "ideal_answer",
            "evaluation_points",
            "difficulty"
        }

        for scenario in self.data["scenarios"]:
            self.assertTrue(
                required_fields.issubset(
                    scenario.keys()
                )
            )

    def test_scenario_ids_are_unique(self):
        ids = [
            scenario["scenario_id"]
            for scenario in self.data["scenarios"]
        ]

        self.assertEqual(
            len(ids),
            len(set(ids))
        )

    def test_each_scenario_has_multiple_options(self):
        for scenario in self.data["scenarios"]:
            self.assertGreaterEqual(
                len(scenario["options"]),
                2
            )

    def test_ideal_answer_is_present(self):
        for scenario in self.data["scenarios"]:
            self.assertTrue(
                scenario["ideal_answer"].strip()
            )

    def test_evaluation_points_exist(self):
        for scenario in self.data["scenarios"]:
            self.assertGreater(
                len(scenario["evaluation_points"]),
                0
            )


if __name__ == "__main__":
    unittest.main()