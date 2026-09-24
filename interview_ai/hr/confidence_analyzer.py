import re

class ConfidenceAnalyzer:
    """
    Detects hesitation and confidence-related patterns
    from an interview response.

    Long pauses are evaluated from optional response metadata
    because actual pause duration cannot be reliably inferred
    from plain text alone.
    """

    UNCERTAINTY_PHRASES = {
        "i think",
        "i guess",
        "maybe",
        "probably",
        "perhaps",
        "not sure",
        "i am not sure",
        "i'm not sure",
        "i don't know",
        "i do not know",
        "as far as i know",
        "i believe",
        "possibly",
        "might be"
    }

    HESITATION_WORDS = {
        "um",
        "uh",
        "erm",
        "hmm"
    }

    def analyze(self, response, metadata=None):
        """
        Analyze a candidate response.

        metadata may contain:
            pause_duration_seconds: total detected pause duration
            long_pause_threshold_seconds: optional threshold
        """

        if response is None:
            response = ""

        response = str(response).strip()

        if metadata is None:
            metadata = {}

        normalized = self._normalize(response)
        words = normalized.split()

        long_pause_detected = self._detect_long_pause(
            metadata
        )

        repeated_words = self._detect_repeated_words(
            words
        )

        uncertainty_phrases = (
            self._detect_uncertainty_phrases(
                normalized
            )
        )

        hesitation_words = (
            self._detect_hesitation_words(
                words
            )
        )

        hesitation_count = (
            len(repeated_words)
            + len(uncertainty_phrases)
            + len(hesitation_words)
            + int(long_pause_detected)
        )

        confidence_indicators = (
            self._build_confidence_indicators(
                response,
                words,
                long_pause_detected,
                repeated_words,
                uncertainty_phrases,
                hesitation_words
            )
        )

        return {
            "long_pause_detected": long_pause_detected,
            "repeated_words": repeated_words,
            "uncertainty_phrases": uncertainty_phrases,
            "hesitation_words": hesitation_words,
            "hesitation_count": hesitation_count,
            "confidence_indicators": confidence_indicators
        }

    def _detect_long_pause(self, metadata):
        pause_duration = metadata.get(
            "pause_duration_seconds"
        )

        if pause_duration is None:
            return False

        try:
            pause_duration = float(
                pause_duration
            )
        except (TypeError, ValueError):
            return False

        threshold = metadata.get(
            "long_pause_threshold_seconds",
            2.0
        )

        try:
            threshold = float(threshold)
        except (TypeError, ValueError):
            threshold = 2.0

        return pause_duration >= threshold

    def _detect_repeated_words(self, words):
        repeated = []
        previous = None

        for word in words:
            if previous is not None and word == previous:
                if word not in repeated:
                    repeated.append(word)

            previous = word

        return repeated

    def _detect_uncertainty_phrases(self, normalized):
        detected = []

        for phrase in self.UNCERTAINTY_PHRASES:
            if phrase in normalized:
                detected.append(phrase)

        return sorted(detected)

    def _detect_hesitation_words(self, words):
        detected = []

        for word in words:
            if word in self.HESITATION_WORDS:
                if word not in detected:
                    detected.append(word)

        return sorted(detected)

    def _build_confidence_indicators(
        self,
        response,
        words,
        long_pause_detected,
        repeated_words,
        uncertainty_phrases,
        hesitation_words
    ):
        indicators = []

        if long_pause_detected:
            indicators.append(
                "long_pause"
            )

        if repeated_words:
            indicators.append(
                "repeated_words"
            )

        if uncertainty_phrases:
            indicators.append(
                "uncertainty_language"
            )

        if hesitation_words:
            indicators.append(
                "hesitation_words"
            )

        if (
            words
            and not indicators
            and len(words) >= 5
        ):
            indicators.append(
                "direct_response"
            )

        return indicators

    @staticmethod
    def _normalize(value):
        value = str(value).strip().lower()

        # Remove punctuation so words such as "um,"
        # are detected as "um".
        value = re.sub(
            r"[^a-z0-9\s']+",
            " ",
            value
        )

        return " ".join(
            value.split()
        )