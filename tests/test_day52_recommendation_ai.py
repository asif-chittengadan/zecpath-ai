
import pytest

from scoring.recommendation import RecommendationAIEngine


@pytest.fixture
def engine():
    return RecommendationAIEngine()


def test_selected_candidate(engine):
    result = engine.evaluate(90)
    assert result["decision"] == "Selected"
    assert result["confidence_score"] > 0


def test_review_candidate(engine):
    result = engine.evaluate(65)
    assert result["decision"] == "Hold / Review"


def test_rejected_low_score(engine):
    result = engine.evaluate(30)
    assert result["decision"] == "Rejected"


def test_failed_eligibility_rejects(engine):
    result = engine.evaluate(
        90,
        eligibility_result={"failed_rules": ["Missing mandatory skills"]},
    )
    assert result["decision"] == "Rejected"


def test_integrity_risk_requires_review(engine):
    result = engine.evaluate(
        90,
        integrity_risk={"risk_level": "HIGH"},
    )
    assert result["decision"] == "Hold / Review"
    assert result["human_review_required"] is True


def test_invalid_score_rejected(engine):
    with pytest.raises(ValueError):
        engine.evaluate(101)


def test_output_is_explainable(engine):
    result = engine.evaluate(80)
    assert result["reasons"]
    assert "risk_factors" in result
    assert "eligibility" in result


def test_behavior_risk_requires_review(engine):
    result = engine.evaluate(
        90,
        behavior_risk={"risk_level": "HIGH"},
    )
    assert result["decision"] == "Hold / Review"
    assert result["human_review_required"] is True


def test_missing_eligibility_data_requires_review(engine):
    result = engine.evaluate(
        90,
        eligibility_result={
            "failed_rules": [],
            "review_rules": ["Experience information unavailable"],
            "missing_mandatory_skills": [],
        },
    )
    assert result["decision"] == "Hold / Review"
    assert result["human_review_required"] is True


def test_rejection_reason_is_returned(engine):
    result = engine.evaluate(
        30,
        eligibility_result={
            "failed_rules": ["Missing mandatory skills"],
            "review_rules": [],
            "missing_mandatory_skills": ["Python"],
        },
    )
    assert result["decision"] == "Rejected"
    assert "Missing mandatory skills" in result["reasons"]
    assert result["eligibility"]["missing_mandatory_skills"] == ["Python"]


def test_review_risk_factor_is_explained(engine):
    result = engine.evaluate(
        90,
        integrity_risk={"risk_level": "HIGH"},
    )
    assert result["risk_factors"]
    assert any("Integrity risk" in item for item in result["risk_factors"])
