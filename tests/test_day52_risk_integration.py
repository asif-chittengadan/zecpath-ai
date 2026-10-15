
from scoring.final_recommendation_generator import FinalRecommendationGenerator


def test_behavioral_evaluator_requires_review(tmp_path):
    generator = FinalRecommendationGenerator(
        output_path=tmp_path / "behavior.json"
    )

    result = generator.generate(
        candidate_id="C52-001",
        candidate_name="Demo Candidate",
        role="Software Developer",
        unified_score=90,
        behavioral_observations={
            "gaze_stability": 0.82,
            "head_movement": 4,
            "attention_patterns": 2,
            "nervous_gestures": 1,
        },
        behavioral_signal_scores={
            "gaze_stability": 82,
            "head_movement": 75,
            "attention_patterns": 90,
            "nervous_gestures": 80,
        },
    )

    assert result["behavioral_evaluation"] is not None
    assert result["decision"] == "Hold / Review"
    assert result["human_review_required"] is True


def test_integrity_evaluator_requires_review(tmp_path):
    generator = FinalRecommendationGenerator(
        output_path=tmp_path / "integrity.json"
    )

    result = generator.generate(
        candidate_id="C52-002",
        candidate_name="Demo Candidate",
        role="Software Developer",
        unified_score=90,
        integrity_observations={
            "tab_switching": 3,
            "screen_focus_loss": 0,
            "external_voice": 1,
            "repeated_looking_away": 4,
        },
    )

    assert result["integrity_evaluation"] is not None
    assert result["decision"] == "Hold / Review"
    assert result["human_review_required"] is True
