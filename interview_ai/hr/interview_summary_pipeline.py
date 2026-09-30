import json
from pathlib import Path

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
    Generates and stores recruiter-ready interview summaries.
    """

    DEFAULT_OUTPUT_PATH = (
        Path("data")
        / "interview_summaries"
        / "interview_summary.json"
    )

    def __init__(
        self,
        output_path=None
    ):
        self.summary_generator = InterviewSummaryGenerator()
        self.risk_analyzer = InterviewRiskAnalyzer()
        self.performance_summary = HRPerformanceSummary()
        self.report_generator = HRInterviewReportGenerator()

        self.output_path = Path(
            output_path
            if output_path is not None
            else self.DEFAULT_OUTPUT_PATH
        )

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

        result = {
            "candidate_name": candidate_name,
            "structured_summary": summary,
            "natural_language_report": report
        }

        self.save_output(result)

        return result

    def save_output(self, result):
        """
        Save the final interview summary output as JSON.
        """

        self.output_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        with self.output_path.open(
            "w",
            encoding="utf-8"
        ) as file:
            json.dump(
                result,
                file,
                indent=4,
                ensure_ascii=False
            )

        return self.output_path