
import json

from scoring.final_recommendation_generator import FinalRecommendationGenerator


def test_generates_and_saves_recommendation(tmp_path):
    output = tmp_path / "recommendation.json"
    generator = FinalRecommendationGenerator(output_path=output)

    result = generator.generate(
        candidate_id="CAND-052",
        candidate_name="Test Candidate",
        role="Software Developer",
        unified_score=90,
    )

    assert result["decision"] == "Selected"
    assert result["candidate_id"] == "CAND-052"
    assert result["human_review_required"] is False

    saved = json.loads(output.read_text(encoding="utf-8"))
    assert saved["unified_score"] == 90.0


def test_integrity_risk_changes_recommendation(tmp_path):
    generator = FinalRecommendationGenerator(
        output_path=tmp_path / "review.json"
    )

    result = generator.generate(
        candidate_id="CAND-053",
        candidate_name="Review Candidate",
        role="Software Developer",
        unified_score=90,
        integrity_risk={"risk_level": "HIGH"},
    )

    assert result["decision"] == "Hold / Review"
    assert result["human_review_required"] is True


def test_eligibility_failure_rejects_candidate(tmp_path):
    generator = FinalRecommendationGenerator(
        output_path=tmp_path / "rejected.json"
    )

    result = generator.generate(
        candidate_id="CAND-054",
        candidate_name="Ineligible Candidate",
        role="Software Developer",
        unified_score=95,
        eligibility_result={
            "failed_rules": ["Missing mandatory skills"],
            "review_rules": [],
            "missing_mandatory_skills": ["Python"],
        },
    )

    assert result["decision"] == "Rejected"
    assert "Missing mandatory skills" in result["reasons"]
