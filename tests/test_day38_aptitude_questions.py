import json
import unittest
from pathlib import Path


class TestDay38AptitudeQuestions(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        project_root = Path(__file__).resolve().parent.parent

        cls.file_path = (
            project_root
            / "data"
            / "aptitude_questions.json"
        )

        with open(
            cls.file_path,
            "r",
            encoding="utf-8"
        ) as file:
            cls.data = json.load(file)

    def test_question_bank_exists(self):
        self.assertTrue(
            self.file_path.exists()
        )

    def test_question_bank_has_questions(self):
        self.assertIn(
            "questions",
            self.data
        )

        self.assertGreater(
            len(self.data["questions"]),
            0
        )

    def test_question_types_exist(self):
        expected_types = {
            "logical_reasoning",
            "analytical_reasoning",
            "numerical_reasoning",
            "pattern_reasoning",
            "problem_solving"
        }

        self.assertEqual(
            set(self.data["question_types"]),
            expected_types
        )

    def test_each_question_has_required_fields(self):
        required_fields = {
            "question_id",
            "category",
            "question",
            "options",
            "correct_answer",
            "reasoning",
            "difficulty",
            "evaluation_points"
        }

        for question in self.data["questions"]:
            self.assertTrue(
                required_fields.issubset(
                    question.keys()
                )
            )

    def test_question_ids_are_unique(self):
        ids = [
            question["question_id"]
            for question in self.data["questions"]
        ]

        self.assertEqual(
            len(ids),
            len(set(ids))
        )

    def test_each_question_has_options(self):
        for question in self.data["questions"]:
            self.assertGreaterEqual(
                len(question["options"]),
                2
            )

    def test_correct_answer_is_an_option(self):
        for question in self.data["questions"]:
            self.assertIn(
                question["correct_answer"],
                question["options"]
            )

    def test_evaluation_points_exist(self):
        for question in self.data["questions"]:
            self.assertGreater(
                len(question["evaluation_points"]),
                0
            )


if __name__ == "__main__":
    unittest.main()