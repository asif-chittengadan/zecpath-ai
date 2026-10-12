from interview_ai.integrity.integrity_detection_framework import (
    IntegrityDetectionFramework,
)
from interview_ai.integrity.malpractice_detection_logic import (
    MalpracticeDetectionLogic,
)
from interview_ai.integrity.risk_flagging_system import (
    RiskFlaggingSystem,
)


class IntegrityEvaluator:
    def __init__(self, thresholds=None):
        self.detector = MalpracticeDetectionLogic(thresholds)
        self.risk_system = RiskFlaggingSystem()

    def evaluate(self, observations, behavioral_result=None):
        signal_analysis = IntegrityDetectionFramework.analyze(
            observations
        )

        detection_result = self.detector.evaluate(observations)

        risk_report = self.risk_system.generate_report(
            detection_result,
            behavioral_result=behavioral_result,
        )

        risk_report["signal_analysis"] = signal_analysis
        risk_report["detection_result"] = detection_result

        return risk_report