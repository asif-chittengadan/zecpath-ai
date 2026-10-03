from scoring.explainability import ExplanationGenerator


def sample_scoring_result():
    return {
        "candidate": "Candidate A",
        "role": "Python Developer",
        "round_scores": {
            "ats": 85,
            "screening": 80,
            "hr_interview": 90,
        },
        "normalized_scores": {
            "ats": 85,
            "screening": 80,
            "hr_interview": 90,
        },
        "weights": {
            "ats": 0.40,
            "screening": 0.25,
            "hr_interview": 0.35,
        },
        "weighted_scores": {
            "ats": 34.0,
            "screening": 20.0,
            "hr_interview": 31.5,
        },
        "unified_score": 85.5,
        "hiring_fit_percentage": 85.5,
    }


def test_explanation_is_generated():
    generator = ExplanationGenerator()

    result = generator.generate(
        sample_scoring_result()
    )

    assert result["score"] == 85.5
    assert result["hiring_fit_percentage"] == 85.5


def test_candidate_and_role_are_preserved():
    generator = ExplanationGenerator()

    result = generator.generate(
        sample_scoring_result()
    )

    assert result["candidate"] == "Candidate A"
    assert result["role"] == "Python Developer"


def test_score_breakdown_contains_all_rounds():
    generator = ExplanationGenerator()

    result = generator.generate(
        sample_scoring_result()
    )

    breakdown = result["score_breakdown"]

    assert len(breakdown) == 3

    rounds = {
        item["round"]
        for item in breakdown
    }

    assert rounds == {
        "ats",
        "screening",
        "hr_interview",
    }


def test_weighted_contributions_are_explained():
    generator = ExplanationGenerator()

    result = generator.generate(
        sample_scoring_result()
    )

    breakdown = {
        item["round"]: item
        for item in result["score_breakdown"]
    }

    assert breakdown["ats"][
        "weighted_contribution"
    ] == 34.0

    assert breakdown["screening"][
        "weighted_contribution"
    ] == 20.0

    assert breakdown["hr_interview"][
        "weighted_contribution"
    ] == 31.5


def test_job_relevant_evidence_is_supported():
    generator = ExplanationGenerator()

    result = generator.generate(
        sample_scoring_result(),
        skill_details={
            "matched": [
                "Python",
                "SQL",
            ],
            "missing": [
                "Docker",
            ],
        },
        experience_details={
            "required_years": 2,
            "candidate_years": 2,
        },
        education_details={
            "required": "B.Tech",
            "candidate": "B.Tech IT",
        },
    )

    evidence = result[
        "job_relevant_evidence"
    ]

    assert evidence["skills"]["matched"] == [
        "Python",
        "SQL",
    ]

    assert evidence["experience"][
        "candidate_years"
    ] == 2

    assert evidence["education"][
        "candidate"
    ] == "B.Tech IT"


def test_missing_optional_evidence_is_allowed():
    generator = ExplanationGenerator()

    result = generator.generate(
        sample_scoring_result()
    )

    assert result[
        "job_relevant_evidence"
    ] == {}


def test_summary_contains_score():
    generator = ExplanationGenerator()

    result = generator.generate(
        sample_scoring_result()
    )

    assert "85.5" in result["summary"]


def test_explanation_contains_limitations():
    generator = ExplanationGenerator()

    result = generator.generate(
        sample_scoring_result()
    )

    assert len(
        result["limitations"]
    ) >= 1


def test_generator_does_not_modify_scoring_result():
    generator = ExplanationGenerator()

    scoring_result = sample_scoring_result()

    original = scoring_result.copy()

    generator.generate(
        scoring_result
    )

    assert scoring_result == original


def test_invalid_scoring_result_is_rejected():
    generator = ExplanationGenerator()

    try:
        generator.generate({})
        assert False
    except ValueError:
        assert True