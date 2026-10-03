# ZECPATH AI — AI Ethics Documentation

**Project:** ZECPATH AI Hiring Platform  
**Review Stage:** Day 43 — Ethics & Compliance Review  
**Document Version:** 1.0

---

## 1. Purpose

This document describes the ethical safeguards implemented in the
ZECPATH AI Hiring Platform.

The review focuses on:

- Candidate consent
- Fairness of candidate scoring
- Removal of demographic bias signals
- Explainability of AI-assisted scoring
- Human review and system limitations

---

## 2. AI-Assisted Hiring Workflow

ZECPATH supports multiple stages of the hiring workflow, including:

- Job description processing
- Resume processing
- ATS evaluation
- AI screening
- HR interview evaluation
- Unified candidate scoring

The ethics controls are designed to operate alongside these processing
stages.

---

## 3. Consent

ZECPATH provides a dedicated consent-management component.

Implemented consent categories include:

- Resume processing
- AI screening
- Interview recording
- Transcript processing
- AI evaluation
- Data retention

Each consent event records:

- Candidate identifier
- Consent type
- Whether consent was granted
- Policy version
- Timestamp
- Source
- Optional withdrawal reason

Consent withdrawal creates a new event rather than deleting the
historical consent record.

This preserves an auditable consent history.

Implementation:

`compliance/models.py`

`compliance/consent_manager.py`

Tests:

`tests/test_consent_manager.py`

---

## 4. Fairness Review

ZECPATH includes a fairness evaluation component that reviews scoring
outputs.

The evaluator can examine:

- Candidate score distribution
- Average score
- Score variation
- Group-level average scores
- Selection rates
- Disparate-impact ratio
- Group score gaps

Fairness analysis is an audit function.

It does not automatically modify candidate scores.

A detected statistical difference is treated as an indicator requiring
further investigation and is not automatically interpreted as proof of
discrimination.

Implementation:

`scoring/bias_evaluator.py`

Tests:

`tests/test_bias_evaluator.py`

Documentation:

`reports/fairness_review_notes.md`

---

## 5. Demographic Bias Protection

Protected demographic fields are prevented from entering the production
candidate scoring representation.

The fairness masker protects fields including:

- Age
- Date of birth
- Gender
- Sex
- Race
- Ethnicity
- Religion
- Nationality
- Marital status
- Disability
- Photograph and image fields

The masking operation creates a sanitized copy.

The original candidate record is not modified.

Job-relevant information such as:

- Skills
- Experience
- Education

remains available for scoring.

Implementation:

`scoring/fairness_masker.py`

Integration:

`scoring/candidate_matching_service.py`

Tests:

`tests/test_fairness_masker.py`

`tests/test_candidate_matching_fairness.py`

---

## 6. Separation of Audit and Production Scoring

Demographic or audit-group information must not be used as a production
scoring feature.

The intended architecture is:

Candidate Data
    |
    +----------------------+
    |                      |
    v                      v
Production Scoring     Fairness Audit
    |                      |
    v                      v
Candidate Score       Review Metrics

Fairness audit information is isolated from the production scoring
pipeline.

---

## 7. Explainability

ZECPATH provides structured explanations for unified candidate scores.

The explanation is generated from existing scoring results rather than
recalculating or changing the score.

The explanation can include:

- Candidate
- Role
- ATS score
- AI screening score
- HR interview score
- Normalized scores
- Configured weights
- Weighted contributions
- Unified score
- Job-relevant evidence
- System limitations

Implementation:

`scoring/explainability/explanation_generator.py`

Integration:

`scoring/unified_scoring_engine.py`

Tests:

`tests/test_explanation_generator.py`

`tests/test_unified_scoring_explainability.py`

---

## 8. Explanation Principles

ZECPATH explanations should:

1. Reflect actual scoring inputs.
2. Use job-relevant evidence.
3. Avoid unsupported claims.
4. Avoid demographic information.
5. Avoid exposing internal prompts or private system information.
6. Clearly identify limitations where information is unavailable.
7. Avoid presenting an AI-generated evaluation as an unquestionable
   decision.

---

## 9. Human Review

AI-generated scores and evaluations should be treated as decision
support.

Where human review is part of the hiring process, reviewers should
consider the relevant candidate evidence and the limitations of
automated evaluation.

The system should not claim that an automated score alone establishes
candidate suitability.

---

## 10. Privacy and Data Minimization

Only information required for a specific processing purpose should be
used by each scoring component.

Demographic attributes should not be included in production scoring
features.

Sensitive information should not be unnecessarily copied into
explanations, debugging output, or audit logs.

---

## 11. Known Limitations

The fairness evaluator does not by itself determine the cause of a
statistical difference.

Potential causes may require investigation of:

- Training or evaluation data
- Candidate sample size
- Job requirements
- Scoring criteria
- Missing candidate information
- Model behavior
- Human review procedures

The explainability component describes the available scoring factors.
It does not expose internal model reasoning or guarantee that an
automated evaluation is correct.

---

## 12. Implementation Summary

| Ethics Area | Implementation | Status |
|---|---|---|
| Consent | ConsentManager | Completed |
| Fairness review | BiasEvaluator | Completed |
| Demographic protection | FairnessMasker | Completed |
| Scoring integration | CandidateMatchingService | Completed |
| Explainability | ExplanationGenerator | Completed |
| Unified-score explanation | UnifiedScoringEngine | Completed |

---

## 13. Day 43 Ethics Review Status

The ZECPATH AI system now contains dedicated components for:

- Consent management
- Fairness analysis
- Demographic-signal masking
- Explainable scoring

The remaining Day 43 activity is:

**Compliance alignment and data-retention logic.**

---

## 14. Related Files

### Compliance

`compliance/models.py`

`compliance/consent_manager.py`

### Fairness

`scoring/bias_evaluator.py`

`scoring/fairness_masker.py`

### Explainability

`scoring/explainability/explanation_generator.py`

### Scoring Integration

`scoring/candidate_matching_service.py`

`scoring/unified_scoring_engine.py`

### Tests

`tests/test_consent_manager.py`

`tests/test_bias_evaluator.py`

`tests/test_fairness_masker.py`

`tests/test_candidate_matching_fairness.py`

`tests/test_explanation_generator.py`

`tests/test_unified_scoring_explainability.py`

---

## 15. Review Conclusion

ZECPATH incorporates explicit controls for consent, fairness review,
demographic-signal protection, and explainability.

These controls are intended to support responsible use of AI in the
hiring workflow and to provide auditable information about how
automated scoring is produced.

The controls do not eliminate all potential sources of bias or error.
Ongoing testing, monitoring, appropriate human review, and policy
updates remain necessary.