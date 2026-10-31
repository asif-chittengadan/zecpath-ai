import json
import os


class ScreeningReportBuilder:

    def __init__(
        self,
        config_path="config/screening_report_rules.json"
    ):
        self.config = self._load_config(config_path)

    @staticmethod
    def _load_config(config_path):
        with open(
            config_path,
            "r",
            encoding="utf-8"
        ) as file:
            return json.load(file)

    def build_report(
        self,
        candidate=None,
        answer_results=None,
        screening_score=None,
        behavioral_analysis=None,
        review_flags=None,
        job_requirement_status=None
    ):
        candidate = candidate or {}
        answer_results = answer_results or []
        behavioral_analysis = (
            behavioral_analysis or {}
        )

        report = {
            "report_title": self.config.get(
                "report_title",
                "AI Screening Report"
            ),
            "candidate_information": (
                self._build_candidate_information(
                    candidate
                )
            ),
            "key_answers": self._build_key_answers(
                answer_results
            ),
            "screening_score": self._build_screening_score(
                screening_score
            ),
            "communication_signals": (
                self._build_communication_signals(
                    behavioral_analysis
                )
            ),
            "strengths": self._identify_strengths(
                answer_results,
                behavioral_analysis
            ),
            "risks": self._identify_risks(
                answer_results,
                screening_score,
                behavioral_analysis
            ),
            "missing_data": self._identify_missing_data(
                candidate,
                answer_results
            ),
            "salary_expectation": (
                self._extract_category_value(
                    answer_results,
                    "salary"
                )
                or self._extract_category_value(
                    answer_results,
                    "salary expectation"
                )
            ),
            "availability": (
                self._extract_category_value(answer_results, "joining_availability")
                or self._extract_category_value(answer_results, "availability")
                or self._extract_category_value(answer_results, "notice_period")
            ),
            "skill_confirmations": (
                self._extract_skill_confirmations(
                    answer_results
                )
            ),
            "review_flags": (
                review_flags
                if review_flags is not None
                else candidate.get("review_flags", [])
            ),
            "job_requirement_status": (
                job_requirement_status
                if job_requirement_status is not None
                else candidate.get("job_requirement_status")
            ),
        }

        report["recruiter_summary"] = (
            self._build_recruiter_summary(report)
        )

        return report

    @staticmethod
    def _build_candidate_information(candidate):
        return {
            "candidate_id": candidate.get("candidate_id", ""),
            "job_id": candidate.get("job_id", ""),
            "session_id": candidate.get("session_id", ""),
            "name": candidate.get("name", ""),
            "email": candidate.get("email", ""),
            "role": candidate.get("role", "")
        }

    @staticmethod
    def _build_key_answers(answer_results):
        key_answers = []

        for item in answer_results:
            if not isinstance(item, dict):
                continue

            question = item.get(
                "question",
                ""
            )

            answer = item.get(
                "answer",
                ""
            )

            category = item.get(
                "category",
                ""
            )

            if answer:
                key_answers.append(
                    {
                        "category": category,
                        "question": question,
                        "answer": answer
                    }
                )

        return key_answers

    @staticmethod
    def _build_screening_score(screening_score):
        if not screening_score:
            return {
                "total_score": None,
                "questions_evaluated": 0
            }

        return {
            "total_score": screening_score.get(
                "total_screening_score"
            ),
            "questions_evaluated": screening_score.get(
                "questions_evaluated",
                0
            ),
            "parameter_scores": (
                screening_score.get(
                    "parameter_scores",
                    {}
                )
            )
        }

    @staticmethod
    def _build_communication_signals(
        behavioral_analysis
    ):
        if not behavioral_analysis:
            return {}

        communication = behavioral_analysis.get(
            "communication",
            {}
        )

        sentiment = behavioral_analysis.get(
            "sentiment",
            {}
        )

        behavioral_strength = (
            behavioral_analysis.get(
                "communication_strength",
                {}
            )
        )

        return {
            "communication_strength": (
                communication.get(
                    "communication_strength",
                    {}
                )
            ),
            "hesitation": communication.get(
                "hesitation",
                {}
            ),
            "uncertainty": communication.get(
                "uncertainty",
                {}
            ),
            "contradictions": communication.get(
                "contradictions",
                {}
            ),
            "response_length": communication.get(
                "response_length",
                {}
            ),
            "response_pace": communication.get(
                "response_pace",
                {}
            ),
            "sentiment": sentiment,
            "behavioral_strength": behavioral_strength
        }

    def _identify_strengths(
        self,
        answer_results,
        behavioral_analysis
    ):
        strengths = []

        communication = behavioral_analysis.get(
            "communication",
            {}
        )

        communication_strength = (
            communication
            .get("communication_strength", {})
            .get("score")
        )

        if (
            communication_strength is not None
            and communication_strength >= 70
        ):
            strengths.append(
                "Strong communication signal."
            )

        return self._unique(strengths)

    def _identify_risks(
        self,
        answer_results,
        screening_score,
        behavioral_analysis
    ):
        risks = []

        thresholds = self.config.get(
            "risk_thresholds",
            {}
        )

        screening_threshold = thresholds.get(
            "low_screening_score",
            50
        )

        if screening_score:
            score = screening_score.get(
                "total_screening_score"
            )

            if (
                score is not None
                and score < screening_threshold
            ):
                risks.append(
                    "Screening score is below "
                    "the configured threshold."
                )

        communication = behavioral_analysis.get(
            "communication",
            {}
        )

        communication_strength = (
            communication
            .get("communication_strength", {})
            .get("score")
        )

        communication_threshold = thresholds.get(
            "low_communication_strength",
            50
        )

        if (
            communication_strength is not None
            and communication_strength
            < communication_threshold
        ):
            risks.append(
                "Communication strength is below "
                "the configured threshold."
            )

        sentiment = behavioral_analysis.get(
            "sentiment",
            {}
        )

        if sentiment.get("sentiment") == "negative":
            risks.append(
                "Negative sentiment signal detected."
            )

        uncertainty = communication.get(
            "uncertainty",
            {}
        )

        if uncertainty.get("detected"):
            risks.append(
                "Uncertainty signals detected "
                "in the response."
            )

        contradictions = communication.get(
            "contradictions",
            {}
        )

        if contradictions.get("detected"):
            risks.append(
                "Potential contradiction signal detected."
            )

        return self._unique(risks)

    def _identify_missing_data(
        self,
        candidate,
        answer_results
    ):
        missing = []

        data_status = {
            "salary": False,
            "availability": False,
            "skills": False,
            "experience": False
        }

        for item in answer_results:
            if not isinstance(item, dict):
                continue

            category = str(
                item.get("category", "")
            ).lower()

            answer = item.get(
                "answer",
                ""
            )

            if not self._has_value(answer):
                continue

            if category in {
                "salary",
                "salary expectation",
                "salary_expectation"
            }:
                data_status["salary"] = True

            elif category in {
                "availability",
                "notice period",
                "notice_period",
                "joining availability",
                "joining_availability"
            }:
                data_status["availability"] = True

            elif category in {
                "skills",
                "skill"
            }:
                data_status["skills"] = True

            elif category in {
                "experience",
                "experience requirements",
                "total experience",
                "total_experience_years"
            }:
                data_status["experience"] = True

        for category, available in data_status.items():
            if not available:
                missing.append(category)

        return missing

    @staticmethod
    def _extract_category_value(answer_results, category):
        target = (
            str(category)
            .strip()
            .lower()
            .replace("_", " ")
            .replace("-", " ")
        )

        for item in answer_results:
            if not isinstance(item, dict):
                continue

            current = (
                str(item.get("category", ""))
                .strip()
                .lower()
                .replace("_", " ")
                .replace("-", " ")
            )

            if current == target:
                answer = item.get("answer")
                if answer:
                    return answer

        return None

    @staticmethod
    def _extract_skill_confirmations(
        answer_results
    ):
        skills = []

        for item in answer_results:
            if not isinstance(item, dict):
                continue

            category = str(item.get("category", "")).strip().lower()
            if category not in {"skills", "skill"}:
                continue

            extracted = item.get(
                "extracted_skills",
                []
            )

            if isinstance(extracted, list):
                skills.extend(
                    skill.strip()
                    for skill in extracted
                    if isinstance(skill, str) and skill.strip()
                )

        return ScreeningReportBuilder._unique(
            skills
        )

    def _build_recruiter_summary(self, report):
        strengths = report.get(
            "strengths",
            []
        )

        risks = report.get(
            "risks",
            []
        )

        missing = report.get(
            "missing_data",
            []
        )
        review_flags = report.get("review_flags", [])
        job_requirement_status = report.get(
            "job_requirement_status"
        )

        summary = []

        if strengths:
            summary.append(
                "Strengths: "
                + "; ".join(strengths)
            )

        if risks:
            summary.append(
                "Risks: "
                + "; ".join(risks)
            )

        if missing:
            summary.append(
                "Missing data: "
                + ", ".join(missing)
            )

        if review_flags:
            summary.append(
                f"Needs review: {len(review_flags)} review flag(s) recorded."
            )

        if (
            isinstance(job_requirement_status, dict)
            and not job_requirement_status.get("available", False)
        ):
            summary.append(
                "Job requirements were unavailable; role alignment could not be assessed."
            )

        if not summary:
            return (
                "No major screening signals were "
                "identified from the available data."
            )

        return "\n".join(summary)

    @staticmethod
    def _has_value(value):
        if value is None:
            return False

        if isinstance(value, str):
            return value.strip().lower() not in {
                "",
                "unknown",
                "not provided",
                "not available",
                "n/a"
            }

        if isinstance(value, list):
            return len(value) > 0

        return True

    @staticmethod
    def _unique(values):
        return list(
            dict.fromkeys(values)
        )

    @staticmethod
    def _humanize_label(value):
        acronyms = {
            "ai": "AI",
            "api": "API",
            "ats": "ATS",
            "hr": "HR",
            "id": "ID",
            "sql": "SQL",
        }
        words = str(value or "general").replace("_", " ").replace("-", " ").split()
        return " ".join(
            acronyms.get(word.lower(), word.capitalize())
            for word in words
        )

    @staticmethod
    def _format_score(value):
        if isinstance(value, (int, float)):
            return f"{value:.2f} / 100"
        return "Not available"

    def to_markdown(self, report):
        lines = []

        lines.append(
            "# "
            + report.get(
                "report_title",
                "AI Screening Report"
            )
        )

        lines.append("")

        candidate = report.get(
            "candidate_information",
            {}
        )

        lines.append("## Candidate Information")
        for label, key in (
            ("Name", "name"),
            ("Email", "email"),
            ("Role", "role"),
            ("Candidate ID", "candidate_id"),
            ("Job ID", "job_id"),
            ("Session ID", "session_id"),
        ):
            value = candidate.get(key)
            lines.append(f"- {label}: {value if value else 'Not provided'}")

        lines.append("")
        lines.append("## Job Requirement Status")
        job_status = report.get("job_requirement_status")
        if not isinstance(job_status, dict):
            lines.append("Not assessed.")
        elif job_status.get("available"):
            lines.append("Job requirements are available for review.")
        else:
            lines.append(
                job_status.get("message")
                or "Job requirements were not available."
            )

        lines.append("")
        lines.append("## Key Answers")

        key_answers = report.get(
            "key_answers",
            []
        )

        if key_answers:
            for item in key_answers:
                category = self._humanize_label(
                    item.get("category") or "general"
                )
                question = str(item.get("question") or "").strip()
                answer = str(item.get("answer") or "").strip()
                lines.append(
                    f"### {category}"
                )
                if question:
                    lines.append(f"- Question / reference: {question}")
                lines.append(f"- Answer: {answer or 'Not provided'}")
                lines.append("")
        else:
            lines.append(
                "- No screening answers available."
            )

        lines.append("")
        lines.append("## Screening Score")

        score = report.get(
            "screening_score",
            {}
        )

        total_score = self._format_score(score.get("total_score"))
        lines.append(f"- Total score: {total_score}")

        lines.append(
            f"- Questions Evaluated: "
            f"{score.get('questions_evaluated', 0)}"
        )

        lines.append("")
        lines.append("## Review Flags")
        review_flags = report.get("review_flags", [])
        if review_flags:
            for flag in review_flags:
                if not isinstance(flag, dict):
                    continue
                reason = self._humanize_label(
                    flag.get("reason") or "review required"
                )
                reference = flag.get("question_id") or flag.get("transcript_id")
                line = f"- {reason}"
                if reference:
                    line += f" (reference: {reference})"
                if flag.get("confidence_level") is not None:
                    line += f"; confidence value: {flag['confidence_level']}"
                lines.append(line)
        else:
            lines.append("No review flags recorded.")

        lines.append("")
        lines.append("## Communication Signals")

        communication = report.get(
            "communication_signals",
            {}
        )

        lines.append(
            f"- Communication Strength: "
            f"{self._format_score(communication.get('communication_strength', {}).get('score'))}"
        )

        lines.append(
            f"- Sentiment: "
            f"{communication.get('sentiment', {}).get('sentiment', 'N/A')}"
        )

        lines.append(
            f"- Behavioral Strength: "
            f"{self._format_score(communication.get('behavioral_strength', {}).get('score'))}"
        )

        lines.append("")
        lines.append("## Strengths")

        strengths = report.get(
            "strengths",
            []
        )

        if strengths:
            lines.extend(
                f"- {item}"
                for item in strengths
            )
        else:
            lines.append(
                "- No strengths identified."
            )

        lines.append("")
        lines.append("## Risks")

        risks = report.get(
            "risks",
            []
        )

        if risks:
            lines.extend(
                f"- {item}"
                for item in risks
            )
        else:
            lines.append(
                "- No risks identified."
            )

        lines.append("")
        lines.append("## Missing Data")

        missing = report.get(
            "missing_data",
            []
        )

        if missing:
            lines.extend(
                f"- {item}"
                for item in missing
            )
        else:
            lines.append(
                "- No required data is missing."
            )

        lines.append("")
        lines.append("## Salary Expectation")
        lines.append(
            str(
                report.get(
                    "salary_expectation"
                )
                or "Not provided"
            )
        )

        lines.append("")
        lines.append("## Availability")
        lines.append(
            str(
                report.get(
                    "availability"
                )
                or "Not provided"
            )
        )

        lines.append("")
        lines.append("## Skills Extracted from Answers")

        skills = report.get(
            "skill_confirmations",
            []
        )

        if skills:
            lines.extend(
                f"- {skill}"
                for skill in skills
            )
        else:
            lines.append(
                "- No skills were extracted from screening answers."
            )

        lines.append("")
        lines.append("## Recruiter Summary")
        lines.append(
            report.get(
                "recruiter_summary",
                ""
            )
        )

        return "\n".join(lines) + "\n"

    def save_markdown(
        self,
        report,
        output_path
    ):
        directory = os.path.dirname(
            output_path
        )

        if directory:
            os.makedirs(
                directory,
                exist_ok=True
            )

        with open(
            output_path,
            "w",
            encoding="utf-8"
        ) as file:
            file.write(
                self.to_markdown(report)
            )
