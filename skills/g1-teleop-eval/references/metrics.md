# Metrics Reference

Use this reference when selecting metrics for a teleoperation evaluation report.

## Input Layer

- Raw sensor rate.
- Valid body/sample rate.
- Invalid and missing sample counts.
- Timestamp interval mean, p95, max.
- Long gaps and disconnect windows.

## Representation Layer

- Retargeted target rate.
- Processing latency.
- Target interval p95/max.
- Target delta norm.
- Yaw step or orientation jump.
- Reachability or IK/optimization residual if available.

## Communication Layer

- Publish rate.
- Publish interval p95/max.
- Publish gaps.
- Effective new-target ratio.
- Stale command/hold behavior.

## Execution Layer

- Tracking error.
- Joint q/dq/tau ranges.
- IMU orientation/angular velocity.
- Foot/contact state if available.
- Video-confirmed behavior.

## Safety Layer

- Outlier suppression count.
- Command spike count.
- Emergency stop count.
- Pause/resume count.
- FSM/mode transitions.
- Manual intervention and support-frame intervention.

## Task Layer

- Success/failure.
- Failure stage.
- Completion time.
- Repeatability.
- Operator subjective notes.
- Training-data suitability.
