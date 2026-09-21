import unittest

from interview_ai.hr.question_generator import HRQuestionGenerator


class TestDay33QuestionGenerator(unittest.TestCase):

    def setUp(self):
        self.generator = HRQuestionGenerator(
            "data/hr_question_bank.json"
        )

    def test_all_required_categories_exist(self):
        expected = {
            "self_introduction",
            "career_journey",
            "strengths_weaknesses",
            "teamwork_culture_fit",
            "career_goals",
            "availability_commitment",
        }

        self.assertEqual(
            expected,
            set(self.generator.question_bank["categories"].keys())
        )

    def test_fresher_technical_questions(self):
        questions = self.generator.generate(
            "self introduction",
            "Fresher",
            "Technical"
        )

        self.assertGreaterEqual(len(questions), 1)

    def test_experienced_non_technical_questions(self):
        questions = self.generator.generate(
            "career goals",
            "Experienced",
            "Non-technical"
        )

        self.assertGreaterEqual(len(questions), 1)

    def test_invalid_category(self):
        with self.assertRaises(ValueError):
            self.generator.generate(
                "unknown_category",
                "fresher",
                "technical"
            )

    def test_invalid_candidate_type(self):
        with self.assertRaises(ValueError):
            self.generator.generate(
                "career_goals",
                "intern",
                "technical"
            )


if __name__ == "__main__":
    unittest.main()