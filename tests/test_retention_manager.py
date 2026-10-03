from datetime import datetime, timezone

import pytest

from compliance.retention_manager import RetentionManager


def test_policy_version_is_loaded():
    manager = RetentionManager()

    assert manager.policy_version == "1.0"


def test_policy_can_be_retrieved():
    manager = RetentionManager()

    policy = manager.get_policy(
        "resume"
    )

    assert policy["retention_days"] == 365
    assert policy["action"] == "delete"


def test_expiry_date_is_calculated():
    manager = RetentionManager()

    created_at = datetime(
        2026,
        1,
        1,
        tzinfo=timezone.utc,
    )

    expiry = manager.calculate_expiry(
        created_at,
        "resume",
    )

    assert expiry == datetime(
        2027,
        1,
        1,
        tzinfo=timezone.utc,
    )


def test_record_is_not_expired_before_expiry():
    manager = RetentionManager()

    created_at = datetime(
        2026,
        1,
        1,
        tzinfo=timezone.utc,
    )

    now = datetime(
        2026,
        6,
        1,
        tzinfo=timezone.utc,
    )

    assert manager.is_expired(
        created_at,
        "resume",
        now,
    ) is False


def test_record_is_expired_after_retention_period():
    manager = RetentionManager()

    created_at = datetime(
        2026,
        1,
        1,
        tzinfo=timezone.utc,
    )

    now = datetime(
        2027,
        1,
        2,
        tzinfo=timezone.utc,
    )

    assert manager.is_expired(
        created_at,
        "resume",
        now,
    ) is True


def test_evaluate_returns_delete_for_expired_resume():
    manager = RetentionManager()

    created_at = datetime(
        2025,
        1,
        1,
        tzinfo=timezone.utc,
    )

    now = datetime(
        2026,
        10,
        3,
        tzinfo=timezone.utc,
    )

    decision = manager.evaluate(
        record_id="RES-001",
        data_type="resume",
        created_at=created_at,
        now=now,
    )

    assert decision.expired is True
    assert decision.action == "delete"
    assert decision.legal_hold is False


def test_active_record_is_retained():
    manager = RetentionManager()

    created_at = datetime(
        2026,
        9,
        1,
        tzinfo=timezone.utc,
    )

    now = datetime(
        2026,
        10,
        3,
        tzinfo=timezone.utc,
    )

    decision = manager.evaluate(
        record_id="RES-002",
        data_type="resume",
        created_at=created_at,
        now=now,
    )

    assert decision.expired is False
    assert decision.action == "delete"


def test_legal_hold_prevents_automated_delete():
    manager = RetentionManager()

    created_at = datetime(
        2025,
        1,
        1,
        tzinfo=timezone.utc,
    )

    now = datetime(
        2026,
        10,
        3,
        tzinfo=timezone.utc,
    )

    decision = manager.evaluate(
        record_id="RES-003",
        data_type="resume",
        created_at=created_at,
        now=now,
        legal_hold=True,
    )

    assert decision.expired is True
    assert decision.action == "retain"
    assert decision.legal_hold is True


def test_multiple_records_can_be_evaluated():
    manager = RetentionManager()

    records = [
        {
            "record_id": "RES-001",
            "data_type": "resume",
            "created_at": datetime(
                2025,
                1,
                1,
                tzinfo=timezone.utc,
            ),
        },
        {
            "record_id": "TR-001",
            "data_type": "transcript",
            "created_at": datetime(
                2026,
                9,
                1,
                tzinfo=timezone.utc,
            ),
        },
    ]

    now = datetime(
        2026,
        10,
        3,
        tzinfo=timezone.utc,
    )

    decisions = manager.evaluate_records(
        records,
        now=now,
    )

    assert len(decisions) == 2
    assert decisions[0].expired is True
    assert decisions[1].expired is False


def test_audit_event_contains_no_candidate_data():
    manager = RetentionManager()

    created_at = datetime(
        2025,
        1,
        1,
        tzinfo=timezone.utc,
    )

    now = datetime(
        2026,
        10,
        3,
        tzinfo=timezone.utc,
    )

    decision = manager.evaluate(
        record_id="RES-004",
        data_type="resume",
        created_at=created_at,
        now=now,
    )

    event = manager.create_audit_event(
        decision,
        timestamp=now,
    )

    assert event.record_id == "RES-004"
    assert event.data_type == "resume"
    assert event.action == "delete"
    assert event.policy_version == "1.0"

    assert not hasattr(
        event,
        "candidate_name",
    )

    assert not hasattr(
        event,
        "email",
    )


def test_invalid_data_type_is_rejected():
    manager = RetentionManager()

    created_at = datetime(
        2026,
        1,
        1,
        tzinfo=timezone.utc,
    )

    with pytest.raises(KeyError):
        manager.evaluate(
            record_id="RES-005",
            data_type="unknown_data_type",
            created_at=created_at,
        )


def test_naive_datetime_is_rejected():
    manager = RetentionManager()

    with pytest.raises(ValueError):
        manager.calculate_expiry(
            datetime(
                2026,
                1,
                1,
            ),
            "resume",
        )


def test_invalid_record_list_is_rejected():
    manager = RetentionManager()

    with pytest.raises(TypeError):
        manager.evaluate_records(
            "not a list"
        )