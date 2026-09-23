class CommunicationScoreNormalizer:
    """
    Normalizes communication scores to a consistent 0-100 range.

    This is a deterministic normalization layer intended to
    reduce the effect of raw score extremes.
    """

    def normalize(self, score, word_count=None):
        """
        Normalize a communication score.

        Args:
            score: Raw communication score.
            word_count: Optional answer length.

        Returns:
            Normalized score between 0 and 100.
        """

        score = self._bounded(score)

        # Very short answers should not receive an artificial
        # advantage from having fewer opportunities for errors.
        if word_count is not None:
            try:
                word_count = int(word_count)
            except (TypeError, ValueError):
                word_count = None

            # No answer means no communication score.
            if word_count == 0:
                return 0

            # Very short answers receive a reduced score.
            if word_count is not None and word_count < 3:
                score *= 0.50

        return round(
            self._bounded(score),
            2
        )

    @staticmethod
    def _bounded(value):
        try:
            value = float(value)
        except (TypeError, ValueError):
            return 0.0

        return max(
            0.0,
            min(value, 100.0)
        )