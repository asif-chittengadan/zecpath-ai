
class RecommendationAIEngine:
    DECISIONS = ("Selected", "Hold / Review", "Rejected")

    def __init__(self, selection_threshold=75, review_threshold=50):
        if not 0 <= review_threshold < selection_threshold <= 100:
            raise ValueError("Invalid recommendation thresholds.")

        self.selection_threshold = selection_threshold
        self.review_threshold = review_threshold

    def evaluate(
        self,
        unified_score,
        eligibility_result=None,
        behavior_risk=None,
        integrity_risk=None,
    ):
        score = self._validate_score(unified_score)
        eligibility_result = eligibility_result or {}
        behavior_risk = behavior_risk or {}
        integrity_risk = integrity_risk or {}

        reasons = []
        risk_factors = []

        failed_rules = eligibility_result.get("failed_rules", [])
        review_rules = eligibility_result.get("review_rules", [])

        if failed_rules:
            decision = "Rejected"
            reasons.extend(failed_rules)
        elif (
            review_rules
            or self._requires_review(behavior_risk)
            or self._requires_review(integrity_risk)
        ):
            decision = "Hold / Review"
            reasons.extend(review_rules)
            if self._requires_review(behavior_risk):
                risk_factors.append("Behavioral risk requires human review")
            if self._requires_review(integrity_risk):
                risk_factors.append("Integrity risk requires human review")
        elif score >= self.selection_threshold:
            decision = "Selected"
            reasons.append("Score meets the selection threshold.")
        elif score >= self.review_threshold:
            decision = "Hold / Review"
            reasons.append("Score falls within the review range.")
        else:
            decision = "Rejected"
            reasons.append("Score is below the review threshold.")

        if not reasons:
            reasons.append("Decision based on the configured score thresholds.")

        confidence = self._calculate_confidence(
            score, decision, bool(failed_rules or review_rules)
        )

        return {
            "decision": decision,
            "unified_score": score,
            "confidence_score": confidence,
            "thresholds": {
                "selection": self.selection_threshold,
                "review": self.review_threshold,
            },
            "risk_factors": risk_factors,
            "eligibility": {
                "failed_rules": failed_rules,
                "review_rules": review_rules,
                "missing_mandatory_skills": eligibility_result.get(
                    "missing_mandatory_skills", []
                ),
            },
            "reasons": reasons,
            "human_review_required": decision == "Hold / Review"
            or bool(risk_factors),
        }

    @staticmethod
    def _validate_score(score):
        if isinstance(score, bool):
            raise ValueError("Unified score must be numeric.")

        try:
            score = float(score)
        except (TypeError, ValueError):
            raise ValueError("Unified score must be numeric.") from None

        if not 0 <= score <= 100:
            raise ValueError("Unified score must be between 0 and 100.")

        return round(score, 2)

    @staticmethod
    def _requires_review(risk):
        if isinstance(risk, bool):
            return risk

        if isinstance(risk, (int, float)):
            return risk > 0

        if isinstance(risk, str):
            return risk.strip().lower() in {
                "high", "critical", "flagged", "review_required"
            }

        if isinstance(risk, dict):
            return (
                risk.get("human_review_required", False) is True
                or risk.get("risk_level", "").lower() in {"high", "critical"}
                or risk.get("decision") == "REVIEW_REQUIRED"
                or bool(risk.get("flags"))
            )

        return False

    @staticmethod
    def _calculate_confidence(score, decision, eligibility_uncertain):
        if eligibility_uncertain:
            return 60.0

        if decision == "Selected":
            return round(min(99.0, 70.0 + (score - 75.0) * 1.16), 2)

        if decision == "Rejected":
            return round(min(99.0, 70.0 + (50.0 - score) * 1.16), 2)

        return round(60.0 + abs(score - 62.5) * 0.4, 2)
