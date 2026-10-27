# Day 61 - Alerting Rules

## Purpose and status

These are proposed starting rules for a pilot, not production safety limits. The repository does not currently expose an API or run a deployed monitoring service. Calibrate the latency and volume thresholds against real traffic before enabling paging. Every alert must include the environment, stage or route, model version when applicable, time window, event count, and a runbook action.

## Proposed rules

| Alert | Trigger | Severity | Initial response |
| --- | --- | --- | --- |
| Scoring service unavailable | Readiness check fails for 2 consecutive one-minute checks, or the model cannot load. | Critical | Check worker health, model files, dependency status, and startup logs. Stop routing requests to an unready worker. |
| Audit event write failure | A score or decision is produced but its required audit record cannot be written. | Critical | Pause decision processing until audit persistence is healthy; preserve the request/run ID and investigate disk, permissions, or storage failure. |
| Elevated terminal failure rate | More than 5% of accepted runs fail terminally in a rolling 5-minute window with at least 20 runs. More than 10% is critical. | Warning / Critical | Group by stage and error code; check recent code/model/config changes and dependency health. |
| Elevated latency | End-to-end p95 exceeds 1 second for 10 minutes with at least 100 runs. Exceeding 2 seconds for 5 minutes is critical. | Warning / Critical | Inspect stage p95s, queue time, CPU/memory, model loading, and cache behavior. Compare against the same traffic profile. |
| Repeated retries | More than 10% of runs retry in a rolling 15-minute window with at least 20 runs. More than 25% is critical. | Warning / Critical | Identify the stage and error code causing retries; confirm that retries are bounded and not masking terminal failures. |
| Invalid model output | More than 1% of validated model outputs fail schema/range checks in 15 minutes with at least 20 outputs. More than 5% is critical. | Warning / Critical | Check model/config version, input normalization, and output validation. Route affected decisions to human review until resolved. |
| Human-review quality regression | On a rolling 28-day window with at least 50 matched, adjudicated reviews for the same role/stage/model version: mean absolute score difference exceeds 10 percentage points, or advance recall falls below 90%. | Warning | Review the matched cases, reviewer agreement, model version, and score calibration. Do not automatically change candidate outcomes or thresholds. |
| Missing quality evidence | No eligible human-review labels are available for the reporting period, or matched-review coverage falls below the agreed evaluation minimum. | Informational | Mark AI quality as “not measurable”; collect governed review labels before reporting an accuracy conclusion. |

The 1-second and 2-second latency thresholds are intentionally above the Day 60 local load simulation's highest observed p95 of about 788 ms at concurrency 4. That run used a warmed single process and a small sample; it did not include HTTP, a load balancer, or multiple replicas. The thresholds must be revisited when a real API and deployment exist.

The score-difference and recall values are proposed pilot guardrails only. Confirm that the score scale, positive decision class, reviewer adjudication procedure, and minimum sample size are suitable before using them for operational decisions. If a role/stage/model slice has fewer than 50 matched reviews, do not emit a pass/fail quality alert from that slice.

## Alert behavior

- Evaluate rate and latency alerts over rolling windows and suppress percentage alerts below their minimum event counts.
- Deduplicate repeated alerts by environment, route/stage, model version, and error code. Escalate severity only when the critical threshold is met.
- Resolve an alert after the metric remains below its trigger for two consecutive evaluation windows. Keep the alert history for incident review.
- Route critical service and audit failures to the on-call operator. Route quality regressions to the responsible model owner and human-review lead.
- Include a link or identifier for the relevant restricted logs and audit events. Do not include candidate names, contact details, resume text, transcript excerpts, or protected-group labels in alert titles or general notification channels.
- An alert is diagnostic. It must never automatically reject, advance, or otherwise change a candidate's hiring outcome.

## Dependencies before production use

1. Add a real API/readiness boundary and emit the structured events from `day61_logging_structure.md`.
2. Instrument duration, failures, retries, output validation, and audit-write failures at pipeline boundaries.
3. Store completed human-review scores and adjudicated decisions under approved access controls; the current audit logger only records whether human review is required.
4. Establish a baseline from representative traffic and confirm owners, escalation paths, and alert delivery channels.

