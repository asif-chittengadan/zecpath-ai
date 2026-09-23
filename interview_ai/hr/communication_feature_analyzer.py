class CommunicationFeatureAnalyzer:
    """
    Analyzes measurable communication features from an HR interview answer.

    Features:
        - fluency
        - grammar quality
        - vocabulary range
        - clarity
        - filler words
        - answer structure
    """

    FILLER_WORDS = {
        "um",
        "uh",
        "erm",
        "hmm",
        "like",
        "basically",
        "actually",
        "you know",
        "i mean",
        "sort of",
        "kind of"
    }

    TRANSITION_WORDS = {
        "first",
        "second",
        "then",
        "next",
        "because",
        "therefore",
        "however",
        "finally",
        "for example",
        "also",
        "although"
    }

    def analyze(self, answer):
        """
        Analyze communication features.

        Returns a dictionary containing measurable feature values.
        """

        normalized = self._normalize(answer)

        if not normalized:
            return {
                "fluency": 0,
                "grammar_quality": 0,
                "vocabulary_range": 0,
                "clarity": 0,
                "filler_words": [],
                "filler_word_count": 0,
                "answer_structure": 0,
                "word_count": 0,
                "sentence_count": 0
            }

        words = normalized.split()
        sentences = self._split_sentences(answer)

        filler_words = self._detect_filler_words(normalized)

        return {
            "fluency": self._measure_fluency(
                words,
                sentences
            ),
            "grammar_quality": self._measure_grammar(
                sentences
            ),
            "vocabulary_range": self._measure_vocabulary(
                words
            ),
            "clarity": self._measure_clarity(
                sentences,
                words
            ),
            "filler_words": filler_words,
            "filler_word_count": len(filler_words),
            "answer_structure": self._measure_structure(
                sentences,
                normalized
            ),
            "word_count": len(words),
            "sentence_count": len(sentences)
        }

    def _measure_fluency(self, words, sentences):
        """
        Basic deterministic fluency measure.

        Longer, properly segmented answers receive a higher
        feature value. This is a heuristic, not an ASR metric.
        """

        if not words:
            return 0

        word_score = min(
            len(words) / 20,
            1.0
        )

        sentence_score = min(
            len(sentences) / 3,
            1.0
        )

        return round(
            ((word_score * 0.6) +
             (sentence_score * 0.4)) * 100,
            2
        )

    def _measure_grammar(self, sentences):
        """
        Lightweight grammar-quality heuristic based on
        sentence completeness and capitalization.
        """

        if not sentences:
            return 0

        valid_sentences = 0

        for sentence in sentences:
            words = sentence.split()

            if len(words) >= 3:
                valid_sentences += 1

        return round(
            (valid_sentences / len(sentences)) * 100,
            2
        )

    def _measure_vocabulary(self, words):
        """
        Measures lexical variety using unique-word ratio.
        """

        if not words:
            return 0

        unique_words = set(words)

        ratio = len(unique_words) / len(words)

        return round(
            min(ratio, 1.0) * 100,
            2
        )

    def _measure_clarity(self, sentences, words):
        """
        Basic clarity heuristic using sentence length.
        Extremely short or excessively long sentences
        reduce the score.
        """

        if not sentences:
            return 0

        good_sentences = 0

        for sentence in sentences:
            count = len(sentence.split())

            if 5 <= count <= 25:
                good_sentences += 1

        return round(
            (good_sentences / len(sentences)) * 100,
            2
        )

    def _detect_filler_words(self, normalized):
        detected = []

        for filler in self.FILLER_WORDS:
            if filler in normalized:
                detected.append(filler)

        return sorted(detected)

    def _measure_structure(self, sentences, normalized):
        """
        Detect basic answer organization through multiple
        sentences and transition words.
        """

        if not sentences:
            return 0

        score = 0

        if len(sentences) >= 2:
            score += 50

        if any(
            transition in normalized
            for transition in self.TRANSITION_WORDS
        ):
            score += 50

        return min(score, 100)

    @staticmethod
    def _normalize(value):
        return " ".join(
            str(value).strip().lower().split()
        )

    @staticmethod
    def _split_sentences(value):
        sentences = []

        for part in value.replace("!", ".").replace("?", ".").split("."):
            cleaned = " ".join(part.strip().split())

            if cleaned:
                sentences.append(cleaned)

        return sentences