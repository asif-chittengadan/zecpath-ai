import unittest

from interview_ai.hr.dynamic_conversation_state import (
    DynamicConversationState
)


class TestDay34DynamicConversationState(unittest.TestCase):

    def setUp(self):
        self.state = DynamicConversationState()

    def test_initial_state(self):
        self.assertEqual(
            self.state.difficulty_level,
            1
        )

        self.assertEqual(
            self.state.questions_asked,
            0
        )

        self.assertEqual(
            self.state.follow_up_count,
            0
        )

    def test_set_question(self):
        self.state.set_question(
            "Q001",
            "Tell me about yourself."
        )

        self.assertEqual(
            self.state.current_question_id,
            "Q001"
        )

        self.assertEqual(
            self.state.current_question,
            "Tell me about yourself."
        )

        self.assertEqual(
            self.state.questions_asked,
            1
        )

    def test_record_response(self):
        self.state.set_question(
            "Q001",
            "Tell me about yourself."
        )

        self.state.record_response(
            "I completed my degree in IT and worked on projects.",
            "complete",
            2
        )

        self.assertEqual(
            self.state.last_classification,
            "complete"
        )

        self.assertEqual(
            self.state.difficulty_level,
            2
        )

        self.assertEqual(
            len(self.state.conversation_history),
            1
        )

    def test_record_follow_up(self):
        self.state.set_question(
            "Q001",
            "Tell me about teamwork."
        )

        self.state.record_follow_up(
            "deepening",
            "What was your specific responsibility?"
        )

        self.assertEqual(
            self.state.last_follow_up_type,
            "deepening"
        )

        self.assertEqual(
            self.state.follow_up_count,
            1
        )

        self.assertTrue(
            self.state.was_question_asked(
                "What was your specific responsibility?"
            )
        )

    def test_question_tracking(self):
        question = "Tell me about your career journey."

        self.state.set_question(
            "Q001",
            question
        )

        self.assertTrue(
            self.state.was_question_asked(question)
        )

    def test_duplicate_question_is_not_added_twice(self):
        question = "What are your strengths?"

        self.state.set_question(
            "Q001",
            question
        )

        self.state.set_question(
            "Q002",
            question
        )

        self.assertEqual(
            len(self.state.asked_questions),
            1
        )

        self.assertEqual(
            self.state.questions_asked,
            2
        )

    def test_get_state(self):
        self.state.set_question(
            "Q001",
            "Tell me about yourself."
        )

        self.state.record_response(
            "I completed my degree in IT.",
            "complete",
            2
        )

        result = self.state.get_state()

        self.assertEqual(
            result["current_question_id"],
            "Q001"
        )

        self.assertEqual(
            result["last_classification"],
            "complete"
        )

        self.assertIn(
            "conversation_history",
            result
        )

    def test_reset(self):
        self.state.set_question(
            "Q001",
            "Tell me about yourself."
        )

        self.state.record_response(
            "I completed my degree in IT.",
            "complete",
            2
        )

        self.state.record_follow_up(
            "example_based",
            "Could you give me an example?"
        )

        self.state.reset()

        self.assertIsNone(
            self.state.current_question
        )

        self.assertEqual(
            self.state.questions_asked,
            0
        )

        self.assertEqual(
            self.state.follow_up_count,
            0
        )

        self.assertEqual(
            self.state.difficulty_level,
            1
        )

        self.assertEqual(
            len(self.state.conversation_history),
            0
        )


if __name__ == "__main__":
    unittest.main()