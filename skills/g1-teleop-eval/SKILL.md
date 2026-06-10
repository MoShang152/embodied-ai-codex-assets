---
name: g1-teleop-eval
description: Evaluate G1 or humanoid teleoperation runs and produce evidence-based reports. Use when Codex needs to analyze teleoperation reproduction, WBC/Pico/VR runs, sensor-input stability, target-generation stability, command publishing, FSM/mode events, robot feedback, safety events, task success, limitations, or next-step recommendations.
---

# G1 Teleop Eval

## Goal

Produce a concise evaluation report for a teleoperation run. Separate what the data proves from what it cannot prove.

## Workflow

1. Identify the system layers: input, representation/retargeting, communication, execution, safety, task result.
2. Load available artifacts: README/runbook, metadata, event logs, generated reports, robot state logs, videos, operator notes.
3. Compute or extract metrics for each layer.
4. Segment by teleop/mode intervals instead of relying only on whole-run averages.
5. Bind every conclusion to evidence.
6. State limitations explicitly.
7. Recommend next actions: continue, collect more data, add logging, tune thresholds, or block unsafe use.

## Layer Checklist

- Input: sensor rate, valid samples, invalid/missing frames, timestamp intervals, dropouts.
- Representation: target rate, processing time, long gaps, target smoothness, reachability.
- Communication: publish rate, publish gaps, effective new-target ratio, stale command behavior.
- Execution: tracking error, q/dq/tau, IMU, foot/contact state, video evidence if available.
- Safety: limits, spike/outlier events, mode switches, pause/resume, emergency stop, manual intervention.
- Task: success, failure stage, repeatability, operator notes, data-training suitability.

## References

- Read `references/metrics.md` when deciding which metrics to report.
- Read `references/report-structure.md` before drafting a final report.

## Scripts

- Use `scripts/summarize_events.py` when the run has JSONL event logs with timestamped events.

## Output Requirements

Always include:

- Verdict with scope.
- Key evidence.
- Layered findings.
- Limitations and what cannot be claimed.
- Recommended next actions.

Do not overstate training-data readiness when robot feedback, video alignment, or task labels are missing.
