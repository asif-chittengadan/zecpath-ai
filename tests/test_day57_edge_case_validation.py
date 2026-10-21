import json
import math
from datetime import datetime as RealDateTime
from pathlib import Path

from parsers.resume_experience_extractor import ResumeExperienceExtractor
from scoring.candidate_matching_service import CandidateMatchingService
from scoring.fairness_masker import FairnessMasker
from scoring.resume_schema_adapter import ResumeSchemaAdapter
from screening_ai.edge_case_handler import EdgeCaseHandler
from screening_ai.response_quality_checker import ResponseQualityChecker


ROOT = Path(__file__).resolve().parents[1]


def _quality_rules():
    with (ROOT / "config" / "edge_case_rules.json").open(
        encoding="utf-8"
    ) as rules_file:
        return json.load(rules_file)


def test_response_quality_handles_malformed_metadata_safely():
    checker = ResponseQualityChecker(_quality_rules())

    assert checker.check("A valid answer", ["unexpected metadata"]) == {
        "valid": True,
        "issues": [],
        "answer": "A valid answer",
    }

    result = checker.check(
        "A valid answer",
        {"audio_confidence": "bad", "noise_score": math.nan},
    )

    assert result["issues"] == ["poor_audio", "background_noise"]


def test_edge_retry_handler_falls_back_for_corrupt_retry_count():
    handler = EdgeCaseHandler(_quality_rules())

    result = handler.handle(
        {"issues": ["poor_audio"]},
        {"poor_audio": "not-a-count"},
    )

    assert result["action"] == "safe_fallback"
    assert result["terminal"] is True


def test_resume_experience_normalizes_nonfinite_and_negative_totals():
    for experience in (
        {"total_months": math.nan},
        {"total_months": math.inf},
        {"total_months": -18},
        {"years": -2},
        {"years": "-2 years"},
    ):
        normalized = ResumeSchemaAdapter.to_ats_schema(
            {"experience": experience}
        )["Experience"]["total_experience"]

        assert normalized == {"years": 0.0, "months": 0, "total_months": 0}
        assert math.isfinite(normalized["years"])


def test_future_and_malformed_resume_dates_are_bounded(monkeypatch):
    class FrozenDateTime(RealDateTime):
        @classmethod
        def now(cls, tz=None):
            return cls(2025, 6, 15)

    monkeypatch.setattr(
        "parsers.resume_experience_extractor.datetime",
        FrozenDateTime,
    )
    extractor = ResumeExperienceExtractor.__new__(ResumeExperienceExtractor)
    dates = [
        None,
        {"start_date": "January 2025", "end_date": "December 2025"},
        {"start_date": "not a date", "end_date": "Present"},
    ]

    result = extractor.calculate_total_experience(dates, [])

    assert result["total_months"] == 6
    assert result["years"] == 0
    assert result["months"] == 6
    assert extractor.detect_gaps(dates) == []
    assert extractor.detect_overlaps(dates) == []


def test_empty_or_wrongly_typed_experience_dates_return_zero():
    extractor = ResumeExperienceExtractor.__new__(ResumeExperienceExtractor)

    assert extractor.calculate_total_experience(None, None)["total_months"] == 0
    assert extractor.calculate_total_experience("not a date list", [])["total_months"] == 0
    assert extractor.calculate_experience_duration(None, None) == ""
    assert extractor.calculate_total_experience(None, [None, "2 years"])[
        "total_months"
    ] == 24
    assert extractor.calculate_total_experience(None, "-2 years")[
        "total_months"
    ] == 0


def test_job_description_edge_types_are_normalized_before_scoring():
    class RecordingSemanticEngine:
        def calculate_skill_similarity(self, candidate_skills, required_skills):
            self.required_skills = required_skills
            return {"score": 0.0}

        def calculate_similarity(self, candidate_text, job_text):
            self.job_text = job_text
            return 0.0

    class RecordingScoreGenerator:
        def generate(self, **values):
            return values

    service = CandidateMatchingService.__new__(CandidateMatchingService)
    service.semantic_engine = RecordingSemanticEngine()
    service.score_generator = RecordingScoreGenerator()
    service.fairness_masker = FairnessMasker()

    result = service.generate_score(
        {},
        {
            "role": 42,
            "skills": "Python",
            "experience": None,
            "education": "Computer Science",
        },
    )

    assert service.semantic_engine.required_skills == ["Python"]
    assert service.semantic_engine.job_text == "Python Computer Science"
    assert result["role"] == ""
    assert result["experience_relevance"] == 1.0
    assert result["education_alignment"] == 0.0


def test_set_valued_resume_fields_are_sorted_for_stable_output():
    normalized = ResumeSchemaAdapter.to_ats_schema(
        {
            "skills": {"technical": {"SQL", "Python"}},
            "projects": {"Zeta", "Alpha"},
        }
    )

    assert normalized["Skills"]["technical"] == ["Python", "SQL"]
    assert normalized["Projects"] == ["Alpha", "Zeta"]
