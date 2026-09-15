import json
import re
from pathlib import Path


class CommunicationAnalyzer:
    """Analyze communication signals in candidate responses."""

    def __init__(self, rules_path=None):
        if rules_path is None:
            rules_path = (
                Path(__file__).resolve().parent.parent
                / "config"
                / "communication_signal_rules.json"
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

    def analyze(
        self,
        response,
        duration_seconds=None
    ):
        response = self._normalize_response(response)

        word_count = self._count_words(response)

        hesitation = self._detect_signals(
            response,
            self.rules["hesitation"]
        )

        uncertainty = self._detect_phrase_signals(
            response,
            self.rules["uncertainty"]["phrases"]
        )

        contradictions = self._detect_phrase_signals(
            response,
            self.rules["contradiction"]["phrases"]
        )

        pace = self._calculate_pace(
            word_count,
            duration_seconds
        )

        length_category = self._classify_length(
            word_count
        )

        strength_score = self._calculate_strength_score(
            word_count=word_count,
            hesitation_count=hesitation["count"],
            uncertainty_count=uncertainty["count"],
            contradiction_count=contradictions["count"],
            pace=pace
        )

        return {
            "response": response,
            "word_count": word_count,
            "duration_seconds": duration_seconds,
            "response_pace_wpm": pace,
            "response_length": {
                "category": length_category
            },
            "hesitation": hesitation,
            "uncertainty": uncertainty,
            "contradictions": contradictions,
            "communication_strength": {
                "score": strength_score,
                "scale": "0-100"
            }
        }

    @staticmethod
    def _normalize_response(response):
        if response is None:
            return ""

        return " ".join(
            str(response).strip().split()
        )

    @staticmethod
    def _count_words(response):
        if not response:
            return 0

        return len(
            re.findall(
                r"\b[\w']+\b",
                response
            )
        )

    @staticmethod
    def _detect_phrase_signals(response, phrases):
        response_lower = response.lower()

        matched = []

        for phrase in phrases:
            pattern = (
                r"(?<!\w)"
                + re.escape(phrase.lower())
                + r"(?!\w)"
            )

            if re.search(pattern, response_lower):
                matched.append(phrase)

        return {
            "detected": bool(matched),
            "count": len(matched),
            "matches": matched
        }

    @staticmethod
    def _detect_signals(response, signal_rules):
        filler_words = signal_rules.get(
            "filler_words",
            []
        )

        hesitation_phrases = signal_rules.get(
            "hesitation_phrases",
            []
        )

        response_lower = response.lower()

        matched_words = []

        for word in filler_words:
            pattern = (
                r"(?<!\w)"
                + re.escape(word.lower())
                + r"(?!\w)"
            )

            matches = re.findall(
                pattern,
                response_lower
            )

            if matches:
                matched_words.extend(
                    [word] * len(matches)
                )

        phrase_result = CommunicationAnalyzer._detect_phrase_signals(
            response,
            hesitation_phrases
        )

        return {
            "detected": bool(
                matched_words or phrase_result["matches"]
            ),
            "count": (
                len(matched_words)
                + phrase_result["count"]
            ),
            "filler_words": matched_words,
            "phrases": phrase_result["matches"]
        }

    def _calculate_pace(
        self,
        word_count,
        duration_seconds
    ):
        if duration_seconds is None:
            return None

        if duration_seconds <= 0:
            return None

        return round(
            (word_count / duration_seconds) * 60,
            2
        )

    def _classify_length(self, word_count):
        length_rules = self.rules["response_length"]

        if word_count == 0:
            return "empty"

        if word_count <= length_rules["very_short_max_words"]:
            return "very_short"

        if word_count <= length_rules["short_max_words"]:
            return "short"

        if word_count <= length_rules["adequate_max_words"]:
            return "adequate"

        return "long"

    def _calculate_strength_score(
        self,
        word_count,
        hesitation_count,
        uncertainty_count,
        contradiction_count,
        pace
    ):
        if word_count == 0:
            return 0.0

        scoring = self.rules["scoring"]

        score = scoring["base_score"]

        score -= (
            hesitation_count
            * scoring["hesitation_penalty"]
        )

        score -= (
            uncertainty_count
            * scoring["uncertainty_penalty"]
        )

        score -= (
            contradiction_count
            * scoring["contradiction_penalty"]
        )

        length_category = self._classify_length(
            word_count
        )

        if length_category == "very_short":
            score -= scoring[
                "very_short_response_penalty"
            ]

        elif length_category == "short":
            score -= scoring[
                "short_response_penalty"
            ]

        if pace is not None:
            pace_rules = self.rules["response_pace"]

            if pace < pace_rules["slow_wpm_max"]:
                score -= scoring[
                    "slow_pace_penalty"
                ]

            elif pace > pace_rules["fast_wpm_max"]:
                score -= scoring[
                    "fast_pace_penalty"
                ]

        return round(
            max(0.0, min(100.0, score)),
            2
        )