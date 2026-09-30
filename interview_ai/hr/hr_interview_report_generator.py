class HRInterviewReportGenerator:
    """
    Generates a recruiter-ready natural-language HR interview report.
    """

    def generate_report(
        self,
        candidate_name,
        summary,
        overall_score=None
    ):
        summary = (
            summary
            if isinstance(summary, dict)
            else {}
        )

        strengths = summary.get(
            "candidate_strengths",
            []
        )

        weaknesses = summary.get(
            "candidate_weaknesses",
            []
        )

        cultural_fit = summary.get(
            "cultural_fit_indicators",
            []
        )

        risk_flags = summary.get(
            "risk_flags",
            []
        )

        inconsistencies = summary.get(
            "inconsistencies",
            []
        )

        performance = summary.get(
            "overall_hr_performance",
            {}
        )

        score = (
            overall_score
            if overall_score is not None
            else performance.get("score")
        )

        sections = []

        sections.append(
            self._candidate_section(
                candidate_name
            )
        )

        sections.append(
            self._performance_section(
                score,
                performance
            )
        )

        sections.append(
            self._list_section(
                "Candidate Strengths",
                strengths,
                "No specific strengths were recorded."
            )
        )

        sections.append(
            self._list_section(
                "Candidate Weaknesses",
                weaknesses,
                "No specific weaknesses were recorded."
            )
        )

        sections.append(
            self._list_section(
                "Cultural Fit Indicators",
                cultural_fit,
                "No specific cultural fit indicators were recorded."
            )
        )

        sections.append(
            self._list_section(
                "Risk Flags",
                risk_flags,
                "No risk flags were recorded."
            )
        )

        sections.append(
            self._list_section(
                "Inconsistencies",
                inconsistencies,
                "No inconsistencies were identified."
            )
        )

        return "\n\n".join(sections)

    def _candidate_section(self, candidate_name):
        name = (
            candidate_name.strip()
            if isinstance(candidate_name, str)
            and candidate_name.strip()
            else "Candidate"
        )

        return f"HR Interview Report\nCandidate: {name}"

    def _performance_section(
        self,
        score,
        performance
    ):
        level = performance.get(
            "level",
            performance.get(
                "performance_level",
                "not_available"
            )
        )

        if score is None:
            score = performance.get(
                "score",
                performance.get(
                    "overall_score"
                )
            )

        if score is None:
            score_text = "Not available"
        else:
            try:
                score_text = f"{float(score):.2f}/100"
            except (TypeError, ValueError):
                score_text = "Not available"

        return (
            "Overall HR Performance\n"
            f"Score: {score_text}\n"
            f"Performance Level: {level}"
        )

    def _list_section(
        self,
        title,
        items,
        empty_message
    ):
        if not isinstance(items, list):
            items = []

        cleaned = [
            str(item).strip()
            for item in items
            if str(item).strip()
        ]

        if not cleaned:
            return f"{title}\n{empty_message}"

        lines = [title]

        for item in cleaned:
            lines.append(f"- {item}")

        return "\n".join(lines)