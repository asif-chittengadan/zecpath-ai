
from scoring.recommendation import RecommendationAIEngine


def test_selected_decision_has_explanation():
    engine = RecommendationAIEngine(
        selection_threshold=75,
        review_threshold=50,
    )

    result = engine.evaluate(90)

    assert result["decision"] == "Selected"
    assert result["reasons"]
    assert "thresholds" in result
    assert "risk_factors" in result


def test_review_decision_has_explanation():
    engine = RecommendationAIEngine(
        selection_threshold=75,
        review_threshold=50,
    )

    result = engine.evaluate(60)

    assert result["decision"] == "Hold / Review"
    assert result["reasons"]
    assert "thresholds" in result


def test_rejected_decision_has_explanation():
    engine = RecommendationAIEngine(
        selection_threshold=75,
        review_threshold=50,
    )

    result = engine.evaluate(30)

    assert result["decision"] == "Rejected"
    assert result["reasons"]
    assert "thresholds" in result


def test_decision_output_contains_eligibility_details():
    engine = RecommendationAIEngine(
        selection_threshold=75,
        review_threshold=50,
    )

    result = engine.evaluate(90)

    assert "eligibility" in result
    assert "failed_rules" in result["eligibility"]
    assert "review_rules" in result["eligibility"]
    assert "missing_mandatory_skills" in result["eligibility"]

def test_selected_decision_includes_explanation():
    engine = RecommendationAIEngine(
        selection_threshold=75,
        review_threshold=50,
    )

    result = engine.evaluate(90)

    assert result["decision"] == "Selected"
    assert "reasons" in result
    assert len(result["reasons"]) > 0


def test_review_decision_includes_explanation():
    engine = RecommendationAIEngine(
        selection_threshold=75,
        review_threshold=50,
    )

    result = engine.evaluate(60)

    assert result["decision"] == "Hold / Review"
    assert "reasons" in result
    assert len(result["reasons"]) > 0


def test_rejected_decision_includes_explanation():
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
    assert "reasons" in result
    assert len(result["reasons"]) > 0
