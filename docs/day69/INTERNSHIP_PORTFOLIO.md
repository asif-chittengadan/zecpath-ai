# ZECPATH AI - Internship Portfolio

**Project author:** Asif C  
**Portfolio status:** Day 69 submission  
**Project type:** Modular Python prototype for AI-assisted recruitment workflows

## Project summary

ZECPATH AI explores how separate software components can structure parts of a hiring workflow: reading resume and job-description documents, comparing job-related evidence, supporting screening and interview stages, combining scores, and recording decision-support results. The repository emphasizes reusable Python modules, configurable rules, synthetic end-to-end demonstrations, automated tests, and documentation of limitations.

The codebase is a prototype and local demonstration environment. It is not a deployed hiring service or an automated replacement for recruiter judgment.

## Problem and approach

Recruitment work often involves unstructured documents, repeated interviews, and scores that are difficult to compare consistently. The project organizes these tasks into modules with explicit data boundaries and outputs. A recruiter or calling program can use the components independently; the Day 56 and Day 63 scripts show selected synthetic handoffs between stages.

```text
Resume / job-description documents
    -> parsing and structured data
    -> candidate-to-job (ATS) scoring
    -> screening and interview modules
    -> unified score and eligibility checks
    -> explainable recommendation for human review
```

The arrows represent available modules and the documented demo path. They do not mean a live upload service automatically runs the entire workflow.

## Technical work represented in the repository

### Parsing and matching

PDF and DOCX readers and resume/job-description parsers extract or normalize document content. `CandidateMatchingService` compares structured resume data with a structured job description using skills, experience, education, and semantic similarity. A schema adapter helps normalize alternate resume formats; the parser-to-ATS handoff still needs an integration layer.

### Screening and interviews

Screening has a conversation state machine, answer handling, scoring, and report utilities. The HR interview package manages interview state, questions, follow-ups, response signals, and score aggregation. Technical interview components manage question flow and consume rubric-based scores. A machine-test evaluator checks supplied task and rubric inputs; the current demo does not run candidate code.

### Scoring, explanations, and governance

The scoring package combines ATS, screening, HR, technical, and optional machine-test values into a unified score with weighted contributions and explanations. Eligibility and recommendation modules apply configured rules. Fairness, consent, access policy, audit, and retention helpers support review and governance, but are not enforced around every entry point and do not constitute a complete production security system.

## Engineering practices and evidence

- Modular packages separate parsing, scoring, interviews, compliance support, configuration, and data.
- JSON configuration makes many score weights, thresholds, interview rules, and policies inspectable.
- Pytest tests cover scoring behavior, schemas, error handling, edge cases, explainability, and compliance utilities.
- Day 56 and Day 63 scripts use fictional inputs to exercise selected multi-stage flows without presenting them as live hiring operations.
- Day 68 fixed a test-isolation issue so `tests/test_section_builder.py` writes to pytest's temporary directory instead of overwriting a shared resume fixture.

The final Day 68 validation completed **679 tests and 8 subtests**, Python compilation checks for eight source/test folders and 18 root entry points, and a four-profile synthetic pipeline run. The run completed in about **1.02 seconds after model initialization**; every expected stage was present, score bounds were valid, and unified weighted totals matched the reported scores. A separate eight-resume warm-scoring benchmark averaged about **0.128 seconds per resume** in that local run. These are demonstration measurements, not a production service-level objective.

## Project outputs and documentation

- Day 66/67 presentation materials provide a timed synthetic demo flow and role-play Q&A.
- Day 68 validation documents test results, the fixture-isolation fix, output consistency, and performance observations.
- Day 55 and Day 58 documents cover security/governance design and proposed AI roadmap/architecture.
- Day 62 references explain module boundaries, callable interfaces, data flows, and persistence status.
- `data/day63_demo/` stores the fictional dataset as a manifest plus separate candidate, job, and assessment files.

See [the documentation index](../README.md) and [the Day 69 AI roadmap](AI_ROADMAP.md) for the complete handoff.

## Responsible-use limits

- Day 63 uses structured synthetic profiles; its runner does not exercise a production upload endpoint or parser-to-ATS integration.
- HR and technical components use deterministic or rubric-based demo inputs. Results are not validated hiring judgments.
- Machine-test fixture results are not produced by executing candidate code in a secure sandbox.
- Consent, access, audit, and retention utilities are not wired around every processing path. The SQL schema is not an active database integration.
- The static `website/index.html` is not an interactive hiring application and is not the company's official website.
- Before any real employment use, the system would need integration, security/privacy review, representative human-labeled evaluation, fairness analysis, accessible human oversight, and approved operational controls.

The project supports human decision-making demonstrations. It should not be used as the sole basis for hiring, rejection, or ranking decisions.
