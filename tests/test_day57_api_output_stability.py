import json
import math

import pytest

from scoring.ats_scoring_engine import ATSScoringEngine
from scoring.candidate_score_generator import CandidateScoreGenerator
from utils.json_output import write_json_atomic


def test_ats_score_components_always_return_finite_numbers():
    engine = ATSScoringEngine()

    result = engine.calculate_score(
        role="Data Analyst",
        skill_match=math.nan,
        experience_relevance=math.inf,
        education_alignment=None,
        semantic_similarity="invalid",
    )

    assert result["skill_match"] == 0.0
    assert result["experience_relevance"] == 1.0
    assert result["education_alignment"] == 0.0
    assert result["semantic_similarity"] == 0.0
    assert math.isfinite(result["overall_score"])
    json.dumps(result, allow_nan=False)


def test_candidate_score_response_has_same_shape_for_missing_inputs():
    generator = CandidateScoreGenerator()

    complete = generator.generate(
        candidate_name="A Candidate",
        role="Data Analyst",
        skill_match=0.7,
        experience_relevance=0.6,
        education_alignment=0.8,
        semantic_similarity=0.75,
    )
    sparse = generator.generate(
        candidate_name="A Candidate",
        role="Data Analyst",
    )

    assert sparse.keys() == complete.keys()
    assert sparse["components"].keys() == complete["components"].keys()
    assert all(isinstance(value, float) for value in sparse["components"].values())
    json.dumps(sparse, allow_nan=False)


def test_failed_json_write_keeps_existing_output_intact(tmp_path):
    output_path = tmp_path / "result.json"
    output_path.write_text('{"previous": true}\n', encoding="utf-8")

    with pytest.raises(ValueError):
        write_json_atomic(output_path, {"score": math.nan})

    assert json.loads(output_path.read_text(encoding="utf-8")) == {
        "previous": True
    }
    assert list(tmp_path.glob("*.tmp")) == []
