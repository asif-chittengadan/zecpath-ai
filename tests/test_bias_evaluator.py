from scoring.bias_evaluator import BiasEvaluator


def test_empty_candidate_list():
    evaluator = BiasEvaluator()

    result = evaluator.evaluate([])

    assert result["candidate_count"] == 0
    assert result["score_range"] == 0.0
    assert result["average_score"] == 0.0
    assert result["bias_indicators"] == []
    assert result["group_analysis"] == []


def test_scores_are_normalized():
    evaluator = BiasEvaluator()

    candidates = [
        {"candidate": "A", "score": 90},
        {"candidate": "B", "score": 70},
    ]

    result = evaluator.evaluate(candidates)

    assert result["candidate_count"] == 2
    assert result["score_range"] == 0.20
    assert result["average_score"] == 0.80


def test_large_score_variation_is_detected():
    evaluator = BiasEvaluator()

    candidates = [
        {"candidate": "A", "score": 0.95},
        {"candidate": "B", "score": 0.20},
    ]

    result = evaluator.evaluate(candidates)

    assert "Large score variation detected" in result[
        "bias_indicators"
    ]


def test_all_zero_scores_are_detected():
    evaluator = BiasEvaluator()

    candidates = [
        {"candidate": "A", "score": 0},
        {"candidate": "B", "score": 0},
    ]

    result = evaluator.evaluate(candidates)

    assert "All candidates received zero scores" in result[
        "bias_indicators"
    ]


def test_group_analysis_calculates_average_scores():
    evaluator = BiasEvaluator()

    candidates = [
        {
            "candidate": "A",
            "score": 0.90,
            "audit_group": "group_a",
        },
        {
            "candidate": "B",
            "score": 0.80,
            "audit_group": "group_a",
        },
        {
            "candidate": "C",
            "score": 0.60,
            "audit_group": "group_b",
        },
        {
            "candidate": "D",
            "score": 0.50,
            "audit_group": "group_b",
        },
    ]

    result = evaluator.evaluate(
        candidates,
        group_field="audit_group",
    )

    groups = {
        item["group"]: item
        for item in result["group_analysis"]
    }

    assert groups["group_a"]["average_score"] == 0.85
    assert groups["group_b"]["average_score"] == 0.55


def test_group_selection_rate_is_calculated():
    evaluator = BiasEvaluator(
        selection_threshold=0.50
    )

    candidates = [
        {
            "candidate": "A",
            "score": 0.90,
            "audit_group": "group_a",
        },
        {
            "candidate": "B",
            "score": 0.80,
            "audit_group": "group_a",
        },
        {
            "candidate": "C",
            "score": 0.40,
            "audit_group": "group_b",
        },
        {
            "candidate": "D",
            "score": 0.30,
            "audit_group": "group_b",
        },
    ]

    result = evaluator.evaluate(
        candidates,
        group_field="audit_group",
    )

    groups = {
        item["group"]: item
        for item in result["group_analysis"]
    }

    assert groups["group_a"]["selection_rate"] == 1.0
    assert groups["group_b"]["selection_rate"] == 0.0


def test_disparate_impact_flags_group_for_review():
    evaluator = BiasEvaluator()

    candidates = [
        {
            "candidate": "A",
            "score": 0.90,
            "audit_group": "group_a",
        },
        {
            "candidate": "B",
            "score": 0.80,
            "audit_group": "group_a",
        },
        {
            "candidate": "C",
            "score": 0.40,
            "audit_group": "group_b",
        },
        {
            "candidate": "D",
            "score": 0.30,
            "audit_group": "group_b",
        },
    ]

    result = evaluator.evaluate(
        candidates,
        group_field="audit_group",
    )

    groups = {
        item["group"]: item
        for item in result["group_analysis"]
    }

    assert groups["group_b"]["review_required"] is True
    assert groups["group_b"]["disparate_impact_ratio"] == 0.0


def test_missing_group_values_are_excluded_from_group_analysis():
    evaluator = BiasEvaluator()

    candidates = [
        {
            "candidate": "A",
            "score": 0.90,
            "audit_group": "group_a",
        },
        {
            "candidate": "B",
            "score": 0.80,
        },
    ]

    result = evaluator.evaluate(
        candidates,
        group_field="audit_group",
    )

    assert len(result["group_analysis"]) == 1
    assert result["group_analysis"][0]["group"] == "group_a"


def test_group_analysis_does_not_modify_scores():
    evaluator = BiasEvaluator()

    candidates = [
        {
            "candidate": "A",
            "score": 0.90,
            "audit_group": "group_a",
        },
        {
            "candidate": "B",
            "score": 0.50,
            "audit_group": "group_b",
        },
    ]

    original_scores = [
        candidate["score"]
        for candidate in candidates
    ]

    evaluator.evaluate(
        candidates,
        group_field="audit_group",
    )

    current_scores = [
        candidate["score"]
        for candidate in candidates
    ]

    assert current_scores == original_scores


def test_invalid_threshold_is_rejected():
    try:
        BiasEvaluator(
            disparate_impact_threshold=1.5
        )
        assert False
    except ValueError:
        assert True