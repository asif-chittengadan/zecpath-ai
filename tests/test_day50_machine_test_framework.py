import pytest

from interview_ai.machine_test.machine_test_framework import (
    MachineTestFramework,
)


@pytest.fixture
def framework():
    return MachineTestFramework()


def test_supported_task_types(framework):
    assert framework.get_supported_task_types() == [
        "coding",
        "debugging",
        "file_based",
        "system_design",
    ]


def test_create_valid_coding_task(framework):
    task = framework.create_task(
        "MT-001",
        "Sum Two Numbers",
        "coding",
        "Write a function that returns the sum of two numbers.",
        30,
        input_data=[2, 3],
        expected_output=5,
    )

    assert task["task_id"] == "MT-001"
    assert task["task_type"] == "coding"
    assert task["time_limit_minutes"] == 30
    assert framework.validate_task(task) is True


def test_reject_unsupported_task_type(framework):
    with pytest.raises(ValueError):
        framework.create_task(
            "MT-002",
            "Unknown Task",
            "unsupported",
            "Description",
            20,
        )


def test_reject_invalid_time_limit(framework):
    with pytest.raises(ValueError):
        framework.create_task(
            "MT-003",
            "Debug Task",
            "debugging",
            "Fix the error.",
            0,
        )


def test_reject_missing_task_fields(framework):
    with pytest.raises(ValueError):
        framework.validate_task({
            "task_id": "MT-004",
            "task_type": "coding",
        })