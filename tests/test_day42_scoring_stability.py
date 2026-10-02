import math

import pytest

from scoring.unified_scoring_engine import UnifiedScoringEngine


def test_nan_score_is_rejected():
    engine = UnifiedScoringEngine()

    with pytest.raises(ValueError, match="finite number"):
        engine.calculate_score(
            candidate_name="Test Candidate",
            role="Software Developer",
            ats_score=math.nan,
            screening_score=8,
            hr_interview_score=90
        )


def test_infinite_score_is_rejected():
    engine = UnifiedScoringEngine()

    with pytest.raises(ValueError, match="finite number"):
        engine.calculate_score(
            candidate_name="Test Candidate",
            role="Software Developer",
            ats_score=math.inf,
            screening_score=8,
            hr_interview_score=90
        )


def test_role_weights_must_total_one():
    engine = UnifiedScoringEngine()

    with pytest.raises(ValueError, match="total 1.0"):
        engine._validate_role_weights({
            "ats": 0.50,
            "screening": 0.30,
            "hr_interview": 0.30
        })


def test_role_weights_must_be_between_zero_and_one():
    engine = UnifiedScoringEngine()

    with pytest.raises(ValueError, match="between 0 and 1"):
        engine._validate_role_weights({
            "ats": 1.10,
            "screening": 0.00,
            "hr_interview": -0.10
        })


def test_valid_role_weights_are_preserved():
    engine = UnifiedScoringEngine()

    weights = engine._validate_role_weights({
        "ats": 0.45,
        "screening": 0.20,
        "hr_interview": 0.35
    })

    assert weights == {
        "ats": 0.45,
        "screening": 0.20,
        "hr_interview": 0.35
    }


def test_unified_score_matches_weighted_scores():
    engine = UnifiedScoringEngine()

    result = engine.calculate_score(
        candidate_name="Test Candidate",
        role="Software Developer",
        ats_score=80,
        screening_score=8,
        hr_interview_score=90
    )

    weighted_total = round(
        result["weighted_scores"]["ats"]
        + result["weighted_scores"]["screening"]
        + result["weighted_scores"]["hr_interview"],
        2
    )

    assert result["unified_score"] == weighted_total
    assert result["hiring_fit_percentage"] == result["unified_score"]