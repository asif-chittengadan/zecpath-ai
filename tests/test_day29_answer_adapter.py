import unittest

from screening_ai.answer_understanding_engine import AnswerUnderstandingEngine
from screening_ai.day29_answer_adapter import Day29AnswerAdapter


class TestDay29AnswerAdapter(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.adapter = Day29AnswerAdapter(AnswerUnderstandingEngine())

    def test_on_topic_answer_is_valid(self):
        result = self.adapter.analyze(
            "I have two years of experience in Python.",
            "experience",
            [],
        )

        self.assertTrue(result["valid"])
        self.assertEqual(result["reason"], "")
        self.assertEqual(
            result["semantic_result"]["intent"]["intent_label"],
            "on_topic",
        )

    def test_off_topic_answer_uses_fallback(self):
        result = self.adapter.analyze(
            "I really enjoy watching cricket.",
            "experience",
            [],
        )

        self.assertFalse(result["valid"])
        self.assertEqual(result["reason"], "off_topic")

    def test_vague_answer_uses_fallback(self):
        result = self.adapter.analyze(
            "I have some experience.",
            "experience",
            [],
        )

        self.assertFalse(result["valid"])
        self.assertEqual(result["reason"], "vague")

    def test_confusion_detection_helper(self):
        self.assertTrue(
            self.adapter.is_confused_text("Sorry, what do you mean?")
        )
        self.assertFalse(
            self.adapter.is_confused_text("I have two years of experience.")
        )


if __name__ == "__main__":
    unittest.main()
