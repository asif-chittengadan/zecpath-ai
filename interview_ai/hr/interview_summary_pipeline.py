from interview_ai.hr.interview_summary_generator import (
    InterviewSummaryGenerator
)
from interview_ai.hr.interview_risk_analyzer import (
    InterviewRiskAnalyzer
)
from interview_ai.hr.hr_performance_summary import (
    HRPerformanceSummary
)
from interview_ai.hr.hr_interview_report_generator import (
    HRInterviewReportGenerator
)


class InterviewSummaryPipeline:
    """
    Integrates the Day 39 interview summary components
    into one recruiter-ready reporting pipeline.
    """

    def __init__(self):
        self.summary_generator = InterviewSummaryGenerator()
        self.risk_analyzer = InterviewRiskAnalyzer()
        self.performance_summary = HRPerformanceSummary()
        self.report_generator = HRInterviewReportGenerator()

    def generate(
        self,
        candidate_name,
        strengths=None,
        weaknesses=None,
        cultural_fit_indicators=None,
        risk_flags=None,
        inconsistencies=None,
        overall_score=None,
        component_scores=None
    ):
        risk_analysis = self.risk_analyzer.analyze(
            inconsistencies=inconsistencies,
            risk_flags=risk_flags
        )

        performance = self.performance_summary.generate(
            overall_score=overall_score,
            component_scores=component_scores
        )

        summary = self.summary_generator.generate_summary(
            strengths=strengths,
            weaknesses=weaknesses,
            cultural_fit_indicators=cultural_fit_indicators,
            risk_flags=risk_analysis["risk_flags"],
            inconsistencies=risk_analysis["inconsistencies"],
            overall_hr_score=performance["overall_score"]
        )

        summary["risk_analysis"] = risk_analysis
        summary["overall_hr_performance"] = performance

        report = self.report_generator.generate_report(
            candidate_name=candidate_name,
            summary=summary
        )

        return {
            "candidate_name": candidate_name,
            "structured_summary": summary,
            "natural_language_report": report
        }