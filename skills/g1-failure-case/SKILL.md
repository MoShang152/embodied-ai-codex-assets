---
name: g1-failure-case
description: Convert robotics, G1 teleoperation, WBC, sensor, retargeting, DDS/ROS, data collection, or sim2real incidents into reusable failure cases. Use when Codex needs to summarize a bug, field failure, debugging session, root cause, fix, prevention rule, checklist item, or automation opportunity from logs, reports, videos, notes, or code changes.
---

# G1 Failure Case

## Goal

Turn a debugging incident into reusable engineering memory.

## Workflow

1. Identify the symptom in observable terms.
2. State the impact on safety, data quality, task success, or delivery.
3. List initial hypotheses and how each was tested.
4. Explain the root cause only when supported by evidence.
5. Describe the fix and validation.
6. Add prevention rules, checklist updates, or automation opportunities.
7. Mark whether the issue can be detected automatically.

## Failure Case Template

Use this structure:

- Title
- Context
- Symptom
- Impact
- Evidence
- Hypotheses
- Root Cause
- Fix
- Validation
- Prevention
- Automation Opportunity
- Related Artifacts

## References

- Read `references/taxonomy.md` for failure categories and recommended wording.
- Read `references/template.md` when producing a reusable case file.

## Output Requirements

Be specific and evidence-based. Avoid vague labels such as "unstable" unless paired with observable metrics, logs, or reproduction steps.

If the root cause is uncertain, say so and list the next evidence needed.
