# Day 61 - Decision Audit Log Plan

## Purpose

Keep a reviewable history of AI scores, recommendations, human reviews, and later corrections. The audit trail must show what produced a decision and who or which trusted service recorded it, without storing raw resumes, interview transcripts, or unnecessary personal information in the log.

## Current implementation and gaps

- `compliance/audit_logger.py` writes `score_generated` and `decision_generated` events as local JSON Lines files under `logs/audit/`.
- Events currently contain `candidate_id`, role, scores, weights, thresholds, decision reasons/risk factors, and whether human review is required. They do not include request correlation ID, model version, scoring-policy version, or a completed human-review outcome.
- `AuditLogger` opens the files directly. It does not call `AccessController`, authenticate a principal, encrypt records, restrict reads, apply retention, or provide tamper-evident verification.
- `config/access_control_policy.json` defaults to deny and grants `audit.write` to the AI processing service and `audit.read` to the compliance auditor. Those permissions are not yet enforced by `AuditLogger` or an audit storage service.
- `config/retention_policy.json` sets `audit_record` to 730 days with action `retain`. The `RetentionManager` evaluates policy and creates retention events; it does not delete files. Confirm whether the intended outcome is indefinite retention before implementing automated expiry behavior.

Therefore, current local JSONL files are audit records, but they should not be described or used as access-controlled production storage until an authorized storage boundary is connected.

## Event types

Use append-only, versioned events. A new event records a change; it never edits or replaces a prior AI decision.

| Event type | When to write it | Required detail |
| --- | --- | --- |
| `score_generated` | A scoring stage completes. | Score set, score scale, stage, role category, model/version, scoring-policy version, score-output validation status, event time, and correlation ID. |
| `decision_generated` | The recommendation engine returns a decision. | Decision, score reference, thresholds, structured reason codes, risk flags, model/version, policy version, and whether human review is required. |
| `human_review_completed` | An authorized reviewer records a completed review. | Reviewer identity from trusted authentication, review outcome, reviewed event ID, timestamp, role/stage, and controlled reason codes. |
| `decision_overridden` | A human changes or supersedes an AI recommendation. | Original decision event ID, new human decision, actor identity/role, timestamp, and a controlled override reason code. Preserve the original AI event unchanged. |
| `audit_access` | An audit record is read, searched, exported, or denied. | Trusted actor, permission/action, target event or bounded query, timestamp, result, and correlation ID. Do not recursively place audit payloads in this event. |
| `audit_retention_action` | A retention decision is applied. | Target opaque event/record reference, policy version, action, timestamp, and completion result. Do not include the candidate record body. |

## Version 2 event envelope

Keep existing version 1 events readable. Add a version 2 schema for new events and migrate consumers before changing writers. Use UTC ISO 8601 timestamps and unique event IDs.

| Field | Purpose |
| --- | --- |
| `schema_version` | Version of the audit event schema. |
| `event_id` | Unique immutable identifier for this event. |
| `event_type` | One of the event types above. |
| `recorded_at` | UTC timestamp, preserving the existing field name. |
| `candidate_ref` | Opaque or keyed-pseudonymous candidate reference; keep the identity mapping in the protected candidate store. |
| `request_id` | Correlates events from the same API request or command-line run. |
| `actor_type` / `actor_ref` | Trusted service or authenticated reviewer that performed the action; never accept actor identity from an untrusted request body. |
| `role_category` / `assessment_stage` | Context needed to interpret the result without putting raw job or candidate content in the event. |
| `model_name` / `model_version` | Exact model identity used to produce the score or recommendation. |
| `policy_version` | Scoring, threshold, or decision policy version used. |
| `input_refs` | Opaque references to protected records required for later review; do not copy source text into the event. |
| `output_summary` | Typed scores, decision, and validation status needed to explain the result. |
| `reason_codes` | Controlled codes for explanation and risk categories; avoid free-form candidate text. |
| `human_review_required` | Whether the AI result required a human review. |
| `supersedes_event_id` | Prior event being corrected or overridden, when applicable; retain the prior event. |
| `integrity` | Hash/signature or previous-event hash used by the selected tamper-evidence mechanism. |

Do not copy names, email addresses, phone numbers, resume text, transcript excerpts, authentication tokens, or unfiltered reviewer notes into audit events. If free-text explanations are required by a business process, store them as protected records and reference them with an opaque ID.

## Authorization and storage boundary

1. Put audit reads and writes behind an `AuditEventStore` or equivalent service. Call `AccessController.require_permission()` inside that service for every operation, using a `Principal` supplied by trusted authentication/session state.
2. Require `audit.write` for the configured AI processing identity and `audit.read` for the compliance auditor. Keep the policy's default-deny behavior. Do not grant audit access merely because a caller can view a dashboard.
3. Restrict the storage directory or service account to the audit writer and authorized audit-reader service. Encrypt audit records at rest and in backups; keep encryption keys outside the log files.
4. Use append-only durable storage. For a local prototype, use restricted file permissions and a single-writer process. For deployment, use an access-controlled central store with immutable retention or a verified hash chain/signature. The current in-process thread lock is not a multi-process integrity guarantee.
5. Log read, export, denied-access, policy-change, and retention actions to a separate protected security-event stream, with payload references rather than copied audit contents.

## Retention, correction, and integrity

- Treat the current `audit_record` policy (`730` days, action `retain`) as a configured rule that needs an explicit owner decision before automated deletion is built. Do not assume that `retention_days` means delete after that many days when the action is `retain`.
- Use the existing `RetentionManager` to evaluate and record retention decisions, then implement deletion or anonymization only after the policy owner confirms the required action and any legal-hold behavior.
- Preserve original score and decision events. Record corrections, human overrides, or rescoring as new events linked with `supersedes_event_id` or the original event ID.
- Detect missing sequence/hash links, invalid signatures, unauthorized access attempts, and write failures. If the required audit write fails, do not treat the associated decision as successfully finalized; raise the critical alert defined in `day61_alerting_rules.md`.
- Keep old schema versions readable for the configured retention life. Do not silently rewrite historical events during schema upgrades.

## Implementation sequence

1. Confirm retention semantics, audit readers/writers, and the trusted identity source.
2. Add a protected audit storage boundary and enforce `AUDIT_WRITE` / `AUDIT_READ` there.
3. Introduce versioned event types and correlation/model/policy identifiers while keeping version 1 records readable.
4. Add human-review and override events as append-only records.
5. Add integrity verification, durable writes, retention execution, access-event logging, and alerting.
6. Test denied reads/writes, write failures, schema compatibility, correction links, legal holds, retention decisions, and tamper detection before production data is used.

