class InterviewRiskAnalyzer:
    """
    Identifies inconsistencies and risk flags from HR interview data.
    """

    def analyze(
        self,
        inconsistencies=None,
        risk_flags=None
    ):
        inconsistencies = self._clean_items(
            inconsistencies
        )

        risk_flags = self._clean_items(
            risk_flags
        )

        return {
            "inconsistencies": inconsistencies,
            "risk_flags": risk_flags,
            "inconsistency_count": len(inconsistencies),
            "risk_flag_count": len(risk_flags),
            "has_inconsistencies": bool(inconsistencies),
            "has_risk_flags": bool(risk_flags)
        }

    def _clean_items(self, items):
        if not isinstance(items, list):
            return []

        cleaned = []

        for item in items:
            if not isinstance(item, str):
                continue

            item = item.strip()

            if item and item not in cleaned:
                cleaned.append(item)

        return cleaned