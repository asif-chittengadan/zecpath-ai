# Day 61 - AI Monitoring and Observability Plan

## Objective

Make Zecpath AI easier to monitor, debug, and review by correlating pipeline events, measuring runtime and model quality, alerting on actionable failures, and preserving a separate decision audit trail.

## Current state

- `utils/logger.py` writes plain-text application logs to `logs/app.log`.
- `compliance/audit_logger.py` writes score and decision events to local JSONL files. The events include candidate identifiers and decision details, but the logger does not enforce access control, encryption, retention, or tamper-evident storage.
- `compliance/access_control.py` and `compliance/retention_manager.py` provide policy components, but the audit logger does not use them. The access policy grants audit read/write permissions with default deny; enforcement at an audit storage boundary is still needed.
- `config/retention_policy.json` sets the audit record policy to 730 days with action `retain`. Confirm the intended expiry behavior before implementing automated deletion.
- No HTTP API route, monitoring backend, alert delivery service, or dashboard UI was found. Current benchmark timings are local service-level measurements, not production API latency.
- The audit log records whether human review is required, but there is no structured completed-review label source for measuring AI-versus-human accuracy.

## Target architecture

```text
API request or command-line run
            |
            v
  Correlation ID + pipeline stage events
            |
      +-----+-------------------+
      |                         |
      v                         v
Operational JSON logs     Protected decision audit store
      |                    score / decision / human review
      v                         |
Metrics aggregation             v
      |                    Restricted audit review
      +-----------+-------------+
                  v
         Dashboard and alerts
```

Operational logs and metrics should contain aggregate, privacy-minimized diagnostics. Individual scores, decision reasons, and human overrides belong in the separately protected audit store. Dashboards should link to audit records only through an authorized service.

## Monitoring scope

### Runtime and pipeline health

Measure accepted, completed, retried, and terminally failed runs; end-to-end and per-stage p50/p95 latency; model startup separately from warm request latency; output validation failures; and audit-write failures. Preserve `request_id` or `run_id` across all events. Keep identifiers such as candidate ID out of metric labels and general logs.

### AI quality

Compare scores only with matched, adjudicated human reviews for the same role, stage, and model version. Report score difference, decision agreement, advance precision/recall, false-rejection rate, matched-review count, and coverage. If human labels or sample counts are missing, display “not measurable” rather than implying the AI is accurate.

### Interview outcomes

Show HR and technical interview completion separately from advancement. Define completion as completed interviews divided by scheduled interviews. Define advancement as human-approved advances divided by completed interviews with a final human review decision. Show missing, pending, no-show, cancelled, and withdrawn states separately when the workflow captures them.

## Alerting approach

Use rolling windows, minimum event counts, deduplication, and named response owners. The proposed pilot triggers are in [day61_alerting_rules.md](day61_alerting_rules.md); they must be calibrated on deployed traffic before paging. A failed required audit write is critical and must prevent the associated decision from being treated as successfully finalized. Alerts must never change a candidate's outcome automatically.

## Decision audit requirements

Use versioned, append-only events for scores, generated decisions, completed human reviews, overrides, audit access, and retention actions. Preserve the original AI event when a human corrects or overrides it. Each event should identify the model and scoring-policy versions, role/stage, trusted actor or service, timestamp, correlation ID, output summary, and references to protected inputs. Avoid raw resumes, transcript excerpts, free-text notes, and unnecessary identity data in the event payload.

The detailed access, schema, integrity, and retention design is in [day61_decision_audit_plan.md](day61_decision_audit_plan.md). The existing local audit files must not be treated as protected production records until the planned authorization and storage boundary is implemented.

## Dashboard layout

1. **Candidate pipeline health:** run volume, completion/failure rate, p50/p95 latency, stage funnel, top error codes, model readiness, and active alerts.
2. **Interview outcomes:** HR and technical interview schedule/completion/advancement counts with explicit denominators and period filters.
3. **AI quality:** human-review coverage and matched AI-human metrics by role, stage, and model version; show sample size and evaluation period.
4. **Alert and audit links:** alert owner/runbook and controlled access to audit events for authorized reviewers.

Keep general dashboard views aggregate-only. Put protected-group fairness analysis in a separate governed review view.

## Implementation phases

1. **Confirm governance:** approve audit readers/writers, trusted identity source, human-review labels, and the meaning of the existing audit retention policy.
2. **Standardize operational logs:** implement the JSONL envelope in [day61_logging_structure.md](day61_logging_structure.md), create a run/request correlation ID, and redact sensitive fields.
3. **Instrument the current pipeline:** record stage start/end, duration, status, model/version, stable error code, retry count, output validation, and audit-write status. Begin with local pipeline runs; add HTTP fields only when an API exists.
4. **Protect decision audits:** add an audit storage service that enforces `AUDIT_WRITE` and `AUDIT_READ`, restricts file/service access, encrypts storage, supports append-only writes, and verifies integrity.
5. **Capture human review outcomes:** store completed reviewer labels and overrides as new, access-controlled events with a documented adjudication method.
6. **Connect metrics, alerts, and dashboard:** aggregate bounded dimensions, implement the proposed rules, and display sample counts and missing-data states.
7. **Validate before production:** check event correlation, metric denominators, alert routing, audit read/write denial, retention/legal-hold behavior, integrity verification, redaction, and dashboard role access using synthetic or de-identified records.

## Day 61 supporting specifications

- [Logging structure](day61_logging_structure.md)
- [Monitoring metrics](day61_metrics_definition.md)
- [Alerting rules](day61_alerting_rules.md)
- [Dashboard design](day61_dashboard_design.md)
- [Decision audit log plan](day61_decision_audit_plan.md)

