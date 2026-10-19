import json
import threading
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4


class AuditLogger:
    _write_lock = threading.Lock()

    def __init__(self, log_directory="logs/audit"):
        self.log_directory = Path(log_directory)

    def log_score(self, candidate_id, score_result):
        event = self._base_event(
            "score_generated",
            candidate_id,
        )
        event.update({
            "role": score_result.get("role"),
            "round_count": score_result.get("round_count"),
            "round_scores": score_result.get("round_scores", {}),
            "normalized_scores": score_result.get(
                "normalized_scores", {}
            ),
            "weights": score_result.get("weights", {}),
            "weighted_scores": score_result.get(
                "weighted_scores", {}
            ),
            "unified_score": score_result.get("unified_score"),
            "score_type": score_result.get("score_type"),
        })

        return self._append_event(
            "score_events.jsonl",
            event,
        )

    def log_decision(
        self,
        candidate_id,
        role,
        decision_result,
    ):
        event = self._base_event(
            "decision_generated",
            candidate_id,
        )
        event.update({
            "role": role,
            "decision": decision_result.get("decision"),
            "unified_score": decision_result.get(
                "unified_score"
            ),
            "confidence_score": decision_result.get(
                "confidence_score"
            ),
            "thresholds": decision_result.get("thresholds", {}),
            "reasons": decision_result.get("reasons", []),
            "risk_factors": decision_result.get(
                "risk_factors", []
            ),
            "human_review_required": decision_result.get(
                "human_review_required"
            ),
        })

        return self._append_event(
            "decision_events.jsonl",
            event,
        )

    @staticmethod
    def _base_event(event_type, candidate_id):
        normalized_id = (
            str(candidate_id).strip()
            if candidate_id is not None
            else None
        )

        return {
            "schema_version": "1.0",
            "event_id": str(uuid4()),
            "event_type": event_type,
            "recorded_at": datetime.now(
                timezone.utc
            ).isoformat(),
            "candidate_id": normalized_id or None,
        }

    def _append_event(self, filename, event):
        self.log_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        log_path = self.log_directory / filename
        serialized_event = json.dumps(
            event,
            ensure_ascii=False,
            separators=(",", ":"),
            default=str,
        )

        with self._write_lock:
            with log_path.open("a", encoding="utf-8") as file:
                file.write(serialized_event + "\n")
                file.flush()

        return event