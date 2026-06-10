# Failure Taxonomy

Use these categories when naming or classifying a failure case.

## Input Failures

- Sensor disconnect.
- Invalid body data.
- Missing tracker.
- Timestamp jump.
- Packet parsing issue.

## Spatial Alignment Failures

- Coordinate frame mismatch.
- Left/right mirror.
- Forward-axis offset.
- Quaternion order mismatch.
- Frame offset missing.

## Timing Failures

- Multi-device desynchronization.
- Long gap.
- Latency spike.
- Stale command.

## Retargeting Failures

- Unreachable target.
- IK jump.
- Joint limit conflict.
- Unstable full-body target.
- Bad target weighting.

## Control/Execution Failures

- Tracking error.
- Torque/velocity saturation.
- Active balance step.
- Oscillation.
- Foot slip.

## Data Failures

- Missing label.
- Incomplete episode.
- Failure mixed with success data.
- Mode transition not clipped.

## Process Failures

- Missing runbook step.
- Wrong network/domain/interface.
- Multiple command sources.
- Logs not recorded.
