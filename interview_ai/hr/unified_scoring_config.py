import json
from pathlib import Path


class UnifiedScoringConfig:
    """
    Loads and validates cross-round scoring configuration.
    """

    REQUIRED_ROUNDS = {
        "ats",
        "screening",
        "hr_interview"
    }

    def __init__(self, config_path):
        self.config_path = Path(config_path)
        self.config = self._load_config()
        self._validate()

    def _load_config(self):
        with self.config_path.open(
            "r",
            encoding="utf-8"
        ) as file:
            return json.load(file)

    def _validate(self):
        rounds = self.config.get(
            "rounds",
            {}
        )

        missing = (
            self.REQUIRED_ROUNDS
            - set(rounds.keys())
        )

        if missing:
            raise ValueError(
                "Missing scoring rounds: "
                + ", ".join(sorted(missing))
            )

        weights = [
            rounds[name]["weight"]
            for name in self.REQUIRED_ROUNDS
        ]

        if any(
            weight < 0 or weight > 1
            for weight in weights
        ):
            raise ValueError(
                "Round weights must be between 0 and 1."
            )

        total_weight = sum(weights)

        if round(total_weight, 6) != 1.0:
            raise ValueError(
                "Round weights must total 1.0. "
                f"Current total: {total_weight}"
            )
        
        role_adjustments = self.config.get(
            "role_adjustments",
            {}
        )

        for role, weights in role_adjustments.items():

            required_keys = {
                "ats",
                "screening",
                "hr_interview"
            }

            if set(weights.keys()) != required_keys:
                raise ValueError(
                    f"Invalid role weights for: {role}"
                )

            total = sum(weights.values())

            if round(total, 6) != 1.0:
                raise ValueError(
                    f"Weights for {role} "
                    f"must total 1.0."
                )

            if any(
                weight < 0 or weight > 1
                for weight in weights.values()
            ):
                raise ValueError(
                    f"Invalid weight for {role}."
                )

    def get_round(self, name):
        return self.config[
            "rounds"
        ][name]

    def get_weight(self, name):
        return self.get_round(
            name
        )["weight"]

    def get_weights(self):
        return {
            name: self.get_weight(name)
            for name in self.REQUIRED_ROUNDS
        }

    def get_input_range(self, name):
        round_config = self.get_round(name)

        return {
            "minimum":
                round_config["input_minimum"],
            "maximum":
                round_config["input_maximum"]
        }

    def get_score_range(self):
        return self.config.get(
            "score_range",
            {
                "minimum": 0,
                "maximum": 100
            }
        )

    def get_role_weights(self, role=None):
        """
        Return cross-round weights for a specific role.

        Falls back to the default weights when the role
        is not configured.
        """

        role_adjustments = self.config.get(
            "role_adjustments",
            {}
        )

        if not role:
            return role_adjustments.get(
                "default",
                self.get_weights()
            )

        normalized_role = (
            role.strip()
            .lower()
            .replace(" ", "_")
            .replace("-", "_")
        )

        weights = role_adjustments.get(
            normalized_role
        )

        if weights is None:
            weights = role_adjustments.get(
                "default",
                self.get_weights()
            )

        return weights