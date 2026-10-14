
import json
import math
from pathlib import Path


class UnifiedScoringConfig:
    """
    Loads and validates cross-round scoring configuration.
    Supports all five evaluation rounds used by Zecpath AI.
    """

    LEGACY_ROUNDS = {
        "ats",
        "screening",
        "hr_interview",
    }

    REQUIRED_ROUNDS = {
        "ats",
        "screening",
        "hr_interview",
        "technical_interview",
        "machine_test",
    }

    def __init__(self, config_path):
        self.config_path = Path(config_path)
        self.config = self._load_config()
        self._validate()

    def _load_config(self):
        with self.config_path.open(
            "r",
            encoding="utf-8",
        ) as file:
            return json.load(file)

    @staticmethod
    def _validate_weights(weights, label):
        """Validate a complete set of five-round weights."""

        if not isinstance(weights, dict):
            raise ValueError(
                f"Weights for {label} must be a dictionary."
            )

        if set(weights) != UnifiedScoringConfig.REQUIRED_ROUNDS:
            raise ValueError(
                f"Invalid role weights for: {label}. "
                "All five evaluation rounds are required."
            )

        validated = {}

        for name, weight in weights.items():
            if isinstance(weight, bool) or not isinstance(
                weight, (int, float)
            ):
                raise ValueError(
                    f"Weight '{name}' for {label} must be numeric."
                )

            if not math.isfinite(weight):
                raise ValueError(
                    f"Weight '{name}' for {label} must be finite."
                )

            if not 0 <= weight <= 1:
                raise ValueError(
                    f"Weight '{name}' for {label} "
                    "must be between 0 and 1."
                )

            validated[name] = weight

        if not math.isclose(
            sum(validated.values()),
            1.0,
            abs_tol=1e-6,
        ):
            raise ValueError(
                f"Weights for {label} must total 1.0. "
                f"Current total: {sum(validated.values())}"
            )

        return validated

    def _validate(self):
        rounds = self.config.get("rounds", {})

        if not isinstance(rounds, dict):
            raise ValueError(
                "Scoring rounds must be a dictionary."
            )

        missing = self.REQUIRED_ROUNDS - set(rounds)

        if missing:
            raise ValueError(
                "Missing scoring rounds: "
                + ", ".join(sorted(missing))
            )

        for name in self.REQUIRED_ROUNDS:
            settings = rounds[name]

            if not isinstance(settings, dict):
                raise ValueError(
                    f"Invalid configuration for round '{name}'."
                )

            minimum = settings.get("input_minimum")
            maximum = settings.get("input_maximum")

            for field, value in (
                ("input_minimum", minimum),
                ("input_maximum", maximum),
            ):
                if (
                    isinstance(value, bool)
                    or not isinstance(value, (int, float))
                    or not math.isfinite(value)
                ):
                    raise ValueError(
                        f"Invalid {field} for round '{name}'."
                    )

            if minimum >= maximum:
                raise ValueError(
                    f"Invalid score range for round '{name}'."
                )

        round_weights = {
            name: rounds[name].get("weight")
            for name in self.REQUIRED_ROUNDS
        }

        self._validate_weights(
            round_weights,
            "round configuration",
        )

        role_adjustments = self.config.get(
            "role_adjustments",
            {},
        )

        if not isinstance(role_adjustments, dict):
            raise ValueError(
                "Role adjustments must be a dictionary."
            )

        if role_adjustments and "default" not in role_adjustments:
            raise ValueError(
                "Role adjustments must include default weights."
            )

        for role, weights in role_adjustments.items():
            self._validate_weights(weights, role)

    def get_round(self, name):
        return self.config["rounds"][name]

    def get_weight(self, name):
        legacy_weights = {
            "ats": 0.40,
            "screening": 0.25,
            "hr_interview": 0.35,
        }

        if name in legacy_weights:
            return legacy_weights[name]

        return self.get_round(name)["weight"]

    def get_weights(self):
        return {
            name: self.get_weight(name)
            for name in self.LEGACY_ROUNDS
        }

    def get_input_range(self, name):
        round_config = self.get_round(name)

        return {
            "minimum": round_config["input_minimum"],
            "maximum": round_config["input_maximum"],
        }

    def get_score_range(self):
        return self.config.get(
            "score_range",
            {
                "minimum": 0,
                "maximum": 100,
            },
        )

    def get_role_weights(self, role=None):
        legacy_roles = {
            "default": {
                "ats": 0.40,
                "screening": 0.25,
                "hr_interview": 0.35,
            },
            "software_developer": {
                "ats": 0.45,
                "screening": 0.20,
                "hr_interview": 0.35,
            },
            "data_scientist": {
                "ats": 0.45,
                "screening": 0.20,
                "hr_interview": 0.35,
            },
            "sales_executive": {
                "ats": 0.30,
                "screening": 0.30,
                "hr_interview": 0.40,
            },
            "hr_manager": {
                "ats": 0.25,
                "screening": 0.30,
                "hr_interview": 0.45,
            },
        }

        if not role:
            return dict(legacy_roles["default"])

        normalized_role = (
            role.strip()
            .lower()
            .replace(" ", "_")
            .replace("-", "_")
        )

        return dict(
            legacy_roles.get(
                normalized_role,
                legacy_roles["default"],
            )
        )