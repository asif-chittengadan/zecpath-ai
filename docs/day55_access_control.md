# Day 55: Access Control

## Implemented control

`compliance/access_control.py` provides role-based authorization with
candidate-level assignment checks. `config/access_control_policy.json` is the
policy source. Unknown roles and permissions are rejected, and the policy
loader requires `default_effect` to be `deny`.

The application must build a `Principal` from a trusted authentication/session
layer. Never accept `subject_id`, role, or candidate assignments from an
untrusted request body. A recruiter or interviewer can access only candidate
IDs assigned to that principal. Trusted background services have broader
candidate scope only for their configured operations.

## Initial role permissions

| Role | Access allowed by policy | Candidate scope |
| --- | --- | --- |
| Candidate | Read own transcript/report; read and update own consent | Assigned candidate only |
| Recruiter | Read reports and scores | Assigned candidates only |
| Interviewer | Read transcripts | Assigned candidates only |
| Compliance auditor | Read audit and retention metadata; read consent records | Audit/retention are role-restricted; consent reads require a candidate ID |
| Consent service | Read and write consent records | Any candidate |
| Retention worker | Read retention state, manage retention, delete expired records | Any candidate |
| AI processing service | Read/write transcripts, write reports and scores, read consent, write audit events | Any candidate |
| Security admin | Manage the access policy | No candidate-record access |

Permissions not listed for a role are denied. This policy does not grant
recruiters access to raw transcripts or grant security administrators access to
candidate records.

## Use at a protected service boundary

```python
from compliance.access_control import (
    AccessController,
    Permission,
    Principal,
    Role,
)

access = AccessController()

# In the application, obtain these trusted fields from authenticated session
# state and server-side assignment records.
principal = Principal(
    subject_id="user-123",
    role=Role.RECRUITER,
    candidate_ids=frozenset({"CAND-000123"}),
)

access.require_permission(
    principal,
    Permission.REPORT_READ,
    candidate_id="CAND-000123",
)
```

Call `require_permission()` before each protected read, write, or delete. Keep
authorization checks inside the service that owns the data so UI visibility
rules cannot be bypassed by calling a lower-level endpoint.

## Current limitation

The repository does not yet authenticate users or maintain recruiter and
interviewer assignments. Existing report writers also do not call the new
authorization service. The policy and enforcement component are in place, but
the existing standalone scripts are not protected until a trusted identity
source and the secure storage boundary are connected.
