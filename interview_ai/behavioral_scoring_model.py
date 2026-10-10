class BehavioralScoringModel:

    WEIGHTS = {
        "gaze_stability": 0.30,
        "head_movement": 0.15,
        "facial_engagement": 0.20,
        "attention_patterns": 0.25,
        "nervous_gestures": 0.10,
    }

    @staticmethod
    def _validate_score(name, value):
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            raise TypeError(f"{name} must be numeric.")

        if not 0 <= value <= 100:
            raise ValueError(f"{name} must be between 0 and 100.")

    @classmethod
    def calculate_score(cls, signal_scores):
        if not isinstance(signal_scores, dict):
            raise TypeError("signal_scores must be a dictionary.")

        unknown = set(signal_scores) - set(cls.WEIGHTS)
        if unknown:
            raise ValueError(
                f"Unknown signals: {sorted(unknown)}"
            )

        if not signal_scores:
            return {
                "overall_score": None,
                "coverage": 0.0,
                "signals_scored": 0,
                "missing_signals": list(cls.WEIGHTS),
                "human_review_required": True,
            }

        for name, value in signal_scores.items():
            cls._validate_score(name, value)

        available_weight = sum(
            cls.WEIGHTS[name] for name in signal_scores
        )

        weighted_total = sum(
            signal_scores[name] * cls.WEIGHTS[name]
            for name in signal_scores
        )

        # Renormalize only across signals actually observed.
        score = weighted_total / available_weight

        return {
            "overall_score": round(score, 2),
            "coverage": round(available_weight * 100, 2),
            "signals_scored": len(signal_scores),
            "missing_signals": [
                name for name in cls.WEIGHTS
                if name not in signal_scores
            ],
            "human_review_required": True,
            "interpretation": (
                "Observable-signal summary only; not a psychological "
                "or hiring suitability assessment."
            ),
        }