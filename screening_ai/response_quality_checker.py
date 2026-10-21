import math
import re
from collections.abc import Mapping


class ResponseQualityChecker:
    """Detect response-quality problems before the answer enters screening analysis."""

    def __init__(self, rules):
        self.rules = rules
        self.thresholds = rules.get("quality_thresholds", {})
        self.language_markers = {
            item.lower() for item in rules.get("language_markers", [])
        }

    def check(self, answer, metadata=None):
        metadata = metadata if isinstance(metadata, Mapping) else {}
        text = "" if answer is None else str(answer).strip()

        issues = []

        if self._is_missing(text):
            issues.append("missing_answer")

        if self._is_poor_audio(metadata):
            issues.append("poor_audio")

        if self._has_background_noise(metadata):
            issues.append("background_noise")

        if self._is_language_mixed(text, metadata):
            issues.append("language_mixing")

        return {
            "valid": not issues,
            "issues": issues,
            "answer": text
        }

    def _is_missing(self, text):
        minimum_length = int(
            self.thresholds.get("minimum_transcript_length", 2)
        )
        return not text or len(text) < minimum_length

    def _is_poor_audio(self, metadata):
        confidence = metadata.get("audio_confidence")
        if confidence is None:
            return False
        confidence = self._bounded_metric(confidence)
        if confidence is None:
            return True
        return confidence < float(
            self.thresholds.get("minimum_audio_confidence", 0.55)
        )

    def _has_background_noise(self, metadata):
        noise_score = metadata.get("noise_score")
        if noise_score is None:
            return False
        noise_score = self._bounded_metric(noise_score)
        if noise_score is None:
            return True
        return noise_score > float(
            self.thresholds.get("maximum_noise_score", 0.70)
        )

    @staticmethod
    def _bounded_metric(value):
        if isinstance(value, bool):
            return None
        try:
            number = float(value)
        except (TypeError, ValueError, OverflowError):
            return None
        if not math.isfinite(number) or not 0.0 <= number <= 1.0:
            return None
        return number

    def _is_language_mixed(self, text, metadata):
        if metadata.get("language_mixed") is True:
            return True

        latin_words = re.findall(r"[A-Za-z]+", text.lower())
        if len(latin_words) < 2:
            return False

        marker_count = sum(
            1 for word in latin_words if word in self.language_markers
        )
        return marker_count >= 1 and len(latin_words) >= 3
