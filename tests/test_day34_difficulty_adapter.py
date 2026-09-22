import unittest

from interview_ai.hr.difficulty_adapter import (
    InterviewDifficultyAdapter
)


class TestDay34DifficultyAdapter(unittest.TestCase):

    def setUp(self):
        self.adapter = InterviewDifficultyAdapter()

    def test_incomplete_gets_level_one(self):
        level = self.adapter.determine_level(
            "incomplete"
        )

        self.assertEqual(
            level,
            1
        )

    def test_vague_gets_level_one(self):
        level = self.adapter.determine_level(
            "vague"
        )

        self.assertEqual(
            level,
            1
        )

    def test_complete_gets_level_two(self):
        level = self.adapter.determine_level(
            "complete"
        )

        self.assertEqual(
            level,
            2
        )

    def test_confident_gets_level_three(self):
        level = self.adapter.determine_level(
            "confident"
        )

        self.assertEqual(
            level,
            3
        )

    def test_complete_increases_from_level_one(self):
        result = self.adapter.should_increase_difficulty(
            1,
            "complete"
        )

        self.assertTrue(result)

    def test_confident_increases_from_level_two(self):
        result = self.adapter.should_increase_difficulty(
            2,
            "confident"
        )

        self.assertTrue(result)

    def test_incomplete_does_not_increase_from_level_two(self):
        result = self.adapter.should_increase_difficulty(
            2,
            "incomplete"
        )

        self.assertFalse(result)

    def test_strategy_for_each_level(self):
        self.assertEqual(
            self.adapter.get_strategy(1),
            "clarification"
        )

        self.assertEqual(
            self.adapter.get_strategy(2),
            "deepening"
        )

        self.assertEqual(
            self.adapter.get_strategy(3),
            "scenario_based"
        )

    def test_unknown_classification_is_safe(self):
        level = self.adapter.determine_level(
            "unknown"
        )

        self.assertEqual(
            level,
            1
        )

    def test_reset(self):
        self.adapter.determine_level("confident")

        self.assertEqual(
            self.adapter.current_level,
            3
        )

        self.adapter.reset()

        self.assertEqual(
            self.adapter.current_level,
            1
        )


if __name__ == "__main__":
    unittest.main()