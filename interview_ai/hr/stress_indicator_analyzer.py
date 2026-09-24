class StressIndicatorAnalyzer:
    """
    Detects textual and metadata-based stress indicators.

    This is a rule-based behavioral signal detector.
    It is not a medical or psychological assessment.
    """

    STRESS_WORDS = {
        "nervous",
        "worried",
        "stressed",
        "stress",
        "afraid",
        "scared",
        "anxious",
        "anxiety",
        "confused",
        "frustrated",
        "overwhelmed",
        "pressure",
        "difficult",
        "hard",
        "uncertain"
    }

    HESITATION_WORDS = {
        "um",
        "uh",
        "erm",
        "hmm"
    }

    def analyze(self, response, metadata=None):
        if response is None:
            response = ""

        response = str(response).strip()

        if metadata is None:
            metadata = {}

        normalized = self._normalize(
            response
        )

        words = normalized.split()

        stress_words = self._detect_stress_words(
            words
        )

        hesitation_words = (
            self._detect_hesitation_words(
                words
            )
        )

        repeated_words = (
            self._detect_repeated_words(
                words
            )
        )

        long_pause = (
            self._detect_long_pause(
                metadata
            )
        )

        stress_indicators = []

        if stress_words:
            stress_indicators.append(
                "stress_language"
            )

        if hesitation_words:
            stress_indicators.append(
                "hesitation"
            )

        if repeated_words:
            stress_indicators.append(
                "repeated_words"
            )

        if long_pause:
            stress_indicators.append(
                "long_pause"
            )

        stress_count = (
            len(stress_words)
            + len(hesitation_words)
            + len(repeated_words)
            + int(long_pause)
        )

        stress_level = self._classify_stress(
            stress_count
        )

        return {
            "stress_indicators": stress_indicators,
            "stress_words": stress_words,
            "hesitation_words": hesitation_words,
            "repeated_words": repeated_words,
            "long_pause_detected": long_pause,
            "stress_count": stress_count,
            "stress_level": stress_level
        }

    def _detect_stress_words(self, words):
        detected = []

        for word in words:
            if (
                word in self.STRESS_WORDS
                and word not in detected
            ):
                detected.append(word)

        return sorted(detected)

    def _detect_hesitation_words(self, words):
        detected = []

        for word in words:
            if (
                word in self.HESITATION_WORDS
                and word not in detected
            ):
                detected.append(word)

        return sorted(detected)

    def _detect_repeated_words(self, words):
        detected = []

        previous = None

        for word in words:
            if (
                previous is not None
                and word == previous
                and word not in detected
            ):
                detected.append(word)

            previous = word

        return detected

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
            threshold = float(
                threshold
            )
        except (TypeError, ValueError):
            threshold = 2.0

        return pause_duration >= threshold

    def _classify_stress(self, stress_count):
        if stress_count == 0:
            return "low"

        if stress_count <= 2:
            return "moderate"

        return "high"

    @staticmethod
    def _normalize(value):
        value = str(value).strip().lower()

        punctuation = ",.!?;:()[]{}\""

        for character in punctuation:
            value = value.replace(
                character,
                " "
            )

        return " ".join(
            value.split()
        )