
import json
import math
from pathlib import Path

from scoring.explainability import ExplanationGenerator


class UnifiedScoringEngine:
    DEFAULT_CONFIG_PATH = (
        Path("config") / "unified_scoring_rules.json"
    )

    ROUND_NAMES = (
        "ats",
        "screening",
        "hr_interview",
        "technical_interview",
        "machine_test",
    )

    def __init__(self, config_path=None):
        self.config_path = Path(
            config_path or self.DEFAULT_CONFIG_PATH
        )
        self.config = self._load_config()
        self._validate_config()
        self.explanation_generator = ExplanationGenerator()

    def _load_config(self):
        with self.config_path.open("r", encoding="utf-8") as file:
            return json.load(file)

    def _validate_config(self):
        rounds = self.config.get("rounds", {})
        required = {"ats", "screening", "hr_interview"}

        if not required.issubset(rounds):
            raise ValueError("Scoring configuration is missing required rounds.")

        for name, settings in rounds.items():
            minimum = settings.get("input_minimum")
            maximum = settings.get("input_maximum")
            weight = settings.get("weight")

            if (
                not isinstance(minimum, (int, float))
                or not isinstance(maximum, (int, float))
                or minimum >= maximum
            ):
                raise ValueError(f"Invalid score range for round '{name}'.")

            if (
                not isinstance(weight, (int, float))
                or not math.isfinite(weight)
                or not 0 <= weight <= 1
            ):
                raise ValueError(f"Invalid configured weight for round '{name}'.")

        role_adjustments = self.config.get("role_adjustments", {})
        for role, weights in role_adjustments.items():
            self._validate_role_weights(weights)

    @staticmethod
    def _validate_score(score, minimum, maximum, score_name):
        if score is None or isinstance(score, bool):
            raise ValueError(f"{score_name} must be numeric.")

        try:
            score = float(score)
        except (TypeError, ValueError):
            raise ValueError(
                f"{score_name} must be numeric."
            ) from None

        if not math.isfinite(score):
            raise ValueError(
                f"{score_name} must be a finite number."
            )

        if not minimum <= score <= maximum:
            raise ValueError(
                f"{score_name} must be between {minimum} and {maximum}."
            )

        return score


    @staticmethod
    def _normalize_score(
        score,
        input_minimum,
        input_maximum,
        target_minimum=0,
        target_maximum=100,
    ):
        if input_maximum == input_minimum:
            raise ValueError("Input score range cannot be zero.")

        value = (
            (score - input_minimum)
            / (input_maximum - input_minimum)
        ) * (target_maximum - target_minimum) + target_minimum

        return round(value, 2)

    @staticmethod
    def _validate_role_weights(weights):
        legacy_rounds = {
            "ats",
            "screening",
            "hr_interview",
        }
        five_rounds = set(UnifiedScoringEngine.ROUND_NAMES)

        if not isinstance(weights, dict):
            raise ValueError("Role weights must be a dictionary.")

        if set(weights) not in (legacy_rounds, five_rounds):
            raise ValueError(
                "Role weights must contain either the three "
                "legacy rounds or all five evaluation rounds."
            )

        validated = {}

        for name, value in weights.items():
            if isinstance(value, bool):
                raise ValueError(
                    f"Weight '{name}' must be numeric."
                )

            try:
                value = float(value)
            except (TypeError, ValueError):
                raise ValueError(
                    f"Weight '{name}' must be numeric."
                ) from None

            if not math.isfinite(value):
                raise ValueError(
                    f"Weight '{name}' must be a finite number."
                )

            if not 0 <= value <= 1:
                raise ValueError(
                    f"Weight '{name}' must be between 0 and 1."
                )

            validated[name] = value

        if not math.isclose(
            sum(validated.values()),
            1.0,
            abs_tol=1e-6,
        ):
            raise ValueError("Role weights must total 1.0.")

        return validated


    def _get_role_weights(self, role):
        adjustments = self.config.get("role_adjustments", {})
        default = adjustments.get("default")

        if default is None:
            config_rounds = self.config.get("rounds", {})
            default = {
                name: config_rounds[name]["weight"]
                for name in self.ROUND_NAMES
                if name in config_rounds
            }

        normalized_role = (
            (role or "")
            .strip()
            .lower()
            .replace(" ", "_")
            .replace("-", "_")
        )

        weights = adjustments.get(normalized_role, default)
        return self._validate_role_weights(weights)


    def calculate_score(
        self,
        candidate_name,
        role,
        ats_score,
        screening_score,
        hr_interview_score,
        technical_interview_score=None,
        machine_test_score=None,
    ):
        supplied = {
            "ats": ats_score,
            "screening": screening_score,
            "hr_interview": hr_interview_score,
            "technical_interview": technical_interview_score,
            "machine_test": machine_test_score,
        }

        active_rounds = [
            name for name in self.ROUND_NAMES
            if supplied[name] is not None
        ]

        if not {"ats", "screening", "hr_interview"}.issubset(active_rounds):
            raise ValueError("ATS, screening, and HR interview scores are required.")

        config_rounds = self.config["rounds"]
        normalized = {}
        raw = {}

        for name in active_rounds:
            settings = config_rounds.get(name)
            if settings is None:
                raise ValueError(
                    f"Configuration is missing the '{name}' round."
                )

            raw[name] = self._validate_score(
                supplied[name],
                settings["input_minimum"],
                settings["input_maximum"],
                f"{name} score",
            )

            normalization = self.config.get("normalization", {})
            if normalization.get("enabled", True):
                normalized[name] = self._normalize_score(
                    raw[name],
                    settings["input_minimum"],
                    settings["input_maximum"],
                    normalization.get("target_minimum", 0),
                    normalization.get("target_maximum", 100),
                )
            else:
                normalized[name] = raw[name]

        configured_weights = self._get_role_weights(role)

        if len(active_rounds) == 3:
            legacy_role_weights = {
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

            role_key = (
                (role or "")
                .strip()
                .lower()
                .replace(" ", "_")
                .replace("-", "_")
            )

            effective_weights = legacy_role_weights.get(
                role_key,
                legacy_role_weights["default"],
            )
        else:
            active_weight_total = sum(
                configured_weights[name] for name in active_rounds
            )

            if active_weight_total <= 0:
                raise ValueError("Active round weights must total more than zero.")

            effective_weights = {
                name: configured_weights[name] / active_weight_total
                for name in active_rounds
            }

        weighted = {
            name: round(normalized[name] * effective_weights[name], 2)
            for name in active_rounds
        }

        unified_score = round(sum(weighted.values()), 2)

        result = {
            "candidate": candidate_name or "Unknown",
            "role": role or "Unknown",
            "round_count": len(active_rounds),
            "round_scores": raw,
            "normalized_scores": normalized,
            "weights": {
                name: round(effective_weights[name], 6)
                for name in active_rounds
            },
            "weighted_scores": weighted,
            "unified_score": unified_score,
            "hiring_fit_percentage": unified_score,
            "score_type": "unified_candidate_score",
        }

        result["explainability"] = self.explanation_generator.generate(result)
        return result
