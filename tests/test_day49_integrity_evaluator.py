from interview_ai.integrity.integrity_evaluator import IntegrityEvaluator


def test_integrated_integrity_evaluation():
    observations = {
        "tab_switching": 3,
        "screen_focus_loss": 0,
        "external_voice": 0,
        "repeated_looking_away": 0,
    }

    result = IntegrityEvaluator().evaluate(observations)

    assert result["decision"] == "REVIEW_REQUIRED"
    assert "tab_switching" in result["risk_tags"]
    assert result["signal_analysis"]["missing_signals"] == []
    assert result["human_review_required"] is True


def test_missing_observations_require_review():
    result = IntegrityEvaluator().evaluate({
        "tab_switching": 0,
    })

    assert result["detection_result"]["missing_signals"]
    assert result["human_review_required"] is True


def test_behavioral_result_is_integrated():
    behavioral = {
        "scoring_summary": {
            "overall_score": 82.94,
            "human_review_required": True,
        },
        "human_review_required": True,
    }

    result = IntegrityEvaluator().evaluate(
        {
            "tab_switching": 0,
            "screen_focus_loss": 0,
            "external_voice": 0,
            "repeated_looking_away": 0,
        },
        behavioral_result=behavioral,
    )

    assert result["behavioral_summary"] == behavioral
    assert result["human_review_required"] is True