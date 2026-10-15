
import json

from scoring.final_recommendation_generator import FinalRecommendationGenerator


def test_report_contains_decision_reasons(tmp_path):
    generator = FinalRecommendationGenerator(
        output_path=tmp_path / "report.json"
    )

    result = generator.generate(
        candidate_id="C52-003",
        candidate_name="Demo Candidate",
        role="Software Developer",
        unified_score=65,
    )

    assert result["decision"] == "Hold / Review"
    assert result["reasons"]
    assert 0 <= result["confidence_score"] <= 100
    assert result["thresholds"]["selection"] == 75
    assert result["thresholds"]["review"] == 50


def test_report_includes_eligibility_and_risk_fields(tmp_path):
    generator = FinalRecommendationGenerator(
        output_path=tmp_path / "report.json"
    )

    result = generator.generate(
        candidate_id="C52-004",
        candidate_name="Demo Candidate",
        role="Software Developer",
        unified_score=90,
        eligibility_result={
            "failed_rules": [],
            "review_rules": [],
            "missing_mandatory_skills": [],
        },
        integrity_risk={"risk_level": "HIGH"},
    )

    assert result["decision"] == "Hold / Review"
    assert "risk_factors" in result
    assert "eligibility" in result
    assert result["human_review_required"] is True


def test_saved_report_matches_result(tmp_path):
    output_path = tmp_path / "final_report.json"
    generator = FinalRecommendationGenerator(output_path=output_path)

    result = generator.generate(
        candidate_id="C52-005",
        candidate_name="Demo Candidate",
        role="Software Developer",
        unified_score=90,
    )

    saved = json.loads(output_path.read_text(encoding="utf-8"))

    assert saved["decision"] == result["decision"]
    assert saved["reasons"] == result["reasons"]
    assert saved["confidence_score"] == result["confidence_score"]
    assert saved["candidate_id"] == "C52-005"
