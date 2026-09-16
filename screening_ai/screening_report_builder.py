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
        behavioral_analysis=None
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
            )
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

        sentiment = behavioral_analysis.get(
            "sentiment",
            {}
        )

        if sentiment.get("sentiment") == "positive":
            strengths.append(
                "Positive sentiment detected."
            )

        for item in answer_results:
            if not isinstance(item, dict):
                continue

            if item.get("category") == "skills":
                answer = item.get(
                    "answer",
                    ""
                )

                if answer:
                    strengths.append(
                        "Relevant skills were confirmed "
                        "during screening."
                    )
                    break

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

            if str(
                item.get("category", "")
            ).lower() != "skills":
                continue

            extracted = item.get(
                "extracted_skills",
                []
            )

            if isinstance(extracted, list):
                skills.extend(extracted)

            answer = item.get(
                "answer",
                ""
            )

            if answer and not extracted:
                skills.append(answer)

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

        if not summary:
            return (
                "No major screening signals were "
                "identified from the available data."
            )

        return " ".join(summary)

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
        lines.append(
            f"- Name: {candidate.get('name', 'N/A')}"
        )
        lines.append(
            f"- Email: {candidate.get('email', 'N/A')}"
        )
        lines.append(
            f"- Role: {candidate.get('role', 'N/A')}"
        )

        lines.append("")
        lines.append("## Key Answers")

        key_answers = report.get(
            "key_answers",
            []
        )

        if key_answers:
            for item in key_answers:
                lines.append(
                    f"- **{item.get('category', 'General')}**: "
                    f"{item.get('answer', '')}"
                )
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

        lines.append(
            f"- Total Score: "
            f"{score.get('total_score', 'N/A')}"
        )

        lines.append(
            f"- Questions Evaluated: "
            f"{score.get('questions_evaluated', 0)}"
        )

        lines.append("")
        lines.append("## Communication Signals")

        communication = report.get(
            "communication_signals",
            {}
        )

        lines.append(
            f"- Communication Strength: "
            f"{communication.get('communication_strength', {}).get('score', 'N/A')}"
        )

        lines.append(
            f"- Sentiment: "
            f"{communication.get('sentiment', {}).get('sentiment', 'N/A')}"
        )

        lines.append(
            f"- Behavioral Strength: "
            f"{communication.get('behavioral_strength', {}).get('score', 'N/A')}"
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
        lines.append("## Skill Confirmations")

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
                "- No skills confirmed during screening."
            )

        lines.append("")
        lines.append("## Recruiter Summary")
        lines.append(
            report.get(
                "recruiter_summary",
                ""
            )
        )

        return "\n".join(lines)

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