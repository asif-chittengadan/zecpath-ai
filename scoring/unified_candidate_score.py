
from dataclasses import asdict, dataclass
from typing import Any


@dataclass
class UnifiedCandidateScore:
    candidate_id: str
    candidate_name: str
    role: str
    round_scores: dict[str, float]
    normalized_scores: dict[str, float]
    weights: dict[str, float]
    weighted_scores: dict[str, float]
    unified_score: float
    human_review_required: bool = True

    def __post_init__(self):
        if not isinstance(self.candidate_id, str) or not self.candidate_id.strip():
            raise ValueError("candidate_id must be a non-empty string")

        if not isinstance(self.candidate_name, str) or not self.candidate_name.strip():
            raise ValueError("candidate_name must be a non-empty string")

        if not isinstance(self.role, str) or not self.role.strip():
            raise ValueError("role must be a non-empty string")

        for field_name in (
            "round_scores",
            "normalized_scores",
            "weights",
            "weighted_scores",
        ):
            value = getattr(self, field_name)
            if not isinstance(value, dict):
                raise TypeError(f"{field_name} must be a dictionary")

        if not 0 <= self.unified_score <= 100:
            raise ValueError("unified_score must be between 0 and 100")

        if not isinstance(self.human_review_required, bool):
            raise TypeError("human_review_required must be a boolean")

    def to_dict(self) -> dict[str, Any]:
        result = asdict(self)
        result["hiring_fit_percentage"] = round(self.unified_score, 2)
        result["score_type"] = "unified_candidate_score"
        result["round_count"] = len(self.round_scores)
        return result
