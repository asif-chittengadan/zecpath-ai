class MalpracticeDetectionLogic:
    DEFAULT_THRESHOLDS = {
        "tab_switching": 3,
        "screen_focus_loss": 3,
        "external_voice": 1,
        "repeated_looking_away": 4,
    }

    def __init__(self, thresholds=None):
        self.thresholds = self.DEFAULT_THRESHOLDS.copy()

        if thresholds:
            unknown = set(thresholds) - set(self.thresholds)
            if unknown:
                raise ValueError(f"Unknown signals: {sorted(unknown)}")

            for signal, value in thresholds.items():
                if (
                    not isinstance(value, (int, float))
                    or isinstance(value, bool)
                    or value < 0
                ):
                    raise ValueError(
                        f"Threshold for {signal} must be non-negative"
                    )
                self.thresholds[signal] = value

    def evaluate(self, observations):
        if not isinstance(observations, dict):
            raise TypeError("observations must be a dictionary")

        unknown = set(observations) - set(self.thresholds)
        if unknown:
            raise ValueError(f"Unknown signals: {sorted(unknown)}")

        flags = []
        missing_signals = []

        for signal, threshold in self.thresholds.items():
            value = observations.get(signal)

            if value is None:
                missing_signals.append(signal)
                continue

            if (
                not isinstance(value, (int, float))
                or isinstance(value, bool)
                or value < 0
            ):
                raise ValueError(
                    f"Observation for {signal} must be non-negative"
                )

            if value >= threshold:
                flags.append({
                    "signal": signal,
                    "observed_value": value,
                    "threshold": threshold,
                    "flag": "REVIEW_REQUIRED",
                })

        return {
            "flags": flags,
            "flag_count": len(flags),
            "missing_signals": missing_signals,
            "human_review_required": bool(flags or missing_signals),
        }