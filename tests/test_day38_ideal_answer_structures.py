import json
import unittest
from pathlib import Path


class TestDay38IdealAnswerStructures(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        project_root = Path(__file__).resolve().parent.parent

        cls.file_path = (
            project_root
            / "data"
            / "ideal_answer_structures.json"
        )

        with open(
            cls.file_path,
            "r",
            encoding="utf-8"
        ) as file:
            cls.data = json.load(file)

    def test_structure_file_exists(self):
        self.assertTrue(
            self.file_path.exists()
        )

    def test_structures_exist(self):
        self.assertIn(
            "structures",
            self.data
        )

        self.assertGreater(
            len(self.data["structures"]),
            0
        )

    def test_structure_types_exist(self):
        expected_types = {
            "logical_reasoning",
            "analytical_reasoning",
            "numerical_reasoning",
            "pattern_reasoning",
            "problem_solving",
            "situational_judgment"
        }

        self.assertEqual(
            set(self.data["structure_types"]),
            expected_types
        )

    def test_each_structure_has_required_fields(self):
        required_fields = {
            "structure_id",
            "category",
            "steps",
            "key_indicators"
        }

        for structure in self.data["structures"]:
            self.assertTrue(
                required_fields.issubset(
                    structure.keys()
                )
            )

    def test_structure_ids_are_unique(self):
        ids = [
            structure["structure_id"]
            for structure in self.data["structures"]
        ]

        self.assertEqual(
            len(ids),
            len(set(ids))
        )

    def test_each_structure_has_multiple_steps(self):
        for structure in self.data["structures"]:
            self.assertGreaterEqual(
                len(structure["steps"]),
                3
            )

    def test_each_structure_has_indicators(self):
        for structure in self.data["structures"]:
            self.assertGreater(
                len(structure["key_indicators"]),
                0
            )

    def test_all_categories_are_supported(self):
        supported = set(
            self.data["structure_types"]
        )

        for structure in self.data["structures"]:
            self.assertIn(
                structure["category"],
                supported
            )


if __name__ == "__main__":
    unittest.main()