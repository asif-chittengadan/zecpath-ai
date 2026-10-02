from interview_ai.hr.adaptive_follow_up_engine import AdaptiveFollowUpEngine


def test_duplicate_follow_up_is_prevented():
    engine = AdaptiveFollowUpEngine()

    analysis = {
        "classification": "vague"
    }

    first_result = engine.decide(
        analysis,
        "career_journey"
    )

    second_result = engine.decide(
        analysis,
        "career_journey",
        previous_follow_up=first_result
    )

    assert first_result["follow_up_required"] is True
    assert first_result["question"] is not None

    assert second_result["follow_up_required"] is False
    assert second_result["trigger"] == "none"
    assert second_result["question"] is None
    assert second_result["reason"] == "Duplicate follow-up prevented."


def test_normal_follow_up_is_still_generated():
    engine = AdaptiveFollowUpEngine()

    analysis = {
        "classification": "vague"
    }

    result = engine.decide(
        analysis,
        "career_journey"
    )

    assert result["follow_up_required"] is True
    assert result["trigger"] == "deepening"
    assert result["question"] is not None