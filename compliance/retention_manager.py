import json
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass(frozen=True)
class RetentionDecision:
    """
    Represents the result of a retention-policy evaluation.
    """

    record_id: str
    data_type: str
    created_at: str
    expires_at: str
    action: str
    expired: bool
    legal_hold: bool = False


@dataclass(frozen=True)
class RetentionEvent:
    """
    Audit-safe record of a retention action.

    Sensitive candidate data should never be placed inside this event.
    """

    record_id: str
    data_type: str
    action: str
    policy_version: str
    timestamp: str


class RetentionManager:
    """
    Configuration-driven data-retention manager for ZECPATH.

    The manager determines when a record reaches the end of its
    configured retention period.

    It does not directly delete database records or files. The caller
    decides how the returned retention decision should be executed.
    """

    DEFAULT_CONFIG_PATH = (
        Path("config") /
        "retention_policy.json"
    )

    VALID_ACTIONS = frozenset(
        {
            "delete",
            "anonymize",
            "retain",
        }
    )

    def __init__(self, config_path=None):

        if config_path is None:
            config_path = self.DEFAULT_CONFIG_PATH

        self.config_path = Path(config_path)

        self.config = self._load_config()

        self._validate_config()

    def _load_config(self) -> Dict[str, Any]:

        if not self.config_path.exists():
            raise FileNotFoundError(
                "Retention policy file was not found: "
                f"{self.config_path}"
            )

        with self.config_path.open(
            "r",
            encoding="utf-8",
        ) as file:

            config = json.load(file)

        if not isinstance(config, dict):
            raise ValueError(
                "Retention policy must contain a JSON object."
            )

        return config

    def _validate_config(self) -> None:

        version = self.config.get("version")

        if not isinstance(version, str) or not version.strip():
            raise ValueError(
                "Retention policy must contain a valid version."
            )

        policies = self.config.get("policies")

        if not isinstance(policies, dict) or not policies:
            raise ValueError(
                "Retention policy must contain policies."
            )

        default_action = self.config.get(
            "default_action"
        )

        if default_action not in self.VALID_ACTIONS:
            raise ValueError(
                "default_action must be one of: "
                f"{sorted(self.VALID_ACTIONS)}"
            )

        for data_type, policy in policies.items():

            if not isinstance(data_type, str) or not data_type.strip():
                raise ValueError(
                    "Retention policy contains an invalid data type."
                )

            if not isinstance(policy, dict):
                raise ValueError(
                    f"Policy for '{data_type}' must be an object."
                )

            retention_days = policy.get(
                "retention_days"
            )

            if (
                not isinstance(retention_days, int)
                or isinstance(retention_days, bool)
                or retention_days < 0
            ):
                raise ValueError(
                    f"Retention days for '{data_type}' "
                    "must be a non-negative integer."
                )

            action = policy.get(
                "action",
                default_action,
            )

            if action not in self.VALID_ACTIONS:
                raise ValueError(
                    f"Invalid retention action '{action}' "
                    f"for '{data_type}'."
                )

    @property
    def policy_version(self) -> str:
        return self.config["version"]

    def get_policy(
        self,
        data_type: str,
    ) -> Dict[str, Any]:

        if not data_type or not data_type.strip():
            raise ValueError(
                "data_type cannot be empty."
            )

        policies = self.config["policies"]

        policy = policies.get(
            data_type.strip()
        )

        if policy is None:
            raise KeyError(
                f"No retention policy exists for "
                f"data type '{data_type}'."
            )

        return policy

    def calculate_expiry(
        self,
        created_at: datetime,
        data_type: str,
    ) -> datetime:

        created_at = self._ensure_utc(
            created_at
        )

        policy = self.get_policy(
            data_type
        )

        return created_at + timedelta(
            days=policy["retention_days"]
        )

    def is_expired(
        self,
        created_at: datetime,
        data_type: str,
        now: Optional[datetime] = None,
    ) -> bool:

        now = self._ensure_utc(
            now or datetime.now(timezone.utc)
        )

        expires_at = self.calculate_expiry(
            created_at,
            data_type,
        )

        return now >= expires_at

    def evaluate(
        self,
        record_id: str,
        data_type: str,
        created_at: datetime,
        now: Optional[datetime] = None,
        legal_hold: bool = False,
    ) -> RetentionDecision:

        if not record_id or not record_id.strip():
            raise ValueError(
                "record_id cannot be empty."
            )

        created_at = self._ensure_utc(
            created_at
        )

        now = self._ensure_utc(
            now or datetime.now(timezone.utc)
        )

        policy = self.get_policy(
            data_type
        )

        expires_at = (
            created_at +
            timedelta(
                days=policy["retention_days"]
            )
        )

        expired = now >= expires_at

        action = policy.get(
            "action",
            self.config["default_action"],
        )

        # A legal hold prevents automated deletion or anonymization.
        if legal_hold and action in {
            "delete",
            "anonymize",
        }:
            action = "retain"

        return RetentionDecision(
            record_id=record_id.strip(),
            data_type=data_type.strip(),
            created_at=created_at.isoformat(),
            expires_at=expires_at.isoformat(),
            action=action,
            expired=expired,
            legal_hold=legal_hold,
        )

    def evaluate_records(
        self,
        records: List[Dict[str, Any]],
        now: Optional[datetime] = None,
    ) -> List[RetentionDecision]:

        if not isinstance(records, list):
            raise TypeError(
                "records must be a list."
            )

        decisions = []

        for record in records:

            if not isinstance(record, dict):
                raise TypeError(
                    "Each retention record must be a dictionary."
                )

            decisions.append(
                self.evaluate(
                    record_id=record["record_id"],
                    data_type=record["data_type"],
                    created_at=record["created_at"],
                    now=now,
                    legal_hold=record.get(
                        "legal_hold",
                        False,
                    ),
                )
            )

        return decisions

    def create_audit_event(
        self,
        decision: RetentionDecision,
        timestamp: Optional[datetime] = None,
    ) -> RetentionEvent:

        timestamp = self._ensure_utc(
            timestamp or datetime.now(timezone.utc)
        )

        action = (
            decision.action
            if decision.expired
            else "retain"
        )

        return RetentionEvent(
            record_id=decision.record_id,
            data_type=decision.data_type,
            action=action,
            policy_version=self.policy_version,
            timestamp=timestamp.isoformat(),
        )

    @staticmethod
    def _ensure_utc(
        value: datetime,
    ) -> datetime:

        if not isinstance(value, datetime):
            raise TypeError(
                "Datetime value must be a datetime instance."
            )

        if value.tzinfo is None:
            raise ValueError(
                "Datetime must include timezone information."
            )

        return value.astimezone(
            timezone.utc
        )