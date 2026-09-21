import unittest

from interview_ai.hr.follow_up_engine import HRFollowUpEngine


class TestDay33FollowUpEngine(unittest.TestCase):

    def setUp(self):
        self.engine = HRFollowUpEngine()

    def test_empty_response_not_followed_up(self):
        result = self.engine.evaluate(
            "Tell me about yourself.",
            "",
            "self_introduction"
        )

        self.assertFalse(result["eligible"])

    def test_short_response_needs_follow_up(self):
        result = self.engine.evaluate(
            "Tell me about a project.",
            "I built a college project.",
            "career_journey"
        )

        self.assertTrue(result["eligible"])

    def test_detailed_response_does_not_need_follow_up(self):
        result = self.engine.evaluate(
            "Tell me about a project.",
            (
                "I built a college project using Django and Python. "
                "I handled the backend development and database integration "
                "and worked with my teammates to complete the project."
            ),
            "career_journey"
        )

        self.assertFalse(result["eligible"])

    def test_behavioral_response_requires_more_detail(self):
        result = self.engine.evaluate(
            "Tell me about teamwork.",
            "I worked with my team on a project.",
            "teamwork_culture_fit"
        )

        self.assertTrue(result["eligible"])

    def test_follow_up_generation(self):
        follow_up = self.engine.generate_follow_up(
            "Tell me about teamwork.",
            "teamwork_culture_fit"
        )

        self.assertEqual(
            follow_up,
            "What was your specific responsibility in that situation?"
        )

    def test_unknown_category_has_default_follow_up(self):
        follow_up = self.engine.generate_follow_up(
            "Tell me something.",
            "unknown_category"
        )

        self.assertEqual(
            follow_up,
            "Could you please provide a little more detail?"
        )


if __name__ == "__main__":
    unittest.main()