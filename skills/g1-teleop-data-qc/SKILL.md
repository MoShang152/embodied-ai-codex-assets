---
name: g1-teleop-data-qc
description: Inspect and classify G1 or humanoid teleoperation datasets for training readiness. Use when Codex needs to analyze teleoperation logs, motion trajectories, command spikes, outlier suppression, long gaps, invalid frames, FSM transitions, pause/resume windows, safety interventions, clean segments, bad windows, quality grades, or whether data should be trained, clipped, labeled, reviewed, or discarded.
---

# G1 Teleop Data QC

## Goal

Classify teleoperation episodes or segments into quality grades and recommend training use.

## Workflow

1. Load metadata, event logs, trajectory data, robot feedback, video notes, and operator notes if available.
2. Check structural completeness: required fields, timestamps, episode boundaries, mode events.
3. Check timing quality: sample rates, intervals, long gaps, timestamp reversals, missing windows.
4. Check command quality: spike events, outlier suppression, large delta norms, yaw jumps, smoothing artifacts.
5. Check execution quality if robot feedback exists: q/dq/tau, IMU, tracking error, contact/foot state.
6. Mark bad windows around mode switches, pauses, emergency stops, outliers, spikes, manual intervention, and safety recovery.
7. Assign A/B/C/D/F grades per segment.
8. Output clean segments, bad windows, grades, recommended use, and limitations.

## Quality Grades

- A: Clean successful trajectory, suitable for main training set.
- B: Mostly usable, minor issues removable by clipping or labeling.
- C: Ambiguous or abnormal, requires human review before use.
- D: Severe issue, use only for failure analysis or debugging.
- F: Dangerous, semantically wrong, or unsafe to reproduce; forbidden for training.

## References

- Read `references/qc-rules.md` for default bad-window and grading rules.
- Read `references/training-use.md` for recommended dataset-use decisions.

## Scripts

- Use `scripts/classify_events.py` for generic JSONL event logs. It emits bad windows, segment grades, and a Markdown QC report.

## Output Requirements

Always include:

- Overall dataset status.
- Segment grades.
- Bad windows with reasons.
- Training-use recommendation.
- Required human review items.
- Missing evidence that limits confidence.

Never mix abnormal/protected/manual-intervention windows into normal successful training trajectories without explicit labels.
