from datetime import datetime, timezone


class RiskFlaggingSystem:
    RISK_LEVELS = {
        0: "LOW",
        1: "LOW",
        2: "MEDIUM",
        3: "HIGH",
        4: "HIGH",
    }

    def generate_report(self, detection_result, behavioral_result=None):
        if not isinstance(detection_result, dict):
            raise TypeError("detection_result must be a dictionary")

        flags = detection_result.get("flags", [])
        if not isinstance(flags, list):
            raise ValueError("flags must be a list")

        count = len(flags)
        risk_level = self.RISK_LEVELS.get(count, "HIGH")

        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "risk_level": risk_level,
            "risk_tags": sorted({
                flag["signal"]
                for flag in flags
                if isinstance(flag, dict) and "signal" in flag
            }),
            "alerts": [
                {
                    "type": "INTEGRITY_REVIEW",
                    "signal": flag.get("signal"),
                    "message": (
                        f"Review required for signal: {flag.get('signal')}"
                    ),
                }
                for flag in flags
                if isinstance(flag, dict)
            ],
            "behavioral_summary_included": behavioral_result is not None,
            "behavioral_summary": behavioral_result,
            "human_review_required": bool(
                flags
                or detection_result.get("missing_signals")
                or (
                    isinstance(behavioral_result, dict)
                    and behavioral_result.get("human_review_required")
                )
            ),
            "decision": "REVIEW_REQUIRED" if flags else "NO_FLAGS_DETECTED",
        }