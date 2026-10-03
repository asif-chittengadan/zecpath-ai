from scoring.unified_scoring_engine import UnifiedScoringEngine


def test_unified_score_contains_explainability():
    engine = UnifiedScoringEngine()

    result = engine.calculate_score(
        candidate_name="Candidate A",
        role="python_developer",
        ats_score=85,
        screening_score=8,
        hr_interview_score=90,
    )

    assert "explainability" in result


def test_explainability_matches_unified_score():
    engine = UnifiedScoringEngine()

    result = engine.calculate_score(
        candidate_name="Candidate A",
        role="python_developer",
        ats_score=85,
        screening_score=8,
        hr_interview_score=90,
    )

    explanation = result["explainability"]

    assert explanation["score"] == result["unified_score"]

    assert (
        explanation["hiring_fit_percentage"]
        == result["hiring_fit_percentage"]
    )


def test_explainability_contains_all_rounds():
    engine = UnifiedScoringEngine()

    result = engine.calculate_score(
        candidate_name="Candidate A",
        role="python_developer",
        ats_score=85,
        screening_score=8,
        hr_interview_score=90,
    )

    breakdown = result["explainability"]["score_breakdown"]

    rounds = {
        item["round"]
        for item in breakdown
    }

    assert rounds == {
        "ats",
        "screening",
        "hr_interview",
    }


def test_explainability_contains_weighted_contributions():
    engine = UnifiedScoringEngine()

    result = engine.calculate_score(
        candidate_name="Candidate A",
        role="python_developer",
        ats_score=85,
        screening_score=8,
        hr_interview_score=90,
    )

    breakdown = {
        item["round"]: item
        for item in result["explainability"]["score_breakdown"]
    }

    assert (
        breakdown["ats"]["weighted_contribution"]
        == result["weighted_scores"]["ats"]
    )

    assert (
        breakdown["screening"]["weighted_contribution"]
        == result["weighted_scores"]["screening"]
    )

    assert (
        breakdown["hr_interview"]["weighted_contribution"]
        == result["weighted_scores"]["hr_interview"]
    )


def test_explainability_has_summary():
    engine = UnifiedScoringEngine()

    result = engine.calculate_score(
        candidate_name="Candidate A",
        role="python_developer",
        ats_score=85,
        screening_score=8,
        hr_interview_score=90,
    )

    summary = result["explainability"]["summary"]

    assert isinstance(summary, str)
    assert len(summary) > 0


def test_explainability_does_not_change_score():
    engine = UnifiedScoringEngine()

    result = engine.calculate_score(
        candidate_name="Candidate A",
        role="python_developer",
        ats_score=85,
        screening_score=8,
        hr_interview_score=90,
    )

    explanation = result["explainability"]

    assert explanation["score"] == result["unified_score"]


def test_explainability_contains_limitations():
    engine = UnifiedScoringEngine()

    result = engine.calculate_score(
        candidate_name="Candidate A",
        role="python_developer",
        ats_score=85,
        screening_score=8,
        hr_interview_score=90,
    )

    limitations = result["explainability"]["limitations"]

    assert isinstance(limitations, list)
    assert len(limitations) > 0