# Layered teleoperation latency model

## Pipeline map

Model the system as ordered layers:

```text
operator motion
  -> device tracking
  -> device serialization/send
  -> network transport
  -> host service/SDK
  -> reader and input queue
  -> coordinate conversion/retargeting
  -> policy inference or interpolation
  -> output scheduler/reference clock
  -> middleware publisher
  -> robot controller/FSM
  -> actuator and mechanical response
  -> operator perception
```

Do not combine adjacent layers until measurements show they cannot be separated.

## Minimum timestamps

| Layer | Preferred evidence |
|---|---|
| Device | device/body/joint timestamp and frame sequence |
| Host receive | monotonic arrival timestamp and socket/service state |
| Reader | accepted/duplicate/backward counts and queue depth |
| Conversion | start/end monotonic time per source frame |
| Policy | inference duration, input sequence, output sequence |
| Scheduler | target timestamp, latest timestamp, backlog amount |
| Publisher | monotonic publish time and frame id |
| Robot | command receive time, low state, joint state, mode |
| Operator | explicit marker or synchronized video |

## Detector audit

For every warning such as `lag`, `behind`, `drop`, or `resync`, extract:

1. Formula.
2. Threshold.
3. Timestamp domains.
4. Buffer used.
5. Recovery action.
6. Print throttling.
7. Whether every event is recorded or only displayed.

A detector based on `latest_source - target_reference` measures internal backlog. It does not measure network latency unless source and host clocks are synchronized and arrival time is part of the formula.

## Queue behavior

Classify each queue as:

- latest-only overwrite;
- bounded FIFO;
- sampled deque;
- transport buffer;
- SDK internal queue;
- hold-last-output buffer.

Capture what happens on overflow or pause. A pause may intentionally make the reference clock stale and produce a resync on resume. Analyze such events separately from continuous control.

## Rate relationships

Record source, conversion, output, publish, and robot-feedback rates separately. Common patterns:

- source faster than target: normal resampling, but batch conversion can waste compute;
- source slower than target: repeated/held frames or extrapolation;
- conversion slower than target: backlog grows;
- publisher faster than new output: repeated commands;
- publisher stable but robot slow: investigate controller/actuator layer;
- frame ids continuous with isolated long intervals: scheduler jitter, not message loss.

## Historical comparisons

When a problem no longer reproduces, compare:

- code snapshot and detector algorithm;
- input backend and queue semantics;
- service instance count and lifecycle;
- SDK initialization count;
- device/tracker configuration;
- network interface and route;
- runtime entrypoint;
- visualization and recording load;
- pause/mode-switch behavior;
- warm-up and experiment duration.

Separate runtime changes from observation-only changes. A recorder or report generator cannot remove lag unless its overhead changes the system, which must itself be measured.
