import pytest

from compliance.consent_manager import ConsentManager
from compliance.models import ConsentType


def test_consent_can_be_granted():
    manager = ConsentManager()

    record = manager.grant_consent(
        candidate_id="candidate_001",
        consent_type=ConsentType.AI_SCREENING,
    )

    assert record.granted is True
    assert record.candidate_id == "candidate_001"
    assert record.consent_type == ConsentType.AI_SCREENING
    assert record.policy_version == "1.0"


def test_granted_consent_is_valid():
    manager = ConsentManager()

    manager.grant_consent(
        candidate_id="candidate_001",
        consent_type=ConsentType.RESUME_PROCESSING,
    )

    assert manager.has_valid_consent(
        "candidate_001",
        ConsentType.RESUME_PROCESSING,
    ) is True


def test_missing_consent_is_invalid():
    manager = ConsentManager()

    assert manager.has_valid_consent(
        "candidate_001",
        ConsentType.AI_SCREENING,
    ) is False


def test_withdrawal_invalidates_consent():
    manager = ConsentManager()

    manager.grant_consent(
        candidate_id="candidate_001",
        consent_type=ConsentType.AI_SCREENING,
    )

    manager.withdraw_consent(
        candidate_id="candidate_001",
        consent_type=ConsentType.AI_SCREENING,
        reason="Candidate withdrew permission.",
    )

    assert manager.has_valid_consent(
        "candidate_001",
        ConsentType.AI_SCREENING,
    ) is False


def test_withdrawal_preserves_history():
    manager = ConsentManager()

    manager.grant_consent(
        candidate_id="candidate_001",
        consent_type=ConsentType.AI_SCREENING,
    )

    manager.withdraw_consent(
        candidate_id="candidate_001",
        consent_type=ConsentType.AI_SCREENING,
        reason="Candidate withdrew permission.",
    )

    history = manager.get_consent_history(
        "candidate_001",
        ConsentType.AI_SCREENING,
    )

    assert len(history) == 2
    assert history[0].granted is True
    assert history[1].granted is False


def test_require_consent_allows_processing_when_granted():
    manager = ConsentManager()

    manager.grant_consent(
        candidate_id="candidate_001",
        consent_type=ConsentType.AI_SCREENING,
    )

    manager.require_consent(
        "candidate_001",
        ConsentType.AI_SCREENING,
    )


def test_require_consent_blocks_processing_without_consent():
    manager = ConsentManager()

    with pytest.raises(PermissionError):
        manager.require_consent(
            "candidate_001",
            ConsentType.AI_SCREENING,
        )


def test_require_consent_blocks_processing_after_withdrawal():
    manager = ConsentManager()

    manager.grant_consent(
        candidate_id="candidate_001",
        consent_type=ConsentType.AI_SCREENING,
    )

    manager.withdraw_consent(
        candidate_id="candidate_001",
        consent_type=ConsentType.AI_SCREENING,
    )

    with pytest.raises(PermissionError):
        manager.require_consent(
            "candidate_001",
            ConsentType.AI_SCREENING,
        )


def test_invalid_candidate_id_is_rejected():
    manager = ConsentManager()

    with pytest.raises(ValueError):
        manager.grant_consent(
            candidate_id="",
            consent_type=ConsentType.AI_SCREENING,
        )


def test_invalid_policy_version_is_rejected():
    with pytest.raises(ValueError):
        ConsentManager(policy_version="")