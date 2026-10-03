from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Optional


class ConsentType(str, Enum):
    """
    Consent categories used by the ZECPATH platform.

    Each consent type represents a distinct processing purpose.
    """

    RESUME_PROCESSING = "resume_processing"
    AI_SCREENING = "ai_screening"
    INTERVIEW_RECORDING = "interview_recording"
    TRANSCRIPT_PROCESSING = "transcript_processing"
    AI_EVALUATION = "ai_evaluation"
    DATA_RETENTION = "data_retention"


@dataclass(frozen=True)
class ConsentRecord:
    """
    Immutable record representing one candidate consent event.
    """

    candidate_id: str
    consent_type: ConsentType
    granted: bool
    policy_version: str
    timestamp: str
    source: str = "candidate_portal"
    withdrawal_reason: Optional[str] = None

    @classmethod
    def create(
        cls,
        candidate_id: str,
        consent_type: ConsentType,
        granted: bool,
        policy_version: str,
        source: str = "candidate_portal",
        withdrawal_reason: Optional[str] = None,
    ):
        if not candidate_id or not candidate_id.strip():
            raise ValueError("candidate_id cannot be empty.")

        if not policy_version or not policy_version.strip():
            raise ValueError("policy_version cannot be empty.")

        if not source or not source.strip():
            raise ValueError("source cannot be empty.")

        return cls(
            candidate_id=candidate_id.strip(),
            consent_type=consent_type,
            granted=bool(granted),
            policy_version=policy_version.strip(),
            timestamp=datetime.now(timezone.utc).isoformat(),
            source=source.strip(),
            withdrawal_reason=withdrawal_reason,
        )