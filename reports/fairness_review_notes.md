# ZECPATH AI — Fairness Review Notes

**Document:** Fairness Review Notes  
**Project:** ZECPATH AI Hiring Platform  
**Review Stage:** Day 43 — Ethics & Compliance Review  
**Version:** 1.0

---

## 1. Purpose

This document records the fairness review performed on the ZECPATH AI
candidate scoring process.

The purpose of the review is to identify potential differences in
candidate scoring and selection outcomes that require further
investigation.

The fairness evaluator is an audit component. It does not modify,
increase, decrease, or otherwise adjust candidate scores.

---

## 2. Scope

The review covers the candidate scoring outputs produced by ZECPATH.

The review considers:

- Candidate score distribution
- Average candidate score
- Score variation
- Group-level average scores
- Group-level selection rates
- Disparate-impact ratio
- Score gaps between audit groups

The fairness review is separate from the production scoring process.

---

## 3. Separation of Scoring and Fairness Analysis

ZECPATH must keep audit-only demographic or group information separate
from production scoring inputs.

The intended architecture is:

Candidate Data
    |
    v
Production Scoring
    |
    v
Candidate Score
    |
    +----------------------+
                           |
                           v
                    Fairness Audit
                           |
                           v
                    Review Metrics

Audit-only group information is supplied only to the fairness analysis
component.

It must not be used as an input feature by the production scoring
engine.

---

## 4. Metrics Reviewed

### 4.1 Candidate Count

The evaluator records the number of candidates included in the review.

### 4.2 Average Score

The evaluator calculates the mean candidate score.

### 4.3 Score Range

The score range is calculated as:

highest score - lowest score

A large score range is recorded as an indicator requiring review.

A large score range alone does not establish discrimination or unfairness.

### 4.4 Group Average Score

When audit-group information is available, the evaluator calculates the
average score for each group.

### 4.5 Selection Rate

The selection rate is calculated using the configured scoring threshold.

Selection rate:

number of selected candidates / number of candidates in the group

### 4.6 Disparate Impact Ratio

The evaluator compares each group's selection rate with the highest
observed group selection rate.

Disparate impact ratio:

group selection rate / highest observed group selection rate

A low ratio is treated as a review indicator.

It is not treated as automatic proof of discrimination.

### 4.7 Score Gap

The evaluator calculates the difference between the highest group
average score and each other group's average score.

A score gap above the configured review threshold is flagged for review.

---

## 5. Review Thresholds

The current evaluator uses the following default review thresholds:

| Metric | Threshold |
|---|---:|
| Selection threshold | 0.50 |
| Disparate impact review threshold | 0.80 |
| Score-gap review threshold | 0.10 |

These values are configurable in the `BiasEvaluator`.

They are used as screening thresholds for further investigation and
should not be interpreted as universal legal standards.

---

## 6. Bias Indicators

The evaluator can identify:

- Large score variation
- All candidates receiving zero scores
- Low group-level selection rate relative to the highest observed group
- Large group-level average-score differences

These indicators require investigation.

They do not independently establish that the scoring model is biased.

---

## 7. Data Integrity

The fairness evaluator does not modify candidate scores.

The review process should preserve the original scoring results so that
fairness analysis remains an audit activity rather than a mechanism for
changing candidate rankings.

---

## 8. Protected / Demographic Information

Demographic information must not be used as a scoring feature.

Where demographic or group information is collected for a legitimate
fairness audit, it must remain separated from the production scoring
pipeline.

The fairness evaluator should receive only the minimum information
required for the audit.

---

## 9. Limitations

The current automated review does not by itself establish whether a
difference in outcomes is caused by discrimination.

A flagged result may require additional investigation of:

- Input data
- Job requirements
- Scoring criteria
- Candidate sample size
- Data quality
- Missing information
- Model behavior
- Human review procedures

Statistical indicators should therefore be interpreted together with
the relevant scoring methodology and dataset.

---

## 10. Review Outcome

The ZECPATH fairness evaluation component provides automated indicators
that can identify score and selection differences requiring human
review.

The component does not automatically label the system as biased and
does not modify candidate scores based on demographic information.

Further review should be performed whenever configured fairness
indicators are triggered.

---

## 11. Implementation References

Primary implementation:

`scoring/bias_evaluator.py`

Fairness-related tests:

`tests/test_bias_evaluator.py`

The fairness evaluator is intended to operate as an audit layer
separate from the production candidate scoring process.

---

## 12. Day 43 Status

Fairness review implementation:

**Completed**

Automated tests:

**10 tests passed**

Fairness review documentation:

**Completed**

Next Day 43 task:

**Remove demographic bias signals from the scoring pipeline.**