"""Role-based, candidate-scoped access checks for ZECPATH records."""

import json
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import FrozenSet, Optional


class Role(str, Enum):
    CANDIDATE = "candidate"
    RECRUITER = "recruiter"
    INTERVIEWER = "interviewer"
    COMPLIANCE_AUDITOR = "compliance_auditor"
    CONSENT_SERVICE = "consent_service"
    RETENTION_WORKER = "retention_worker"
    AI_PROCESSING_SERVICE = "ai_processing_service"
    SECURITY_ADMIN = "security_admin"


class Permission(str, Enum):
    TRANSCRIPT_READ = "transcript.read"
    TRANSCRIPT_WRITE = "transcript.write"
    REPORT_READ = "report.read"
    REPORT_WRITE = "report.write"
    SCORE_READ = "score.read"
    SCORE_WRITE = "score.write"
    CONSENT_READ = "consent.read"
    CONSENT_WRITE = "consent.write"
    AUDIT_READ = "audit.read"
    AUDIT_WRITE = "audit.write"
    RETENTION_READ = "retention.read"
    RETENTION_MANAGE = "retention.manage"
    RECORD_DELETE = "record.delete"
    ACCESS_POLICY_MANAGE = "access_policy.manage"


class AccessDeniedError(PermissionError):
    """Raised when the current principal is not allowed to perform an action."""


@dataclass(frozen=True)
class Principal:
    """Authenticated identity plus candidate assignments from a trusted caller.

    Do not construct this object from untrusted request fields. The
    authentication layer must supply the subject, role, and candidate scope.
    """

    subject_id: str
    role: Role
    candidate_ids: FrozenSet[str] = frozenset()

    def __post_init__(self):
        if not self.subject_id or not self.subject_id.strip():
            raise ValueError("subject_id cannot be empty.")

        if not isinstance(
            self.candidate_ids,
            (set, frozenset, list, tuple),
        ):
            raise TypeError("candidate_ids must be a collection of candidate IDs.")

        try:
            normalized_role = Role(self.role)
        except (TypeError, ValueError) as error:
            raise ValueError("role is not recognized.") from error

        normalized_candidate_ids = frozenset(
            str(candidate_id).strip()
            for candidate_id in self.candidate_ids
            if candidate_id is not None and str(candidate_id).strip()
        )

        object.__setattr__(self, "subject_id", self.subject_id.strip())
        object.__setattr__(self, "role", normalized_role)
        object.__setattr__(self, "candidate_ids", normalized_candidate_ids)


class AccessController:
    """Checks configured permissions and candidate-level assignment scope.

    The policy defaults to deny. This class authorizes an identity supplied by
    a trusted authentication layer; it does not authenticate users itself.
    """

    DEFAULT_POLICY_PATH = (
        Path("config") / "access_control_policy.json"
    )

    CANDIDATE_SCOPED_PERMISSIONS = frozenset(
        {
            Permission.TRANSCRIPT_READ.value,
            Permission.TRANSCRIPT_WRITE.value,
            Permission.REPORT_READ.value,
            Permission.REPORT_WRITE.value,
            Permission.SCORE_READ.value,
            Permission.SCORE_WRITE.value,
            Permission.CONSENT_READ.value,
            Permission.CONSENT_WRITE.value,
            Permission.RECORD_DELETE.value,
        }
    )

    VALID_SCOPES = frozenset({"assigned", "all", "none"})

    def __init__(self, policy_path=None):
        self.policy_path = Path(
            policy_path or self.DEFAULT_POLICY_PATH
        )
        self.policy = self._load_policy()

    def _load_policy(self):
        if not self.policy_path.exists():
            raise FileNotFoundError(
                f"Access-control policy was not found: {self.policy_path}"
            )

        with self.policy_path.open("r", encoding="utf-8") as file:
            policy = json.load(file)

        if not isinstance(policy, dict):
            raise ValueError("Access-control policy must be a JSON object.")

        if policy.get("default_effect") != "deny":
            raise ValueError("Access-control policy must default to deny.")

        roles = policy.get("roles")
        if not isinstance(roles, dict) or not roles:
            raise ValueError("Access-control policy must define roles.")

        known_permissions = {permission.value for permission in Permission}
        normalized_roles = {}

        for role_name, role_policy in roles.items():
            try:
                role = Role(role_name)
            except ValueError as error:
                raise ValueError(
                    f"Unknown role in access-control policy: {role_name}"
                ) from error

            if not isinstance(role_policy, dict):
                raise ValueError(f"Policy for role '{role_name}' must be an object.")

            permissions = role_policy.get("permissions")
            scope = role_policy.get("candidate_scope")

            if not isinstance(permissions, list):
                raise ValueError(
                    f"Permissions for role '{role_name}' must be a list."
                )

            unknown_permissions = set(permissions) - known_permissions
            if unknown_permissions:
                raise ValueError(
                    f"Unknown permissions for role '{role_name}': "
                    f"{sorted(unknown_permissions)}"
                )

            if scope not in self.VALID_SCOPES:
                raise ValueError(
                    f"Invalid candidate scope for role '{role_name}'."
                )

            if (
                scope == "none"
                and set(permissions) & self.CANDIDATE_SCOPED_PERMISSIONS
            ):
                raise ValueError(
                    f"Role '{role_name}' has candidate permissions but no scope."
                )

            normalized_roles[role.value] = {
                "permissions": frozenset(permissions),
                "candidate_scope": scope,
            }

        return {
            "version": policy.get("version", "1.0"),
            "roles": normalized_roles,
        }

    def is_allowed(
        self,
        principal: Principal,
        permission,
        candidate_id: Optional[str] = None,
    ) -> bool:
        """Return whether the principal may perform the requested operation."""

        if not isinstance(principal, Principal):
            return False

        try:
            permission_value = Permission(permission).value
        except (TypeError, ValueError):
            return False

        role_policy = self.policy["roles"].get(principal.role.value)
        if role_policy is None:
            return False

        if permission_value not in role_policy["permissions"]:
            return False

        if permission_value not in self.CANDIDATE_SCOPED_PERMISSIONS:
            return True

        if not candidate_id or not str(candidate_id).strip():
            return False

        scope = role_policy["candidate_scope"]
        if scope == "all":
            return True
        if scope != "assigned":
            return False

        return str(candidate_id).strip() in principal.candidate_ids

    def require_permission(
        self,
        principal: Principal,
        permission,
        candidate_id: Optional[str] = None,
    ) -> None:
        """Raise a generic denial when permission or candidate scope is absent."""

        if not self.is_allowed(
            principal=principal,
            permission=permission,
            candidate_id=candidate_id,
        ):
            raise AccessDeniedError("Access denied.")
