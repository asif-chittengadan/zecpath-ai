from typing import Any, Dict, List


class ExplanationGenerator:
    """
    Generates human-readable explanations from existing ZECPATH
    scoring results.

    The generator does not calculate or modify candidate scores.
    It only explains values already produced by the scoring engine.

    It intentionally uses only job-relevant scoring information.
    """

    ROUND_LABELS = {
        "ats": "ATS screening",
        "screening": "AI screening",
        "hr_interview": "HR interview",
    }

    def generate(
        self,
        scoring_result: Dict[str, Any],
        skill_details: Dict[str, Any] | None = None,
        experience_details: Dict[str, Any] | None = None,
        education_details: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        """
        Generate structured explainability information.

        scoring_result must come from the ZECPATH scoring pipeline.

        Optional skill, experience, and education details can be
        supplied when those details are available from the upstream
        scoring components.
        """

        if not isinstance(scoring_result, dict):
            raise TypeError(
                "scoring_result must be a dictionary."
            )

        unified_score = scoring_result.get(
            "unified_score"
        )

        if unified_score is None:
            raise ValueError(
                "scoring_result must contain 'unified_score'."
            )

        explanation = {
            "candidate": scoring_result.get(
                "candidate",
                "Unknown",
            ),
            "role": scoring_result.get(
                "role",
                "Unknown",
            ),
            "score": unified_score,
            "hiring_fit_percentage": scoring_result.get(
                "hiring_fit_percentage",
                unified_score,
            ),
            "score_breakdown": self._build_score_breakdown(
                scoring_result
            ),
            "job_relevant_evidence": self._build_evidence(
                skill_details=skill_details,
                experience_details=experience_details,
                education_details=education_details,
            ),
            "summary": self._build_summary(
                scoring_result
            ),
            "limitations": [
                "The explanation reflects the scoring "
                "factors available to ZECPATH.",
                "An AI-assisted evaluation should be "
                "reviewed together with relevant "
                "candidate evidence and applicable "
                "human review procedures.",
            ],
        }

        return explanation

    def _build_score_breakdown(
        self,
        scoring_result: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        weighted_scores = scoring_result.get(
            "weighted_scores",
            {}
        )

        normalized_scores = scoring_result.get(
            "normalized_scores",
            {}
        )

        weights = scoring_result.get(
            "weights",
            {}
        )

        round_scores = scoring_result.get(
            "round_scores",
            {}
        )

        breakdown = []

        for round_name in (
            "ats",
            "screening",
            "hr_interview",
        ):
            breakdown.append(
                {
                    "round": round_name,
                    "label": self.ROUND_LABELS[
                        round_name
                    ],
                    "raw_score": round_scores.get(
                        round_name
                    ),
                    "normalized_score": normalized_scores.get(
                        round_name
                    ),
                    "weight": weights.get(
                        round_name
                    ),
                    "weighted_contribution": weighted_scores.get(
                        round_name
                    ),
                }
            )

        return breakdown

    @staticmethod
    def _build_evidence(
        skill_details,
        experience_details,
        education_details,
    ) -> Dict[str, Any]:
        evidence = {}

        if skill_details is not None:
            evidence["skills"] = skill_details

        if experience_details is not None:
            evidence["experience"] = experience_details

        if education_details is not None:
            evidence["education"] = education_details

        return evidence

    def _build_summary(
        self,
        scoring_result: Dict[str, Any],
    ) -> str:
        score = scoring_result.get(
            "unified_score",
            0,
        )

        breakdown = scoring_result.get(
            "weighted_scores",
            {}
        )

        contributing_rounds = [
            self.ROUND_LABELS[name]
            for name in (
                "ats",
                "screening",
                "hr_interview",
            )
            if breakdown.get(name) is not None
        ]

        if contributing_rounds:
            rounds_text = ", ".join(
                contributing_rounds
            )

            return (
                f"The unified score is {score}. "
                f"It is derived from the configured "
                f"ZECPATH scoring components: "
                f"{rounds_text}."
            )

        return (
            f"The unified score is {score}. "
            "No additional scoring breakdown "
            "was available."
        )