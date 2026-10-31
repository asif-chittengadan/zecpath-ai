
"""
ZECPATH AI - Hiring Intelligence Report Generator
Day 53: Combines candidate evaluation outputs and explains results.
"""

import json
import math
from pathlib import Path


class HiringIntelligenceReportGenerator:
    """Combines existing evaluation results into one candidate report."""

    DEFAULT_OUTPUT_PATH = (
        Path("data") / "hiring_reports" / "hiring_intelligence_report.json"
    )

    SECTIONS = (
        "ats_summary",
        "screening_results",
        "hr_insights",
        "technical_performance",
        "behavioral_flags",
    )

    def __init__(self):
        self.version = "1.1"

    @staticmethod
    def _as_dict(value):
        """Return a dictionary without inventing missing data."""
        return value if isinstance(value, dict) else {}

    @staticmethod
    def _as_list(value):
        """Normalize optional list fields."""
        if value is None:
            return []
        if isinstance(value, set):
            return sorted(value, key=str)
        if isinstance(value, (list, tuple)):
            return list(value)
        return [value]

    @staticmethod
    def _format_score(value):
        """Render numeric recruiter-facing scores with their 100-point scale."""
        if isinstance(value, bool):
            return str(value)

        try:
            score = float(value)
        except (TypeError, ValueError, OverflowError):
            return str(value)

        if not math.isfinite(score):
            return str(value)

        return f"{score:.2f} / 100"

    @classmethod
    def _collect_items(cls, sources, keys):
        """Collect unique, explicitly supplied summary items."""
        items = []

        for source in sources:
            source = cls._as_dict(source)

            for key in keys:
                values = source.get(key)
                if values is None:
                    continue

                for item in cls._as_list(values):
                    if item is None:
                        continue

                    if isinstance(item, dict):
                        text = item.get("message") or item.get("signal")
                        if text is None:
                            continue
                        text = str(text).strip()
                    else:
                        text = str(item).strip()

                    if text and text not in items:
                        items.append(text)

        return items

    @classmethod
    def _collect_from_evaluation(cls, evaluation, recommendation, keys):
        """Read summary fields from direct results and known report wrappers."""
        sources = []
        for result in list(evaluation.values()) + [recommendation]:
            result = cls._as_dict(result)
            sources.append(result)

            # Existing modules sometimes wrap their actual findings under one
            # of these stable keys (for example, InterviewSummaryPipeline).
            for wrapper_key in ("structured_summary", "summary"):
                wrapped = cls._as_dict(result.get(wrapper_key))
                if wrapped:
                    sources.append(wrapped)

        return cls._collect_items(sources, keys)

    @staticmethod
    def _append_details(lines, details, indent=0):
        """Append nested evaluation data as readable Markdown bullets."""
        prefix = "  " * indent
        if isinstance(details, dict):
            for key, value in details.items():
                label = str(key).replace("_", " ").capitalize()
                if isinstance(value, dict):
                    lines.append(f"{prefix}- **{label}:**")
                    HiringIntelligenceReportGenerator._append_details(
                        lines, value, indent + 1
                    )
                elif isinstance(value, (list, tuple, set)):
                    lines.append(f"{prefix}- **{label}:**")
                    values = sorted(value, key=str) if isinstance(value, set) else list(value)
                    if not values:
                        lines.append(f"{prefix}  - None supplied.")
                    for item in values:
                        if isinstance(item, dict):
                            lines.append(f"{prefix}  -")
                            HiringIntelligenceReportGenerator._append_details(
                                lines, item, indent + 2
                            )
                        else:
                            lines.append(
                                f"{prefix}  - {item if item is not None else 'Not provided'}"
                            )
                else:
                    rendered = "Not provided" if value is None else str(value)
                    lines.append(f"{prefix}- **{label}:** {rendered}")
        elif details is not None:
            lines.append(f"{prefix}- {details}")

    @staticmethod
    def _build_recruiter_summary(
        strengths,
        weaknesses,
        risk_indicators,
        recommendation,
        missing_sections,
    ):
        """Explain the supplied evidence without changing the decision."""
        decision = recommendation.get("decision", "Not available")
        reasons = recommendation.get("reasons", [])

        if isinstance(reasons, str):
            reasons = [reasons]
        elif not isinstance(reasons, (list, tuple)):
            reasons = []

        explanation = [
            str(reason).strip()
            for reason in reasons
            if reason is not None and str(reason).strip()
        ]

        if missing_sections:
            explanation.append(
                "Evaluation data is missing for: "
                + ", ".join(missing_sections)
                + "."
            )

        if risk_indicators:
            explanation.append(
                "One or more risk indicators require review."
            )

        if recommendation.get("human_review_required", True):
            explanation.append(
                "Human review is required before a final hiring decision."
            )

        if not explanation:
            explanation.append(
                "No decision rationale was supplied; review the available "
                "evaluation evidence before taking action."
            )

        return {
            "decision": decision,
            "explanation": explanation,
            "strength_count": len(strengths),
            "weakness_count": len(weaknesses),
            "risk_count": len(risk_indicators),
            "missing_sections": list(missing_sections),
            "human_review_required": recommendation.get(
                "human_review_required", True
            ),
        }

    def generate_report(
        self,
        candidate_id,
        candidate_name,
        role,
        ats_summary=None,
        screening_results=None,
        hr_insights=None,
        technical_performance=None,
        behavioral_flags=None,
        final_recommendation=None,
    ):
        """Build a unified and explainable candidate report."""

        evaluation = {
            "ats_summary": self._as_dict(ats_summary),
            "screening_results": self._as_dict(screening_results),
            "hr_insights": self._as_dict(hr_insights),
            "technical_performance": self._as_dict(
                technical_performance
            ),
            "behavioral_flags": self._as_dict(behavioral_flags),
        }

        recommendation = self._as_dict(final_recommendation)

        strengths = self._collect_from_evaluation(
            evaluation,
            recommendation,
            ("strengths", "candidate_strengths"),
        )

        weaknesses = self._collect_from_evaluation(
            evaluation,
            recommendation,
            ("weaknesses", "candidate_weaknesses"),
        )

        risk_indicators = self._collect_from_evaluation(
            evaluation,
            recommendation,
            (
                "risk_indicators",
                "risk_factors",
                "risk_flags",
                "risks",
                "flags",
                "alerts",
                "inconsistencies",
            ),
        )

        missing_sections = [
            section
            for section in self.SECTIONS
            if not evaluation[section]
        ]

        # Keep the complete Day 52 decision payload, including thresholds,
        # eligibility details, and risk factors. The report only summarizes it.
        recommendation_summary = dict(recommendation)
        recommendation_summary.setdefault("decision", "Not available")
        recommendation_summary["reasons"] = self._as_list(
            recommendation_summary.get("reasons")
        )
        if not isinstance(
            recommendation_summary.get("human_review_required"), bool
        ):
            recommendation_summary["human_review_required"] = True

        recruiter_summary = self._build_recruiter_summary(
            strengths,
            weaknesses,
            risk_indicators,
            recommendation_summary,
            missing_sections,
        )

        return {
            "report_type": "hiring_intelligence_report",
            "version": self.version,
            "candidate": {
                "candidate_id": candidate_id,
                "candidate_name": candidate_name or "Unknown",
                "role": role or "Unknown",
            },
            "evaluation": evaluation,
            "summary": {
                "strengths": strengths,
                "weaknesses": weaknesses,
                "risk_indicators": risk_indicators,
            },
            "final_recommendation": recommendation_summary,
            "recruiter_summary": recruiter_summary,
            "data_completeness": {
                section: bool(evaluation[section])
                for section in self.SECTIONS
            },
            "limitations": [
                "Only supplied evaluation results are included.",
                "Missing sections are not interpreted as zero scores.",
                "The generator does not recalculate evaluation scores.",
                "Explanations are based on supplied reasons and available data.",
                "Risk indicators are not proof of misconduct or unsuitability.",
                "The report supports recruiter review; it does not replace "
                "human hiring judgment.",
            ],
        }

    @staticmethod
    def render_markdown(report):
        """Render a complete report in a recruiter-friendly Markdown layout."""
        if not isinstance(report, dict):
            raise TypeError("report must be a dictionary")

        candidate = HiringIntelligenceReportGenerator._as_dict(
            report.get("candidate")
        )
        summary = HiringIntelligenceReportGenerator._as_dict(
            report.get("summary")
        )
        recommendation = HiringIntelligenceReportGenerator._as_dict(
            report.get("final_recommendation")
        )
        recruiter_summary = HiringIntelligenceReportGenerator._as_dict(
            report.get("recruiter_summary")
        )
        evaluation = HiringIntelligenceReportGenerator._as_dict(
            report.get("evaluation")
        )

        lines = [
            "# Hiring Intelligence Report",
            "",
            "## Candidate Profile",
            f"- **Candidate ID:** {candidate.get('candidate_id') or 'Not provided'}",
            f"- **Name:** {candidate.get('candidate_name') or 'Unknown'}",
            f"- **Role:** {candidate.get('role') or 'Unknown'}",
            "",
            "## Recruiter Summary",
            f"- **Recommendation:** {recruiter_summary.get('decision', 'Not available')}",
            f"- **Human review required:** "
            f"{'Yes' if recruiter_summary.get('human_review_required', True) else 'No'}",
            f"- **Strengths:** {recruiter_summary.get('strength_count', 0)}",
            f"- **Weaknesses:** {recruiter_summary.get('weakness_count', 0)}",
            f"- **Risk indicators:** {recruiter_summary.get('risk_count', 0)}",
            "",
            "### Explanation",
        ]
        notice = report.get("notice")
        if notice:
            lines = [lines[0], "", f"> {notice}", ""] + lines[2:]

        explanations = recruiter_summary.get("explanation", [])
        if not isinstance(explanations, (list, tuple)):
            explanations = [explanations]
        lines.extend(
            f"- {str(item)}" for item in explanations if item is not None
        )

        for title, key in (
            ("Strengths", "strengths"),
            ("Weaknesses", "weaknesses"),
            ("Risk Indicators", "risk_indicators"),
        ):
            lines.extend(("", f"## {title}"))
            items = summary.get(key, [])
            if not isinstance(items, (list, tuple)):
                items = [items]
            if items:
                lines.extend(f"- {item}" for item in items)
            else:
                lines.append("- None supplied.")

        lines.extend(("", "## Final Recommendation"))
        lines.append(
            "> Scores use a 0–100 scale. Decision confidence is a heuristic "
            "indicator, not a probability of candidate success."
        )
        lines.append("")
        lines.append(
            f"- **Decision:** {recommendation.get('decision', 'Not available')}"
        )
        for label, key in (
            ("Unified score", "unified_score"),
            ("Decision confidence", "confidence_score"),
            ("Human review required", "human_review_required"),
        ):
            if recommendation.get(key) is not None:
                value = recommendation[key]
                if key == "human_review_required":
                    value = "Yes" if value else "No"
                elif key in {"unified_score", "confidence_score"}:
                    value = HiringIntelligenceReportGenerator._format_score(
                        value
                    )
                lines.append(f"- **{label}:** {value}")

        reasons = recommendation.get("reasons", [])
        if not isinstance(reasons, (list, tuple)):
            reasons = [reasons]
        if reasons:
            lines.append("- **Reasons:**")
            lines.extend(f"  - {reason}" for reason in reasons if reason is not None)

        additional_recommendation_details = {
            key: value
            for key, value in recommendation.items()
            if key not in {
                "decision",
                "unified_score",
                "confidence_score",
                "human_review_required",
                "reasons",
            }
        }
        if additional_recommendation_details:
            lines.extend(("", "### Additional Decision Details"))
            HiringIntelligenceReportGenerator._append_details(
                lines, additional_recommendation_details
            )

        lines.extend(("", "## Evaluation Details"))
        completeness = HiringIntelligenceReportGenerator._as_dict(
            report.get("data_completeness")
        )
        section_titles = {
            "ats_summary": "ATS Summary",
            "screening_results": "Screening Results",
            "hr_insights": "HR Insights",
            "technical_performance": "Technical Performance",
            "behavioral_flags": "Behavioral Flags",
        }
        for section, result in evaluation.items():
            title = section_titles.get(
                section,
                section.replace("_", " ").title(),
            )
            lines.extend(("", f"### {title}"))
            status = (
                "Provided"
                if completeness.get(section, bool(result))
                else "Missing"
            )
            lines.append(f"**Data status:** {status}")
            if result:
                HiringIntelligenceReportGenerator._append_details(
                    lines, result
                )
            else:
                lines.append("No evaluation data was supplied for this section.")

        limitations = report.get("limitations", [])
        if limitations:
            lines.extend(("", "## Limitations"))
            lines.extend(f"- {item}" for item in limitations)

        return "\n".join(lines).rstrip() + "\n"

    def save_report(self, report, output_path=None, output_format=None):
        """Save a report as JSON or Markdown and return the written path."""
        path = Path(output_path or self.DEFAULT_OUTPUT_PATH)
        selected_format = (output_format or path.suffix.lstrip(".") or "json").lower()
        if selected_format in {"md", "markdown"}:
            selected_format = "markdown"
        elif selected_format != "json":
            raise ValueError("output_format must be 'json' or 'markdown'")

        expected_suffix = ".md" if selected_format == "markdown" else ".json"
        if path.suffix.lower() != expected_suffix:
            path = path.with_suffix(expected_suffix)

        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as file:
            if selected_format == "markdown":
                file.write(self.render_markdown(report))
            else:
                json.dump(report, file, indent=2, ensure_ascii=False, default=str)
                file.write("\n")
        return path

    def save_exports(
        self,
        report,
        output_directory=None,
        basename="hiring_intelligence_report",
    ):
        """Write both structured JSON and recruiter-readable Markdown exports."""
        output_directory = Path(
            output_directory or self.DEFAULT_OUTPUT_PATH.parent
        )
        json_path = self.save_report(
            report,
            output_directory / f"{basename}.json",
            output_format="json",
        )
        markdown_path = self.save_report(
            report,
            output_directory / f"{basename}.md",
            output_format="markdown",
        )
        return {"json": json_path, "markdown": markdown_path}
    @staticmethod
    def export_json(report, output_path):
        """Export a generated hiring report as formatted JSON."""
        from pathlib import Path

        if not isinstance(report, dict):
            raise TypeError("report must be a dictionary")

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with output_path.open("w", encoding="utf-8") as file:
            json.dump(report, file, indent=4, ensure_ascii=False)

        return output_path

    @staticmethod
    def export_markdown(report, output_path):
        """Export a generated hiring report as recruiter-readable Markdown."""
        from pathlib import Path

        if not isinstance(report, dict):
            raise TypeError("report must be a dictionary")

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            HiringIntelligenceReportGenerator.render_markdown(report),
            encoding="utf-8",
        )
        return output_path
