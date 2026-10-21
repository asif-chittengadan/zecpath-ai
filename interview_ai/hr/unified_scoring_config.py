
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
    def _validate_weights(weights, label, required_rounds=None):
        """Validate a complete set of round weights."""

        if not isinstance(weights, dict):
            raise ValueError(
                f"Weights for {label} must be a dictionary."
            )

        expected_rounds = required_rounds or UnifiedScoringConfig.REQUIRED_ROUNDS
        if set(weights) != expected_rounds:
            raise ValueError(
                f"Invalid role weights for: {label}. "
                "All required evaluation rounds must be provided."
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

        legacy_adjustments = self.config.get("legacy_role_adjustments", {})
        if not isinstance(legacy_adjustments, dict):
            raise ValueError("Legacy role adjustments must be a dictionary.")
        if legacy_adjustments and "default" not in legacy_adjustments:
            raise ValueError(
                "Legacy role adjustments must include default weights."
            )
        for role, weights in legacy_adjustments.items():
            self._validate_weights(
                weights,
                role,
                required_rounds=self.LEGACY_ROUNDS,
            )

    def get_round(self, name):
        return self.config["rounds"][name]

    def get_weight(self, name):
        legacy_weights = self.config.get(
            "legacy_role_adjustments", {}
        ).get("default", {})

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
        legacy_roles = self.config.get("legacy_role_adjustments", {})
        if legacy_roles:
            normalized_role = (
                (role or "")
                .strip()
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

        # Older configuration files may only provide five-round weights.
        normalized_role = (
            (role or "")
            .strip()
            .lower()
            .replace(" ", "_")
            .replace("-", "_")
        )
        role_adjustments = self.config.get("role_adjustments", {})
        five_round_weights = role_adjustments.get(
            normalized_role,
            role_adjustments.get("default", {}),
        )
        legacy_weights = {
            name: five_round_weights[name]
            for name in self.LEGACY_ROUNDS
            if name in five_round_weights
        }
        total = sum(legacy_weights.values())
        if total <= 0:
            raise ValueError("Legacy active round weights must total more than zero.")
        return {
            name: weight / total
            for name, weight in legacy_weights.items()
        }
