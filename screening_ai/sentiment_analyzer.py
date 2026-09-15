import json
import re
from pathlib import Path


class SentimentAnalyzer:
    """Analyze positive and negative sentiment in candidate responses."""

    def __init__(self, rules_path=None):
        if rules_path is None:
            rules_path = (
                Path(__file__).resolve().parent.parent
                / "config"
                / "sentiment_rules.json"
            )

        self.rules = self._load_rules(rules_path)

    @staticmethod
    def _load_rules(rules_path):
        with open(
            rules_path,
            "r",
            encoding="utf-8"
        ) as file:
            return json.load(file)

    def analyze(self, response):
        response = self._normalize_response(response)

        if not response:
            return {
                "sentiment": "neutral",
                "score": 0.0,
                "positive_count": 0,
                "negative_count": 0,
                "positive_matches": [],
                "negative_matches": []
            }

        tokens = self._tokenize(response)

        positive_matches = []
        negative_matches = []

        for index, token in enumerate(tokens):
            previous_token = (
                tokens[index - 1]
                if index > 0
                else None
            )

            if token in self.rules["positive_words"]:
                if previous_token in self.rules["negations"]:
                    negative_matches.append(
                        f"not {token}"
                    )
                else:
                    positive_matches.append(token)

            elif token in self.rules["negative_words"]:
                if previous_token in self.rules["negations"]:
                    positive_matches.append(
                        f"not {token}"
                    )
                else:
                    negative_matches.append(token)

        positive_count = len(positive_matches)
        negative_count = len(negative_matches)

        total_sentiment_terms = (
            positive_count + negative_count
        )

        if total_sentiment_terms == 0:
            score = 0.0
            sentiment = "neutral"
        else:
            score = round(
                (
                    (positive_count - negative_count)
                    / total_sentiment_terms
                ) * 100,
                2
            )

            if score > 10:
                sentiment = "positive"
            elif score < -10:
                sentiment = "negative"
            else:
                sentiment = "neutral"

        return {
            "sentiment": sentiment,
            "score": score,
            "positive_count": positive_count,
            "negative_count": negative_count,
            "positive_matches": positive_matches,
            "negative_matches": negative_matches
        }

    @staticmethod
    def _normalize_response(response):
        if response is None:
            return ""

        return " ".join(
            str(response).strip().split()
        ).lower()

    @staticmethod
    def _tokenize(response):
        return re.findall(
            r"\b[\w']+\b",
            response
        )