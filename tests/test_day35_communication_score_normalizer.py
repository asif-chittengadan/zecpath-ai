import unittest

from interview_ai.hr.communication_score_normalizer import (
    CommunicationScoreNormalizer
)


class TestDay35CommunicationScoreNormalizer(unittest.TestCase):

    def setUp(self):
        self.normalizer = CommunicationScoreNormalizer()

    def test_normal_score_is_preserved(self):
        result = self.normalizer.normalize(
            80,
            word_count=20
        )

        self.assertEqual(
            result,
            80
        )

    def test_score_never_exceeds_100(self):
        result = self.normalizer.normalize(
            150,
            word_count=20
        )

        self.assertEqual(
            result,
            100
        )

    def test_score_never_goes_below_zero(self):
        result = self.normalizer.normalize(
            -20,
            word_count=20
        )

        self.assertEqual(
            result,
            0
        )

    def test_very_short_answer_is_adjusted(self):
        result = self.normalizer.normalize(
            80,
            word_count=2
        )

        self.assertEqual(
            result,
            40
        )

    def test_three_words_are_not_penalized(self):
        result = self.normalizer.normalize(
            80,
            word_count=3
        )

        self.assertEqual(
            result,
            80
        )

    def test_invalid_score_is_safe(self):
        result = self.normalizer.normalize(
            "invalid",
            word_count=20
        )

        self.assertEqual(
            result,
            0
        )

    def test_invalid_word_count_is_safe(self):
        result = self.normalizer.normalize(
            80,
            word_count="invalid"
        )

        self.assertEqual(
            result,
            80
        )

    def test_empty_answer_score_is_zero(self):
        result = self.normalizer.normalize(
            10,
            word_count=0
        )

        self.assertEqual(
            result,
            0
        )

if __name__ == "__main__":
    unittest.main()