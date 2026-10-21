
from pathlib import Path
from compliance.audit_logger import AuditLogger
from interview_ai.behavioral_evaluator import BehavioralEvaluator
from interview_ai.integrity.integrity_evaluator import IntegrityEvaluator
from scoring.recommendation import RecommendationAIEngine
from utils.json_output import write_json_atomic


class FinalRecommendationGenerator:
    DEFAULT_OUTPUT_PATH = (
        Path("data") / "recommendations" / "final_recommendations.json"
    )

    def __init__(self, engine=None, output_path=None, audit_logger=None):
        self.engine = engine or RecommendationAIEngine()
        self.integrity_evaluator = IntegrityEvaluator()
        self.output_path = Path(
            output_path or self.DEFAULT_OUTPUT_PATH
        )
        self.audit_logger = audit_logger or AuditLogger()

    def generate(
        self,
        candidate_id,
        candidate_name,
        role,
        unified_score,
        eligibility_result=None,
        behavior_risk=None,
        integrity_risk=None,
        behavioral_observations=None,
        behavioral_signal_scores=None,
        integrity_observations=None,
        audit_logger=None,
    ):
        behavioral_result = None

        if behavioral_observations is not None or behavioral_signal_scores is not None:
            if behavioral_observations is None:
                behavioral_observations = {}
            if behavioral_signal_scores is None:
                behavioral_signal_scores = {}

            behavioral_result = BehavioralEvaluator.evaluate(
                behavioral_observations,
                behavioral_signal_scores,
            )

            behavior_risk = behavior_risk or behavioral_result["scoring_summary"]

        if integrity_observations is not None:
            integrity_risk = self.integrity_evaluator.evaluate(
                integrity_observations,
                behavioral_result=behavioral_result,
            )

        recommendation = self.engine.evaluate(
            unified_score=unified_score,
            eligibility_result=eligibility_result,
            behavior_risk=behavior_risk,
            integrity_risk=integrity_risk,
        )

        result = {
            "candidate_id": candidate_id,
            "candidate_name": candidate_name,
            "role": role,
            **recommendation,
            "behavioral_evaluation": behavioral_result,
            "integrity_evaluation": integrity_risk,
        }
        (audit_logger or self.audit_logger).log_decision(
            candidate_id=candidate_id,
            role=role,
            decision_result=result,
        )

        self.save(result)
        return result

    def save(self, result):
        return write_json_atomic(self.output_path, result)
