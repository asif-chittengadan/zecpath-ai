import json
from pathlib import Path

from interview_ai.hr.hr_interview_simulation_runner import (
    HRInterviewSimulationRunner
)
from interview_ai.hr.hr_manual_evaluation_comparator import (
    HRManualEvaluationComparator
)
from interview_ai.hr.hr_scoring_inconsistency_analyzer import (
    HRScoringInconsistencyAnalyzer
)


class HRInterviewTestReportGenerator:
    """
    Runs HR interview simulations, compares AI evaluations
    against manual evaluations, analyzes inconsistencies,
    and produces a reusable test report.
    """

    DEFAULT_OUTPUT_PATH = (
        Path("data")
        / "interview_test_reports"
        / "hr_interview_test_report.json"
    )

    DEFAULT_MANUAL_SCORES = {
        "confident": {
            "answer_relevance": 82,
            "communication": 80,
            "confidence": 85,
            "consistency": 80,
        },
        "hesitant": {
            "answer_relevance": 65,
            "communication": 60,
            "confidence": 55,
            "consistency": 70,
        },
        "inexperienced": {
            "answer_relevance": 60,
            "communication": 65,
            "confidence": 55,
            "consistency": 65,
        },
        "overqualified": {
            "answer_relevance": 88,
            "communication": 82,
            "confidence": 85,
            "consistency": 88,
        },
    }

    def __init__(self, output_path=None):
        self.runner = HRInterviewSimulationRunner()
        self.comparator = HRManualEvaluationComparator()
        self.analyzer = HRScoringInconsistencyAnalyzer()

        self.output_path = (
            Path(output_path)
            if output_path
            else self.DEFAULT_OUTPUT_PATH
        )

    def generate(
        self,
        manual_scores=None,
        tolerance=5
    ):
        manual_scores = (
            manual_scores
            if manual_scores is not None
            else self.DEFAULT_MANUAL_SCORES
        )

        simulations = self.runner.run_all()

        candidate_reports = []

        total_difference = 0.0

        for simulation in simulations:
            candidate_type = simulation[
                "candidate_type"
            ]

            ai_scores = simulation[
                "normalized_scores"
            ]

            candidate_manual_scores = manual_scores.get(
                candidate_type,
                {}
            )

            comparison = self.comparator.compare(
                ai_scores=ai_scores,
                manual_scores=candidate_manual_scores,
                tolerance=tolerance
            )

            analysis = self.analyzer.analyze(
                comparison
            )

            total_difference += comparison[
                "average_difference"
            ]

            candidate_reports.append({
                "candidate_name":
                    simulation["candidate_name"],

                "candidate_type":
                    candidate_type,

                "ai_result":
                    simulation,

                "manual_scores":
                    candidate_manual_scores,

                "comparison":
                    comparison,

                "inconsistency_analysis":
                    analysis,
            })

        candidate_count = len(candidate_reports)

        overall_average_difference = round(
            total_difference / candidate_count,
            2
        ) if candidate_count else 0.0

        report = {
            "report_type":
                "HR Interview Test Report",

            "candidate_count":
                candidate_count,

            "tolerance":
                tolerance,

            "overall_accuracy_evaluation": {
                "average_difference":
                    overall_average_difference,

                "evaluation_basis":
                    "Average absolute difference between "
                    "AI and manual component scores."
            },

            "candidate_reports":
                candidate_reports,

            "improvement_recommendations":
                self._collect_recommendations(
                    candidate_reports
                ),
        }

        self.save_report(report)

        return report

    @staticmethod
    def _collect_recommendations(
        candidate_reports
    ):
        recommendations = []

        for candidate in candidate_reports:
            for recommendation in candidate[
                "inconsistency_analysis"
            ]["recommendations"]:
                if recommendation not in recommendations:
                    recommendations.append(
                        recommendation
                    )

        return recommendations

    def save_report(self, report):
        self.output_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        with self.output_path.open(
            "w",
            encoding="utf-8"
        ) as file:
            json.dump(
                report,
                file,
                indent=2
            )

        return self.output_path