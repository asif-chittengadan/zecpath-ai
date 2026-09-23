class CommunicationScoringEngine:
    """
    Calculates a 0-100 communication score from
    communication feature analysis.

    This is a deterministic scoring model.
    """

    WEIGHTS = {
        "fluency": 0.20,
        "grammar_quality": 0.20,
        "vocabulary_range": 0.15,
        "clarity": 0.20,
        "answer_structure": 0.15,
        "filler_control": 0.10
    }

    def score(self, features):
        """
        Calculate the final communication score.

        Returns:
            {
                "score": float,
                "components": dict,
                "formula": str
            }
        """

        filler_control = self._calculate_filler_control(
            features
        )

        components = {
            "fluency": self._bounded(
                features.get("fluency", 0)
            ),
            "grammar_quality": self._bounded(
                features.get("grammar_quality", 0)
            ),
            "vocabulary_range": self._bounded(
                features.get("vocabulary_range", 0)
            ),
            "clarity": self._bounded(
                features.get("clarity", 0)
            ),
            "answer_structure": self._bounded(
                features.get("answer_structure", 0)
            ),
            "filler_control": filler_control
        }

        total = 0

        for name, weight in self.WEIGHTS.items():
            total += components[name] * weight

        total = round(
            self._bounded(total),
            2
        )

        return {
            "score": total,
            "components": components,
            "formula": (
                "(Fluency × 0.20) + "
                "(Grammar × 0.20) + "
                "(Vocabulary × 0.15) + "
                "(Clarity × 0.20) + "
                "(Structure × 0.15) + "
                "(Filler Control × 0.10)"
            )
        }

    def _calculate_filler_control(self, features):
        """
        Convert filler-word frequency into a 0-100
        control score.

        Up to 5 filler words produce a gradual penalty.
        Beyond 5, the control score reaches zero.
        """

        filler_count = max(
            0,
            int(features.get("filler_word_count", 0))
        )

        penalty = min(
            filler_count * 10,
            100
        )

        return round(
            100 - penalty,
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