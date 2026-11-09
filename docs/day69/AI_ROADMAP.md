# ZECPATH AI - AI Roadmap

**Day 69 submission | Status: forward-looking plan, not a delivery commitment**

## Vision

Develop ZECPATH AI into a governed decision-support workflow that helps recruiters organize job-relevant evidence while preserving human control over hiring decisions. Keep the company's official website separate from this prototype unless a future integration is explicitly approved.

## Current baseline

The repository contains callable resume and job-description parsers, semantic ATS matching, screening state and scoring components, HR and technical interview modules, machine-test scoring, unified scoring and recommendations, explainability, fairness helpers, and compliance-support utilities. Day 56 and Day 63 scripts demonstrate selected synthetic flows.

Day 68 validation passed 679 tests and 8 subtests. A four-profile Day 63 synthetic run completed in about 1.02 seconds after model initialization. These results validate local demo behavior only. The modules are not joined into a production web service: parser output is not wired automatically into ATS matching, there is no implemented HTTP API, and demo technical and machine-test inputs include supplied rubric values.

## Phase 1 - Connect a controlled end-to-end service

Build a small orchestration layer that validates job and resume schemas, invokes the parser and ATS adapter, records consent before processing, passes typed results between screening and interview stages, and returns an explainable result with source evidence. Add clear error handling and ensure each run can be traced without putting unnecessary candidate details into logs.

**Exit gate:** integration tests cover PDF/DOCX input, malformed files, schema edge cases, consent denial and withdrawal, and repeated requests. The same candidate/job pair must produce a traceable and internally consistent report.

## Phase 2 - Enforce privacy, access, and retention controls

Connect the existing consent and access checks to every service entry point. Add authentication and authorization at the service boundary, protected storage for sensitive records, and an audited retention worker that performs approved deletion rather than only calculating a retention action. Define data minimization, backup, incident-response, and access-review procedures.

**Exit gate:** a security review confirms that unauthenticated users cannot access candidate records; consent and withdrawal are enforced consistently; retention behavior is tested against storage; logs and exports avoid unnecessary personal data.

## Phase 3 - Validate scoring quality and fairness with human review

Create a governed evaluation set with consent and documented labels across relevant job families. Have qualified reviewers independently score the same evidence, measure reviewer agreement, and compare model outputs against that reference. Calibrate thresholds per role only after analyzing errors, missing evidence, and group-level outcomes. Keep fairness analysis as an audit signal; do not feed protected attributes into candidate scoring.

**Exit gate:** acceptance thresholds are written before evaluation, results are reproducible, subgroup limitations are documented, and a human reviewer can see evidence and correct or override the recommendation.

## Phase 4 - Improve interview and technical evaluation safely

Prioritize evidence-grounded interview summaries and structured rubric support. Measure speech transcription quality and candidate experience separately from interview scoring. If coding tasks are run, execute untrusted submissions only in a purpose-built, isolated sandbox with resource limits and no access to production data or secrets. Do not treat fixture-scored tests as verified code execution. Keep emotion inference and sensitive-trait inference out of candidate ranking.

**Exit gate:** stage scores are supported by reviewable evidence; automated outputs are compared with independent human ratings; unsafe code cannot access the host; consent and accommodations are handled before any pilot.

## Phase 5 - Run a limited internal pilot, then decide whether to scale

Start with a small, approved set of roles and users in a separate internal application or service. Define support ownership, monitoring, latency and reliability goals, reviewer correction tracking, candidate notice, escalation, rollback, and a feature-disable path. Do not connect to the official company website until its owners approve the integration and security review.

**Exit gate:** the pilot meets pre-agreed quality, safety, privacy, fairness, and operational criteria. Expand only the features that pass; revise or pause the rest.

## Roadmap principles

- Keep human reviewers accountable for every real employment decision.
- Explain scores with job-related evidence, uncertainty, and known gaps.
- Separate research prototypes and synthetic demo data from live candidate records.
- Re-evaluate when a model, rubric, job family, or data source changes.
- Set measurable targets with stakeholders before a pilot; this roadmap does not invent dates or performance guarantees.

## Relationship to the Day 58 proposal

This roadmap refines the Day 58 AI roadmap and architecture proposal using the Day 62 module reference and Day 68 validation. Day 58 concepts such as interview coaching and transcript summaries remain proposals until implemented and reviewed against the gates above.
