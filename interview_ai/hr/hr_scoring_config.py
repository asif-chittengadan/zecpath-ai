import json
from pathlib import Path


class HRScoringConfig:
    """
    Loads and validates HR interview scoring configuration.
    """

    REQUIRED_PARAMETERS = {
        "answer_relevance",
        "communication",
        "confidence",
        "consistency"
    }

    def __init__(self, config_path, required_parameters=None):
        self.config_path = Path(config_path)
        self.required_parameters = (
            required_parameters
            if required_parameters is not None
            else self.REQUIRED_PARAMETERS
        )
        self.config = self._load_config()
        self._validate()

    def _load_config(self):
        with self.config_path.open(
            "r",
            encoding="utf-8"
        ) as file:
            return json.load(file)

    def _validate(self):
        parameters = self.config.get(
            "parameters",
            {}
        )

        missing = (
            set(self.required_parameters)
            - set(parameters.keys())
        )

        if missing:
            raise ValueError(
                "Missing scoring parameters: "
                + ", ".join(sorted(missing))
            )

        weights = [
            parameters[name]["weight"]
            for name in self.required_parameters
        ]

        if any(
            weight < 0 or weight > 1
            for weight in weights
        ):
            raise ValueError(
                "Scoring weights must be between 0 and 1."
            )

        total_weight = sum(weights)

        if round(total_weight, 6) != 1.0:
            raise ValueError(
                f"Scoring weights must total 1.0. "
                f"Current total: {total_weight}"
            )

    def get_parameter(self, name):
        return self.config[
            "parameters"
        ][name]

    def get_weight(self, name):
        return self.get_parameter(
            name
        )["weight"]

    def get_weights(self):
        return {
            name: self.get_weight(name)
            for name in self.required_parameters
        }

    def get_score_range(self):
        return self.config.get(
            "score_range",
            {
                "minimum": 0,
                "maximum": 100
            }
        )

    def is_normalization_enabled(self):
        return self.config.get(
            "normalization",
            {}
        ).get(
            "enabled",
            True
        )