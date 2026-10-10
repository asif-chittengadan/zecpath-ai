from interview_ai.behavioral_analysis_framework import (
    BehavioralAnalysisFramework,
)
from interview_ai.behavioral_scoring_model import (
    BehavioralScoringModel,
)


class BehavioralEvaluator:

    @classmethod
    def evaluate(cls, observations, signal_scores):
        mapped = BehavioralAnalysisFramework.map_observations(
            observations
        )

        scoring = BehavioralScoringModel.calculate_score(
            signal_scores
        )

        return {
            "signal_analysis": mapped,
            "scoring_summary": scoring,
            "limitations": [
                "Scores describe observable signals only.",
                "Missing observations are not treated as zero.",
                "No psychological or personality inference is performed.",
                "Human review is required.",
            ],
        }