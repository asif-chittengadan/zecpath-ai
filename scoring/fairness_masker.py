from copy import deepcopy
from typing import Any, Dict


class FairnessMasker:
    """
    Removes protected demographic signals from candidate data before
    production scoring.

    The original candidate data is never modified.

    IMPORTANT:
    This component is intended to protect the production scoring
    pipeline from demographic attributes. It does not delete the
    original candidate record from storage.
    """

    PROTECTED_FIELDS = frozenset(
        {
            "age",
            "date_of_birth",
            "dob",
            "gender",
            "sex",
            "race",
            "ethnicity",
            "religion",
            "nationality",
            "marital_status",
            "disability",
            "photo",
            "profile_photo",
            "profile_image",
            "image",
            "gender_identity",
            "sexual_orientation",
        }
    )

    def __init__(self, additional_protected_fields=None):
        """
        Create a fairness masker.

        additional_protected_fields can be supplied when the application
        needs to protect additional fields for a specific deployment.
        """

        additional = additional_protected_fields or set()

        self.protected_fields = frozenset(
            field.lower().strip()
            for field in (
                set(self.PROTECTED_FIELDS)
                | set(additional)
            )
            if field and field.strip()
        )

    def mask_candidate(
        self,
        candidate: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Return a sanitized copy of a candidate record.

        Protected fields are removed recursively from dictionaries.
        Lists and nested structures are preserved where possible.
        """

        if not isinstance(candidate, dict):
            raise TypeError(
                "candidate must be a dictionary."
            )

        return self._mask_value(
            deepcopy(candidate)
        )

    def mask_candidates(self, candidates):
        """
        Sanitize a list of candidate records.
        """

        if not isinstance(candidates, list):
            raise TypeError(
                "candidates must be a list."
            )

        return [
            self.mask_candidate(candidate)
            for candidate in candidates
        ]

    def contains_protected_fields(
        self,
        candidate: Dict[str, Any],
    ) -> bool:
        """
        Check whether a candidate contains any protected field.

        This is useful for validation before sending candidate data
        to the scoring engine.
        """

        if not isinstance(candidate, dict):
            raise TypeError(
                "candidate must be a dictionary."
            )

        return self._contains_protected_field(
            candidate
        )

    def _mask_value(self, value):
        if isinstance(value, dict):
            sanitized = {}

            for key, item in value.items():
                normalized_key = str(key).strip().lower()

                if normalized_key in self.protected_fields:
                    continue

                sanitized[key] = self._mask_value(item)

            return sanitized

        if isinstance(value, list):
            return [
                self._mask_value(item)
                for item in value
            ]

        if isinstance(value, tuple):
            return tuple(
                self._mask_value(item)
                for item in value
            )

        return value

    def _contains_protected_field(
        self,
        value,
    ) -> bool:
        if isinstance(value, dict):
            for key, item in value.items():
                normalized_key = str(key).strip().lower()

                if normalized_key in self.protected_fields:
                    return True

                if self._contains_protected_field(item):
                    return True

            return False

        if isinstance(value, (list, tuple)):
            return any(
                self._contains_protected_field(item)
                for item in value
            )

        return False