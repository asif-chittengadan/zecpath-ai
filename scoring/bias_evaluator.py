from collections import defaultdict
from typing import Any, Dict, List, Optional


class BiasEvaluator:
    """
    Evaluates candidate scoring outputs for potential fairness concerns.

    IMPORTANT:
    Audit-only demographic/group information may be supplied to this
    evaluator for fairness analysis. It must never be passed into the
    production scoring engine.

    The evaluator does not modify candidate scores or rank candidates.
    It only reports statistical indicators that require review.
    """

    DEFAULT_SELECTION_THRESHOLD = 0.50
    DEFAULT_DISPARATE_IMPACT_THRESHOLD = 0.80
    DEFAULT_SCORE_GAP_THRESHOLD = 0.10

    def __init__(
        self,
        selection_threshold: float = DEFAULT_SELECTION_THRESHOLD,
        disparate_impact_threshold: float = DEFAULT_DISPARATE_IMPACT_THRESHOLD,
        score_gap_threshold: float = DEFAULT_SCORE_GAP_THRESHOLD,
    ):
        self.selection_threshold = self._validate_threshold(
            selection_threshold,
            "selection_threshold",
        )

        self.disparate_impact_threshold = self._validate_threshold(
            disparate_impact_threshold,
            "disparate_impact_threshold",
        )

        self.score_gap_threshold = self._validate_threshold(
            score_gap_threshold,
            "score_gap_threshold",
        )

    def evaluate(
        self,
        candidates: List[Dict[str, Any]],
        group_field: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Evaluate overall score distribution and, when an audit-only
        group field is supplied, calculate group-level fairness metrics.

        Expected candidate structure:

        {
            "candidate": "Candidate A",
            "score": 0.82,
            "audit_group": "group_a"
        }

        `audit_group` is used only for fairness analysis and must not
        be used by the production scoring engine.
        """

        if not candidates:
            return self._empty_result()

        scores = [
            self._normalize_score(candidate.get("score", 0))
            for candidate in candidates
        ]

        highest = max(scores)
        lowest = min(scores)

        score_range = round(
            highest - lowest,
            4,
        )

        indicators = []

        if score_range > 0.50:
            indicators.append(
                "Large score variation detected"
            )

        if all(score == 0 for score in scores):
            indicators.append(
                "All candidates received zero scores"
            )

        result = {
            "candidate_count": len(candidates),
            "score_range": score_range,
            "average_score": round(
                sum(scores) / len(scores),
                4,
            ),
            "bias_indicators": indicators,
            "group_analysis": [],
        }

        if group_field:
            result["group_analysis"] = self._evaluate_groups(
                candidates,
                group_field,
            )

        return result

    def _evaluate_groups(
        self,
        candidates: List[Dict[str, Any]],
        group_field: str,
    ) -> List[Dict[str, Any]]:
        """
        Calculate fairness indicators for audit groups.

        Metrics:
        - group size
        - average score
        - selection rate
        - score gap from highest-performing group
        - disparate impact ratio

        These are review indicators, not automatic decisions.
        """

        groups = defaultdict(list)

        for candidate in candidates:
            group = candidate.get(group_field)

            if group is None:
                continue

            groups[str(group)].append(
                self._normalize_score(
                    candidate.get("score", 0)
                )
            )

        if not groups:
            return []

        group_statistics = []

        for group_name, scores in groups.items():
            average_score = sum(scores) / len(scores)

            selected_count = sum(
                score >= self.selection_threshold
                for score in scores
            )

            selection_rate = selected_count / len(scores)

            group_statistics.append(
                {
                    "group": group_name,
                    "candidate_count": len(scores),
                    "average_score": round(
                        average_score,
                        4,
                    ),
                    "selection_rate": round(
                        selection_rate,
                        4,
                    ),
                }
            )

        max_selection_rate = max(
            item["selection_rate"]
            for item in group_statistics
        )

        max_average_score = max(
            item["average_score"]
            for item in group_statistics
        )

        for item in group_statistics:
            selection_rate = item["selection_rate"]

            if max_selection_rate > 0:
                disparate_impact = (
                    selection_rate / max_selection_rate
                )
            else:
                disparate_impact = 1.0

            score_gap = (
                max_average_score -
                item["average_score"]
            )

            item["disparate_impact_ratio"] = round(
                disparate_impact,
                4,
            )

            item["score_gap_from_highest_group"] = round(
                score_gap,
                4,
            )

            item["review_required"] = (
                disparate_impact <
                self.disparate_impact_threshold
                or
                score_gap >
                self.score_gap_threshold
            )

        return group_statistics

    @staticmethod
    def _normalize_score(score: Any) -> float:
        """
        Convert scores to a normalized 0.0-1.0 range.

        Existing ZECPATH code may provide either:
        - 0.0 to 1.0
        - 0 to 100
        """

        try:
            normalized = float(score)
        except (TypeError, ValueError):
            normalized = 0.0

        if normalized > 1:
            normalized /= 100

        return max(
            0.0,
            min(normalized, 1.0),
        )

    @staticmethod
    def _validate_threshold(
        value: float,
        name: str,
    ) -> float:
        try:
            value = float(value)
        except (TypeError, ValueError) as exc:
            raise ValueError(
                f"{name} must be a numeric value."
            ) from exc

        if not 0 <= value <= 1:
            raise ValueError(
                f"{name} must be between 0 and 1."
            )

        return value

    @staticmethod
    def _empty_result() -> Dict[str, Any]:
        return {
            "candidate_count": 0,
            "score_range": 0.0,
            "average_score": 0.0,
            "bias_indicators": [],
            "group_analysis": [],
        }