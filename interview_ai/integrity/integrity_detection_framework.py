class IntegrityDetectionFramework:
    SIGNALS = {
        "tab_switching": {
            "metric": "switches_per_minute",
            "unit": "count",
        },
        "screen_focus_loss": {
            "metric": "focus_loss_events_per_minute",
            "unit": "count",
        },
        "external_voice": {
            "metric": "external_voice_events",
            "unit": "count",
        },
        "repeated_looking_away": {
            "metric": "look_away_events_per_minute",
            "unit": "count",
        },
    }

    @classmethod
    def get_supported_signals(cls):
        return {
            name: details.copy()
            for name, details in cls.SIGNALS.items()
        }

    @classmethod
    def analyze(cls, observations):
        if not isinstance(observations, dict):
            raise TypeError("observations must be a dictionary")

        unknown = set(observations) - set(cls.SIGNALS)
        if unknown:
            raise ValueError(f"Unknown signals: {sorted(unknown)}")

        signals = {}

        for name, details in cls.SIGNALS.items():
            value = observations.get(name)

            if value is not None:
                if (
                    not isinstance(value, (int, float))
                    or isinstance(value, bool)
                    or value < 0
                ):
                    raise ValueError(
                        f"{name} must be a non-negative number or None"
                    )

            signals[name] = {
                **details,
                "observed_value": value,
                "available": value is not None,
            }

        return {
            "signals": signals,
            "missing_signals": [
                name
                for name, signal in signals.items()
                if not signal["available"]
            ],
            "human_review_required": True,
        }