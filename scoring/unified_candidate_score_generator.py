import json
from pathlib import Path

from scoring.unified_scoring_engine import UnifiedScoringEngine


class UnifiedCandidateScoreGenerator:
    """
    Generates and stores the final unified candidate score.
    """

    DEFAULT_OUTPUT_PATH = (
        Path("data")
        / "unified_scores"
        / "unified_candidate_score.json"
    )

    def __init__(
        self,
        scoring_engine=None,
        output_path=None
    ):
        self.scoring_engine = (
            scoring_engine
            if scoring_engine is not None
            else UnifiedScoringEngine()
        )

        self.output_path = (
            Path(output_path)
            if output_path is not None
            else self.DEFAULT_OUTPUT_PATH
        )

    def generate(
        self,
        candidate_name,
        role,
        ats_score,
        screening_score,
        hr_interview_score
    ):
        result = self.scoring_engine.calculate_score(
            candidate_name=candidate_name,
            role=role,
            ats_score=ats_score,
            screening_score=screening_score,
            hr_interview_score=hr_interview_score
        )

        result["score_type"] = (
            "unified_candidate_score"
        )

        result["round_count"] = 3

        self.save(result)

        return result

    def save(self, result):
        self.output_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        with self.output_path.open(
            "w",
            encoding="utf-8"
        ) as file:
            json.dump(
                result,
                file,
                indent=4
            )

        return self.output_path