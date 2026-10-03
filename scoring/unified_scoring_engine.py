import json
import math
from pathlib import Path
from scoring.explainability import ExplanationGenerator


class UnifiedScoringEngine:
    """
    Combines ATS, screening, and HR interview scores
    into a unified hiring-fit score.
    """

    DEFAULT_CONFIG_PATH = (
        Path("config") /
        "unified_scoring_rules.json"
    )

    def __init__(self, config_path=None):

        if config_path is None:
            config_path = self.DEFAULT_CONFIG_PATH

        self.config_path = Path(config_path)
        self.config = self._load_config()

        self._validate_config()

        self.explanation_generator = ExplanationGenerator()

    def _load_config(self):

        with self.config_path.open(
            "r",
            encoding="utf-8"
        ) as file:

            return json.load(file)

    def _validate_config(self):

        rounds = self.config.get(
            "rounds",
            {}
        )

        required_rounds = {
            "ats",
            "screening",
            "hr_interview"
        }

        if not required_rounds.issubset(
            rounds.keys()
        ):
            raise ValueError(
                "Unified scoring configuration "
                "is missing required rounds."
            )

        total_weight = sum(
            rounds[name]["weight"]
            for name in required_rounds
        )

        if round(total_weight, 6) != 1.0:
            raise ValueError(
                "Unified scoring weights must "
                f"total 1.0, got {total_weight}"
            )

    @staticmethod
    def _validate_score(
        score,
        minimum,
        maximum,
        score_name
    ):

        if score is None:
            raise ValueError(
                f"{score_name} cannot be None."
            )

        try:
            score = float(score)
        except (TypeError, ValueError):
            raise ValueError(
                f"{score_name} must be numeric."
            )

        if not math.isfinite(score):
            raise ValueError(
                f"{score_name} must be a finite number."
            )

        if not minimum <= score <= maximum:
            raise ValueError(
                f"{score_name} must be between "
                f"{minimum} and {maximum}."
            )

        return score

    @staticmethod
    def _normalize_score(
        score,
        input_minimum,
        input_maximum,
        target_minimum=0,
        target_maximum=100
    ):

        if input_maximum == input_minimum:
            raise ValueError(
                "Input score range cannot be zero."
            )

        normalized = (
            (
                score - input_minimum
            )
            /
            (
                input_maximum -
                input_minimum
            )
        ) * (
            target_maximum -
            target_minimum
        ) + target_minimum

        return round(normalized, 2)

    def calculate_score(
        self,
        candidate_name,
        role,
        ats_score,
        screening_score,
        hr_interview_score
    ):

        ats_config = self.config[
            "rounds"
        ]["ats"]

        screening_config = self.config[
            "rounds"
        ]["screening"]

        hr_config = self.config[
            "rounds"
        ]["hr_interview"]

        ats_score = self._validate_score(
            ats_score,
            ats_config["input_minimum"],
            ats_config["input_maximum"],
            "ATS score"
        )

        screening_score = self._validate_score(
            screening_score,
            screening_config["input_minimum"],
            screening_config["input_maximum"],
            "Screening score"
        )

        hr_interview_score = self._validate_score(
            hr_interview_score,
            hr_config["input_minimum"],
            hr_config["input_maximum"],
            "HR interview score"
        )

        normalized_ats = self._normalize_score(
            ats_score,
            ats_config["input_minimum"],
            ats_config["input_maximum"]
        )

        normalized_screening = self._normalize_score(
            screening_score,
            screening_config["input_minimum"],
            screening_config["input_maximum"]
        )

        normalized_hr = self._normalize_score(
            hr_interview_score,
            hr_config["input_minimum"],
            hr_config["input_maximum"]
        )

        role_weights = self._get_role_weights(
            role
        )

        ats_weight = role_weights["ats"]
        screening_weight = role_weights["screening"]
        hr_weight = role_weights["hr_interview"]

        weighted_ats = round(
            normalized_ats * ats_weight,
            2
        )

        weighted_screening = round(
            normalized_screening *
            screening_weight,
            2
        )

        weighted_hr = round(
            normalized_hr * hr_weight,
            2
        )

        unified_score = round(
            weighted_ats +
            weighted_screening +
            weighted_hr,
            2
        )

        result = {
            "candidate": candidate_name or "Unknown",
            "role": role or "Unknown",
            "round_scores": {
                "ats": ats_score,
                "screening": screening_score,
                "hr_interview": hr_interview_score
            },
            "normalized_scores": {
                "ats": normalized_ats,
                "screening": normalized_screening,
                "hr_interview": normalized_hr
            },
            "weights": {
                "ats": ats_weight,
                "screening": screening_weight,
                "hr_interview": hr_weight
            },
            "weighted_scores": {
                "ats": weighted_ats,
                "screening": weighted_screening,
                "hr_interview": weighted_hr
            },
            "unified_score": unified_score,
            "hiring_fit_percentage": unified_score
        }

        result["explainability"] = (
            self.explanation_generator.generate(
                result
            )
        )

        return result

    def _validate_role_weights(self, weights):
        required_weights = {
            "ats",
            "screening",
            "hr_interview"
        }

        if not required_weights.issubset(weights.keys()):
            raise ValueError(
                "Role weights must contain ATS, screening, "
                "and HR interview weights."
            )

        validated_weights = {}

        for name in required_weights:
            try:
                weight = float(weights[name])
            except (TypeError, ValueError):
                raise ValueError(
                    f"Role weight '{name}' must be numeric."
                )

            if not math.isfinite(weight):
                raise ValueError(
                    f"Role weight '{name}' must be a finite number."
                )

            if not 0 <= weight <= 1:
                raise ValueError(
                    f"Role weight '{name}' must be between 0 and 1."
                )

            validated_weights[name] = weight

        total_weight = sum(validated_weights.values())

        if round(total_weight, 6) != 1.0:
            raise ValueError(
                "Role weights must total 1.0, "
                f"got {total_weight}"
            )

        return validated_weights

    def _get_role_weights(self, role):
        role_adjustments = self.config.get(
            "role_adjustments",
            {}
        )

        if not role:
            weights = role_adjustments.get(
                "default",
                {
                    "ats": 0.40,
                    "screening": 0.25,
                    "hr_interview": 0.35
                }
            )

            return self._validate_role_weights(weights)

        normalized_role = (
            role.strip()
            .lower()
            .replace(" ", "_")
            .replace("-", "_")
        )

        weights = role_adjustments.get(
            normalized_role,
            role_adjustments.get(
                "default",
                {
                    "ats": 0.40,
                    "screening": 0.25,
                    "hr_interview": 0.35
                }
            )
        )

        return self._validate_role_weights(weights)