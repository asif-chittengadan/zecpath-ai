import unittest

from interview_ai.hr.repetition_guard import (
    InterviewRepetitionGuard
)


class TestDay34RepetitionGuard(unittest.TestCase):

    def setUp(self):
        self.guard = InterviewRepetitionGuard()

    def test_new_question_is_not_repeated(self):
        result = self.guard.is_repeated(
            "Tell me about your teamwork experience."
        )

        self.assertFalse(result)

    def test_registered_question_is_repeated(self):
        question = (
            "Tell me about your teamwork experience."
        )

        self.guard.register_question(question)

        self.assertTrue(
            self.guard.is_repeated(question)
        )

    def test_case_and_spacing_are_normalized(self):
        self.guard.register_question(
            "Tell me about your teamwork experience."
        )

        result = self.guard.is_repeated(
            "  TELL ME ABOUT YOUR TEAMWORK EXPERIENCE.  "
        )

        self.assertTrue(result)

    def test_alternative_question_is_selected(self):
        original = (
            "Tell me about your teamwork experience."
        )

        alternative = (
            "How do you handle disagreements within a team?"
        )

        self.guard.register_question(original)

        result = self.guard.get_alternative(
            original,
            [
                original,
                alternative
            ]
        )

        self.assertEqual(
            result,
            alternative
        )

    def test_all_used_alternatives_return_none(self):
        first = "Tell me about your teamwork experience."
        second = "How do you handle disagreements within a team?"

        self.guard.register_question(first)
        self.guard.register_question(second)

        result = self.guard.get_alternative(
            first,
            [first, second]
        )

        self.assertIsNone(result)

    def test_clear_history(self):
        question = (
            "Tell me about your career journey."
        )

        self.guard.register_question(question)

        self.assertTrue(
            self.guard.is_repeated(question)
        )

        self.guard.clear()

        self.assertFalse(
            self.guard.is_repeated(question)
        )

    def test_multiple_questions_are_tracked(self):
        questions = [
            "Tell me about your career journey.",
            "What are your strengths?",
            "Where do you see yourself in five years?"
        ]

        for question in questions:
            self.guard.register_question(question)

        for question in questions:
            self.assertTrue(
                self.guard.is_repeated(question)
            )

        self.assertEqual(
            len(self.guard.asked_questions),
            3
        )


if __name__ == "__main__":
    unittest.main()