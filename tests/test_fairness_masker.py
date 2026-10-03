import pytest

from scoring.fairness_masker import FairnessMasker


def test_protected_fields_are_removed():
    masker = FairnessMasker()

    candidate = {
        "name": "Candidate A",
        "age": 24,
        "gender": "Male",
        "nationality": "Indian",
        "skills": ["Python", "SQL"],
    }

    result = masker.mask_candidate(candidate)

    assert "age" not in result
    assert "gender" not in result
    assert "nationality" not in result


def test_job_relevant_fields_are_preserved():
    masker = FairnessMasker()

    candidate = {
        "name": "Candidate A",
        "skills": ["Python", "SQL"],
        "experience_years": 2,
        "education": "B.Tech IT",
    }

    result = masker.mask_candidate(candidate)

    assert result["name"] == "Candidate A"
    assert result["skills"] == ["Python", "SQL"]
    assert result["experience_years"] == 2
    assert result["education"] == "B.Tech IT"


def test_nested_protected_fields_are_removed():
    masker = FairnessMasker()

    candidate = {
        "profile": {
            "age": 25,
            "gender": "Female",
            "skills": ["Python"],
        },
        "experience": {
            "years": 3,
        },
    }

    result = masker.mask_candidate(candidate)

    assert "age" not in result["profile"]
    assert "gender" not in result["profile"]
    assert result["profile"]["skills"] == ["Python"]
    assert result["experience"]["years"] == 3


def test_original_candidate_is_not_modified():
    masker = FairnessMasker()

    candidate = {
        "name": "Candidate A",
        "age": 24,
        "gender": "Male",
        "skills": ["Python"],
    }

    original = {
        "name": "Candidate A",
        "age": 24,
        "gender": "Male",
        "skills": ["Python"],
    }

    masker.mask_candidate(candidate)

    assert candidate == original


def test_list_of_candidates_is_supported():
    masker = FairnessMasker()

    candidates = [
        {
            "name": "Candidate A",
            "age": 24,
            "skills": ["Python"],
        },
        {
            "name": "Candidate B",
            "gender": "Female",
            "skills": ["SQL"],
        },
    ]

    result = masker.mask_candidates(candidates)

    assert "age" not in result[0]
    assert "gender" not in result[1]
    assert result[0]["skills"] == ["Python"]
    assert result[1]["skills"] == ["SQL"]


def test_protected_field_detection():
    masker = FairnessMasker()

    candidate = {
        "name": "Candidate A",
        "gender": "Male",
    }

    assert masker.contains_protected_fields(candidate) is True


def test_clean_candidate_has_no_protected_fields():
    masker = FairnessMasker()

    candidate = {
        "name": "Candidate A",
        "skills": ["Python"],
        "experience_years": 2,
    }

    assert masker.contains_protected_fields(candidate) is False


def test_case_insensitive_field_matching():
    masker = FairnessMasker()

    candidate = {
        "AGE": 24,
        "Gender": "Male",
        "NaTiOnAlItY": "Indian",
    }

    result = masker.mask_candidate(candidate)

    assert "AGE" not in result
    assert "Gender" not in result
    assert "NaTiOnAlItY" not in result


def test_additional_protected_fields_are_supported():
    masker = FairnessMasker(
        additional_protected_fields={
            "employee_id"
        }
    )

    candidate = {
        "employee_id": "EMP001",
        "skills": ["Python"],
    }

    result = masker.mask_candidate(candidate)

    assert "employee_id" not in result
    assert result["skills"] == ["Python"]


def test_invalid_candidate_type_is_rejected():
    masker = FairnessMasker()

    with pytest.raises(TypeError):
        masker.mask_candidate(
            ["not", "a", "dictionary"]
        )