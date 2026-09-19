# Day 30 - AI vs Human Judgment Comparison

## Objective

Compare the current AI intent result with a predefined human reference for simulated screening responses.

## Baseline

| Stage | Cases | Matches | Agreement |
|---|---:|---:|---:|
| Before intent optimization | 10 | 2 | 20.00% |
| After intent optimization | 10 | 10 | 100.00% |

## Evaluation

| Case | Category | Human Intent | AI Intent | Human Action | AI Action | Result |
|---|---|---|---|---|---|---|
| D30-001 | Experience | on_topic | on_topic | accept | accept | Match |
| D30-002 | Skills | on_topic | on_topic | accept | accept | Match |
| D30-003 | Salary | on_topic | on_topic | accept | accept | Match |
| D30-004 | Availability | on_topic | on_topic | accept | accept | Match |
| D30-005 | Experience | vague | vague | clarify | clarify | Match |
| D30-006 | Skills | off_topic | off_topic | fallback | fallback | Match |
| D30-007 | Salary | missing | missing | clarify | clarify | Match |
| D30-008 | Experience | on_topic | on_topic | accept | accept | Match |
| D30-009 | Skills | on_topic | on_topic | accept | accept | Match |
| D30-010 | Notice Period | on_topic | on_topic | accept | accept | Match |

## Summary

- Test cases: **10**
- Matches: **10**
- Mismatches: **0**
- Human-AI agreement: **100.00%**
- False rejections in this test set: **0**

## Findings

The initial 20% agreement was caused primarily by category-name mismatch between the test inputs and the intent configuration. Category normalization corrected this behavior.

Confusion handling was also added so a response such as “I don't understand what you mean” is treated as missing/clarification rather than off-topic.

## Limitation

The 100% agreement applies only to this 10-case simulated evaluation set. It should not be interpreted as 100% accuracy for all real-world screening conversations.

## Day 30 relevance

This comparison supports the Day 30 requirement to compare AI screening output with human judgment and identify false rejection behavior before further optimization.
