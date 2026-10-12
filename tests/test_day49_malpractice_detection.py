import pytest

from interview_ai.integrity.malpractice_detection_logic import (
    MalpracticeDetectionLogic,
)


def test_threshold_flags_are_generated():
    result = MalpracticeDetectionLogic().evaluate({
        "tab_switching": 3,
        "screen_focus_loss": 0,
        "external_voice": 0,
        "repeated_looking_away": 0,
    })

    assert result["flag_count"] == 1
    assert result["flags"][0]["signal"] == "tab_switching"
    assert result["human_review_required"] is True


def test_values_below_threshold_are_not_flagged():
    result = MalpracticeDetectionLogic().evaluate({
        "tab_switching": 0,
        "screen_focus_loss": 0,
        "external_voice": 0,
        "repeated_looking_away": 0,
    })

    assert result["flags"] == []
    assert result["human_review_required"] is False


def test_missing_signals_are_reported():
    result = MalpracticeDetectionLogic().evaluate({
        "tab_switching": 1,
    })

    assert set(result["missing_signals"]) == {
        "screen_focus_loss",
        "external_voice",
        "repeated_looking_away",
    }
    assert result["human_review_required"] is True


def test_invalid_observation_is_rejected():
    with pytest.raises(ValueError):
        MalpracticeDetectionLogic().evaluate({
            "tab_switching": -1,
        })


def test_custom_threshold_is_supported():
    detector = MalpracticeDetectionLogic({
        "tab_switching": 5,
    })

    result = detector.evaluate({
        "tab_switching": 4,
    })

    assert result["flags"] == []