import pytest

from interview_ai.integrity.integrity_detection_framework import (
    IntegrityDetectionFramework,
)


def test_all_integrity_signals_are_recorded():
    observations = {
        "tab_switching": 3,
        "screen_focus_loss": 2,
        "external_voice": 1,
        "repeated_looking_away": 4,
    }

    result = IntegrityDetectionFramework.analyze(observations)

    assert result["signals"]["tab_switching"]["observed_value"] == 3
    assert result["signals"]["screen_focus_loss"]["observed_value"] == 2
    assert result["signals"]["external_voice"]["observed_value"] == 1
    assert result["signals"]["repeated_looking_away"]["observed_value"] == 4
    assert result["missing_signals"] == []
    assert result["human_review_required"] is True


def test_missing_signals_are_reported():
    result = IntegrityDetectionFramework.analyze({
        "tab_switching": 2,
    })

    assert set(result["missing_signals"]) == {
        "screen_focus_loss",
        "external_voice",
        "repeated_looking_away",
    }


def test_negative_observation_is_rejected():
    with pytest.raises(ValueError):
        IntegrityDetectionFramework.analyze({
            "tab_switching": -1,
        })


def test_unknown_signal_is_rejected():
    with pytest.raises(ValueError):
        IntegrityDetectionFramework.analyze({
            "unknown_signal": 1,
        })


def test_non_dictionary_input_is_rejected():
    with pytest.raises(TypeError):
        IntegrityDetectionFramework.analyze([])