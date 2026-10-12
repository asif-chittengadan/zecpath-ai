from interview_ai.integrity.risk_flagging_system import RiskFlaggingSystem


def test_flags_generate_alerts_and_risk_tags():
    result = RiskFlaggingSystem().generate_report({
        "flags": [
            {"signal": "tab_switching"},
            {"signal": "external_voice"},
        ],
        "missing_signals": [],
    })

    assert result["risk_level"] == "MEDIUM"
    assert result["risk_tags"] == ["external_voice", "tab_switching"]
    assert len(result["alerts"]) == 2
    assert result["human_review_required"] is True


def test_no_flags_returns_low_risk():
    result = RiskFlaggingSystem().generate_report({
        "flags": [],
        "missing_signals": [],
    })

    assert result["risk_level"] == "LOW"
    assert result["decision"] == "NO_FLAGS_DETECTED"
    assert result["human_review_required"] is False


def test_missing_signals_require_review():
    result = RiskFlaggingSystem().generate_report({
        "flags": [],
        "missing_signals": ["external_voice"],
    })

    assert result["human_review_required"] is True


def test_behavioral_result_is_included():
    behavioral = {
        "scoring_summary": {"overall_score": 82.94},
        "human_review_required": True,
    }

    result = RiskFlaggingSystem().generate_report(
        {"flags": [], "missing_signals": []},
        behavioral_result=behavioral,
    )

    assert result["behavioral_summary"] == behavioral
    assert result["behavioral_summary_included"] is True
    assert result["human_review_required"] is True


def test_four_flags_produce_high_risk():
    result = RiskFlaggingSystem().generate_report({
        "flags": [
            {"signal": "tab_switching"},
            {"signal": "screen_focus_loss"},
            {"signal": "external_voice"},
            {"signal": "repeated_looking_away"},
        ],
        "missing_signals": [],
    })

    assert result["risk_level"] == "HIGH"