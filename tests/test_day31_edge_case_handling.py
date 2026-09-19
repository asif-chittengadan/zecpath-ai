import json
from pathlib import Path
import unittest

from screening_ai.response_quality_checker import ResponseQualityChecker
from screening_ai.edge_case_handler import EdgeCaseHandler


BASE_DIR = Path(__file__).resolve().parents[1]


def load_rules():
    with open(
        BASE_DIR / "config" / "edge_case_rules.json",
        "r",
        encoding="utf-8"
    ) as file:
        return json.load(file)


class TestDay31EdgeCaseHandling(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        rules = load_rules()
        cls.checker = ResponseQualityChecker(rules)
        cls.handler = EdgeCaseHandler(rules)

    def test_valid_response(self):
        result = self.checker.check(
            "I have two years of Python experience.",
            {"audio_confidence": 0.95, "noise_score": 0.10}
        )
        self.assertTrue(result["valid"])
        self.assertEqual(result["issues"], [])

    def test_missing_answer(self):
        result = self.checker.check("")
        self.assertIn("missing_answer", result["issues"])

    def test_poor_audio(self):
        result = self.checker.check(
            "I have two years of experience.",
            {"audio_confidence": 0.40}
        )
        self.assertIn("poor_audio", result["issues"])

    def test_background_noise(self):
        result = self.checker.check(
            "I have two years of experience.",
            {"noise_score": 0.90}
        )
        self.assertIn("background_noise", result["issues"])

    def test_explicit_language_mixing(self):
        result = self.checker.check(
            "I have two years experience.",
            {"language_mixed": True}
        )
        self.assertIn("language_mixing", result["issues"])

    def test_retry_action(self):
        quality = {"valid": False, "issues": ["poor_audio"], "answer": ""}
        result = self.handler.handle(quality, {})
        self.assertEqual(result["action"], "retry")
        self.assertFalse(result["terminal"])
        self.assertEqual(result["retry_count"]["poor_audio"], 1)

    def test_clarification_action(self):
        quality = {"valid": False, "issues": ["language_mixing"], "answer": ""}
        result = self.handler.handle(quality, {})
        self.assertEqual(result["action"], "clarify")

    def test_retry_limit_safe_fallback(self):
        quality = {"valid": False, "issues": ["missing_answer"], "answer": ""}
        result = self.handler.handle(quality, {"missing_answer": 2})
        self.assertEqual(result["action"], "safe_fallback")
        self.assertTrue(result["terminal"])


if __name__ == "__main__":
    unittest.main()
