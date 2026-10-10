"""
ZECPATH AI - Behavioral Analysis Framework
Day 48: Maps observable interview signals to measurable indicators.

Scores describe observable signals only. They are not measures of
honesty, competence, personality, or psychological state.
"""


class BehavioralAnalysisFramework:

    SIGNAL_MAPPING = {
        "gaze_stability": {
            "indicator": "focus_level",
            "measurement": "Proportion of valid observation time with gaze in a defined interview area",
        },
        "head_movement": {
            "indicator": "movement_frequency",
            "measurement": "Number of detected head movements per minute",
        },
        "facial_engagement": {
            "indicator": "engagement_signal",
            "measurement": "Presence and duration of predefined visible engagement cues",
        },
        "attention_patterns": {
            "indicator": "distraction_frequency",
            "measurement": "Number of detected attention shifts away from the interview area per minute",
        },
        "nervous_gestures": {
            "indicator": "gesture_frequency",
            "measurement": "Number of predefined repetitive gestures per minute",
        },
    }

    @classmethod
    def get_signal_mapping(cls):
        return {
            signal: dict(details)
            for signal, details in cls.SIGNAL_MAPPING.items()
        }

    @classmethod
    def map_observations(cls, observations):
        if not isinstance(observations, dict):
            raise TypeError("Observations must be a dictionary.")

        results = {}

        for signal, details in cls.SIGNAL_MAPPING.items():
            value = observations.get(signal)

            results[signal] = {
                "indicator": details["indicator"],
                "observed_value": value,
                "measurement": details["measurement"],
                "available": value is not None,
            }

        return {
            "signals": results,
            "missing_signals": [
                signal
                for signal, result in results.items()
                if not result["available"]
            ],
            "psychological_inference_performed": False,
            "human_review_required": True,
        }
