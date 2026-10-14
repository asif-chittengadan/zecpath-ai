
import json
from pathlib import Path

from scoring.unified_candidate_score import UnifiedCandidateScore
from scoring.unified_scoring_engine import UnifiedScoringEngine


class UnifiedCandidateScoreGenerator:
    DEFAULT_OUTPUT_PATH = (
        Path("data")
        / "unified_scores"
        / "unified_candidate_score.json"
    )

    def __init__(self, scoring_engine=None, output_path=None):
        self.scoring_engine = scoring_engine or UnifiedScoringEngine()
        self.output_path = Path(output_path or self.DEFAULT_OUTPUT_PATH)

    def generate(
        self,
        candidate_name,
        role,
        ats_score,
        screening_score,
        hr_interview_score,
        technical_interview_score=None,
        machine_test_score=None,
        candidate_id=None,
    ):
        result = self.scoring_engine.calculate_score(
            candidate_name=candidate_name,
            role=role,
            ats_score=ats_score,
            screening_score=screening_score,
            hr_interview_score=hr_interview_score,
            technical_interview_score=technical_interview_score,
            machine_test_score=machine_test_score,
        )

        score_object = UnifiedCandidateScore(
            candidate_id=candidate_id or candidate_name or "UNKNOWN",
            candidate_name=candidate_name or "Unknown",
            role=role or "Unknown",
            round_scores=result["round_scores"],
            normalized_scores=result["normalized_scores"],
            weights=result["weights"],
            weighted_scores=result["weighted_scores"],
            unified_score=result["unified_score"],
        )

        result.update(score_object.to_dict())
        result["explainability"] = self.scoring_engine.explanation_generator.generate(result)
        self.save(result)
        return result

    def save(self, result):
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        with self.output_path.open("w", encoding="utf-8") as file:
            json.dump(result, file, indent=4)
        return self.output_path
