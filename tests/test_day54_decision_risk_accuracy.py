
from scoring.recommendation import RecommendationAIEngine



def test_mandatory_skill_failure_overrides_high_score():
    engine = RecommendationAIEngine(
        selection_threshold=75,
        review_threshold=50,
    )

    result = engine.evaluate(
        95,
        eligibility_result={
            "failed_rules": ["Missing mandatory skills"],
            "review_rules": [],
            "missing_mandatory_skills": ["Python"],
        },
    )

    assert result["decision"] == "Rejected"
    assert "Missing mandatory skills" in result["reasons"]



def test_high_integrity_risk_requires_review():
    engine = RecommendationAIEngine(
        selection_threshold=75,
        review_threshold=50,
    )

    result = engine.evaluate(
        95,
        integrity_risk={"risk_level": "HIGH"},
    )

    assert result["decision"] == "Hold / Review"
    assert result["human_review_required"] is True


def test_high_behavior_risk_requires_review():
    engine = RecommendationAIEngine(
        selection_threshold=75,
        review_threshold=50,
    )

    result = engine.evaluate(
        95,
        behavior_risk={"risk_level": "HIGH"},
    )

    assert result["decision"] == "Hold / Review"
    assert result["human_review_required"] is True


def test_clean_high_score_can_be_selected():
    engine = RecommendationAIEngine(
        selection_threshold=75,
        review_threshold=50,
    )

    result = engine.evaluate(90)

    assert result["decision"] == "Selected"
    assert result["risk_factors"] == []
