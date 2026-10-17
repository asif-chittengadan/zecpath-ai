
import pytest

from scoring.recommendation import RecommendationAIEngine


@pytest.fixture
def engine():
    return RecommendationAIEngine(
        selection_threshold=75,
        review_threshold=50,
    )


@pytest.mark.parametrize(
    ("score", "expected_decision"),
    [
        (100, "Selected"),
        (75, "Selected"),
        (74.99, "Hold / Review"),
        (50, "Hold / Review"),
        (49.99, "Rejected"),
        (0, "Rejected"),
    ],
)
def test_score_boundary_decisions(
    engine, score, expected_decision
):
    result = engine.evaluate(score)

    assert result["decision"] == expected_decision


def test_high_score_with_failed_eligibility_is_rejected(engine):
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


def test_high_score_with_missing_information_requires_review(engine):
    result = engine.evaluate(
        95,
        eligibility_result={
            "failed_rules": [],
            "review_rules": ["Experience information unavailable"],
            "missing_mandatory_skills": [],
        },
    )

    assert result["decision"] == "Hold / Review"
    assert result["human_review_required"] is True


@pytest.mark.parametrize(
    "risk_type",
    ["behavior_risk", "integrity_risk"],
)
def test_high_score_with_high_risk_requires_review(
    engine, risk_type
):
    result = engine.evaluate(
        95,
        **{risk_type: {"risk_level": "HIGH"}},
    )

    assert result["decision"] == "Hold / Review"
    assert result["human_review_required"] is True


def test_low_risk_does_not_force_review_by_itself(engine):
    result = engine.evaluate(
        90,
        integrity_risk={"risk_level": "LOW"},
    )

    assert result["decision"] == "Selected"


def test_output_contains_explanation_and_thresholds(engine):
    result = engine.evaluate(80)

    assert result["reasons"]
    assert result["thresholds"] == {
        "selection": 75,
        "review": 50,
    }
    assert "risk_factors" in result
    assert "eligibility" in result
