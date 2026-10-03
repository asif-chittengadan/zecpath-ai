from typing import Dict, List, Optional

from compliance.models import ConsentRecord, ConsentType


class ConsentManager:
    """
    Manages candidate consent records for ZECPATH.

    Consent is stored as an append-only event history in memory.
    A database/persistent repository can be connected later without
    changing the public API of this manager.
    """

    def __init__(self, policy_version: str = "1.0"):
        if not policy_version or not policy_version.strip():
            raise ValueError("policy_version cannot be empty.")

        self.policy_version = policy_version.strip()

        self._records: Dict[
            str,
            List[ConsentRecord]
        ] = {}

    def grant_consent(
        self,
        candidate_id: str,
        consent_type: ConsentType,
        source: str = "candidate_portal",
    ) -> ConsentRecord:
        """
        Grant a specific consent type for a candidate.
        """

        record = ConsentRecord.create(
            candidate_id=candidate_id,
            consent_type=consent_type,
            granted=True,
            policy_version=self.policy_version,
            source=source,
        )

        self._store(record)

        return record

    def withdraw_consent(
        self,
        candidate_id: str,
        consent_type: ConsentType,
        reason: Optional[str] = None,
        source: str = "candidate_portal",
    ) -> ConsentRecord:
        """
        Withdraw a previously granted consent.

        Withdrawal creates a new event rather than deleting historical
        consent records.
        """

        record = ConsentRecord.create(
            candidate_id=candidate_id,
            consent_type=consent_type,
            granted=False,
            policy_version=self.policy_version,
            source=source,
            withdrawal_reason=reason,
        )

        self._store(record)

        return record

    def has_valid_consent(
        self,
        candidate_id: str,
        consent_type: ConsentType,
    ) -> bool:
        """
        Return True when the latest consent event for the requested
        candidate and consent type is granted.
        """

        records = self._records.get(candidate_id, [])

        matching_records = [
            record
            for record in records
            if record.consent_type == consent_type
        ]

        if not matching_records:
            return False

        latest_record = matching_records[-1]

        return latest_record.granted

    def get_consent_history(
        self,
        candidate_id: str,
        consent_type: Optional[ConsentType] = None,
    ) -> List[ConsentRecord]:
        """
        Return consent history for a candidate.

        If consent_type is supplied, only records for that consent
        category are returned.
        """

        records = list(
            self._records.get(candidate_id, [])
        )

        if consent_type is None:
            return records

        return [
            record
            for record in records
            if record.consent_type == consent_type
        ]

    def require_consent(
        self,
        candidate_id: str,
        consent_type: ConsentType,
    ) -> None:
        """
        Block processing when the required consent has not been granted.

        Raises PermissionError when consent is unavailable.
        """

        if not self.has_valid_consent(
            candidate_id,
            consent_type,
        ):
            raise PermissionError(
                "Required consent has not been granted "
                f"for '{consent_type.value}'."
            )

    def _store(
        self,
        record: ConsentRecord,
    ) -> None:
        """
        Store a consent event without modifying previous events.
        """

        if record.candidate_id not in self._records:
            self._records[record.candidate_id] = []

        self._records[
            record.candidate_id
        ].append(record)