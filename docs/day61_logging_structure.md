# Day 61 - Logging Structure

## Purpose

Define a consistent, privacy-aware event format for following a hiring request through parsing, scoring, screening, interviews, and decision generation. Operational logs support debugging and performance analysis. Decision audit records remain a separate, access-controlled record.

## Current project state

- `utils/logger.py` writes application messages to `logs/app.log` using the standard Python logger and a plain-text format.
- `compliance/audit_logger.py` writes score and decision events as JSON Lines under `logs/audit/`. These records include candidate identifiers and decision details, so they must remain access-controlled.
- The repository does not currently contain an HTTP API route. HTTP request fields below describe what to log when an API boundary is added; they do not claim an API logger is already running.

## Common event envelope

Write one JSON object per line. Use UTC timestamps and stable event names so the same fields can be searched across components.

| Field | Required | Meaning |
| --- | --- | --- |
| `schema_version` | Yes | Version of this operational log schema, initially `1.0`. |
| `timestamp_utc` | Yes | Event time in ISO 8601 UTC format. |
| `event_id` | Yes | Unique identifier for this log event. |
| `event_type` | Yes | Stable name such as `pipeline.stage.completed` or `model.output.recorded`. |
| `level` | Yes | `INFO`, `WARNING`, or `ERROR`; reserve `DEBUG` for local development. |
| `component` | Yes | Module or service that emitted the event. |
| `request_id` | Yes | Correlation ID generated at the API boundary; use a `run_id` for command-line jobs. |
| `stage` | When relevant | Pipeline stage, such as `resume_parse`, `ats_score`, or `interview_evaluation`. |
| `status` | When relevant | `started`, `completed`, `failed`, or `retrying`. |
| `duration_ms` | On completion | Elapsed time for the operation, measured with a monotonic clock. |
| `error_code` | On failure | Stable, machine-readable failure category. |
| `exception_type` | On failure | Exception class only; do not copy unfiltered exception text into operational logs. |

## Event-specific fields

### API request events

When an API is introduced, record `http_method`, `route_template`, `status_code`, `duration_ms`, and `request_id`. Log route templates such as `/candidates/{candidate_id}/score`, not full URLs with identifiers or query values. Do not log request bodies, authorization headers, access tokens, resume text, or interview transcripts.

### Model output events

Record `model_name`, `model_version`, `task`, `output_type`, `output_valid`, `duration_ms`, and `audit_event_id` when the output is also captured by the audit logger. Operational logs should contain only a small result summary needed for troubleshooting. Full score breakdowns and decision reasons stay in the restricted audit files rather than being copied into general application logs.

### Error events

Record the common envelope plus `error_code`, `exception_type`, `retryable`, and `stage`. Use a safe, short message that describes the failure category. Keep any detailed diagnostic trace in a restricted development or incident channel after checking that it contains no candidate text or secrets.

## Example records

```json
{"schema_version":"1.0","timestamp_utc":"2026-10-27T10:15:30.125Z","event_id":"e1a8...","event_type":"pipeline.stage.completed","level":"INFO","component":"candidate_matching","request_id":"r7c2...","stage":"ats_score","status":"completed","duration_ms":42.6}
{"schema_version":"1.0","timestamp_utc":"2026-10-27T10:15:30.126Z","event_id":"b9d4...","event_type":"model.output.recorded","level":"INFO","component":"candidate_matching","request_id":"r7c2...","stage":"ats_score","model_name":"all-MiniLM-L6-v2","model_version":"configured-version","output_type":"candidate_score","output_valid":true,"audit_event_id":"a35f..."}
{"schema_version":"1.0","timestamp_utc":"2026-10-27T10:15:30.127Z","event_id":"c4f0...","event_type":"pipeline.stage.failed","level":"ERROR","component":"resume_parser","request_id":"r7c2...","stage":"resume_parse","status":"failed","error_code":"RESUME_PARSE_FAILED","exception_type":"ValueError","retryable":false}
```

The IDs above are illustrative placeholders, not real request or audit IDs.

## Privacy and audit separation

- Do not put names, email addresses, phone numbers, resume text, interview transcripts, credentials, or access tokens in operational logs.
- Do not use a candidate identifier as the operational correlation ID. Link to a decision record only through the restricted audit event ID when needed.
- Keep score and decision audit events in `logs/audit/` with access limited to authorized reviewers. Preserve the existing audit event format for compatibility; this proposed operational schema does not rename its `recorded_at` field.
- Apply the project's approved retention and deletion rules to both log classes. Avoid adding a new retention period in code or configuration until the policy is confirmed.

## Severity and handling

- `INFO`: stage start/completion and valid model outputs.
- `WARNING`: recoverable issue, retry, or output requiring human review.
- `ERROR`: terminal stage failure or unavailable dependency.
- Every completion event should include `duration_ms`; every failure should include a stable `error_code` and `request_id`/`run_id`.
- Use JSON Lines locally for development and forward the same schema to a centralized, access-controlled log sink in a deployed environment. Configure rotation and retention outside the scoring logic.

## Implementation boundary

This document defines the schema for the first Day 61 task. The current application logger and audit logger are identified above; converting runtime output to this schema and adding instrumentation at each pipeline boundary can follow after the structure is reviewed. API-specific events should be added when the repository has an API boundary.
