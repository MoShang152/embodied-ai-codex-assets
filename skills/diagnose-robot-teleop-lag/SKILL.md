---
name: diagnose-robot-teleop-lag
description: Reproduce, instrument, isolate, and report latency or intermittent lag in robot teleoperation pipelines across different robot models, trackers, policies, middleware, and control modes. Use when teleoperation feels delayed, logs show lag/resync/drop/backlog warnings, input or command rates are unstable, a previously observed lag no longer reproduces, or Codex needs to design a safe input-only and integrated robot experiment with layered timestamps, subjective markers, and evidence-backed root-cause classification.
---

# Diagnose Robot Teleop Lag

## Objective

Isolate lag by measuring each pipeline layer separately, preserving robot safety, and distinguishing backlog warnings from end-to-end motion latency. Do not attribute causality from a terminal warning alone.

## Core workflow

1. Establish the exact current stack.
2. Freeze safety and control boundaries.
3. Map timestamps and queues across layers.
4. Add passive instrumentation without changing runtime behavior.
5. Run an input-only baseline.
6. Run a controlled integrated experiment.
7. Correlate internal events, publish continuity, robot feedback, and operator markers.
8. Classify findings by evidence strength and produce a formal report.

Read [references/architecture.md](references/architecture.md) before designing instrumentation. Read [references/safety-and-experiment-design.md](references/safety-and-experiment-design.md) before any live robot operation. Use [references/config-schema.md](references/config-schema.md) when preparing the generic analyzer.

## 1. Establish the current stack

Inspect the real repository and host state. Do not assume that an old runbook, copied module, or terminal warning describes the code currently executed.

Identify:

- active entrypoint and Python environment;
- input device, service, transport, and receive API;
- raw input rate and source timestamp fields;
- resampling/interpolation stage and target rate;
- policy or retargeting compute stage;
- publisher topic, message type, and frame identifier;
- robot mode/FSM and switch semantics;
- pause/resume behavior;
- available robot feedback topics;
- existing logs, recorders, reports, and historical code snapshots.

Compare preserved historical code with current code before claiming that an algorithm change removed lag.

## 2. Freeze safety boundaries

Before live control, state and enforce:

- required safe startup mode;
- explicit opt-in needed for mode switching or command publication;
- emergency stop, remote controller, pause, and exit actions;
- robot workspace clearance;
- actions forbidden during the test;
- automatic return-to-safe-mode behavior;
- read-only checks that must pass first.

Never broaden an input-only test into robot control. Do not publish while the robot is in a non-teleoperation mode. Stop publication before switching back to the regular mode.

## 3. Define the lag hypothesis

Rewrite vague reports into measurable hypotheses. Separate at least:

- source interruption or burst delivery;
- host reader scheduling or queue overwrite;
- conversion/policy compute overrun;
- synthetic clock backlog and resync;
- publisher jitter or frame loss;
- robot-side execution delay;
- intentional pause/resume or mode-switch boundaries;
- operator-perceived lag without internal warnings;
- internal warnings without perceived lag.

Record the exact warning formula, threshold, time domain, buffer semantics, and print throttling. Treat a backlog detector as a backlog detector unless it compares synchronized end-to-end timestamps.

## 4. Instrument passively

Prefer optional callbacks, counters, or recorders that leave default runtime semantics unchanged. Record monotonic event time plus source-domain timestamps.

Capture, where available:

- raw arrival time and source timestamp;
- device/body/joint timestamps;
- queue depth, dropped samples, duplicate or backward timestamps;
- per-frame conversion and policy compute time;
- target/reference timestamp and lag ticks;
- resync/drop/backlog events;
- output pose interval;
- publish time, frame id, and publish result;
- mode/FSM switches;
- pause/resume events;
- robot feedback timestamps and state;
- operator lag marker button;
- recorder queue drops and process resource samples.

Use asynchronous writing when synchronous disk I/O could perturb the reader or control thread.

## 5. Run the input-only baseline

Do not connect robot control. Keep the actual input device and service path.

Use phases that distinguish startup, stillness, slow motion, faster motion, combined motion, and recovery. Include a warm-up phase. Record the full raw evidence and generate a report immediately.

Determine whether lag events cluster around:

- cold start;
- reconnect or device discovery;
- high-motion phases;
- input gaps followed by bursts;
- compute spikes;
- queue saturation;
- pause/resume.

If source timestamps are missing or constant, use the narrowest valid timestamp such as per-joint timestamps. State the limitation.

## 6. Run the integrated robot experiment

Proceed only after input-only checks and read-only robot preflight pass.

Use a fixed, low-risk protocol. Keep actions count-based when the operator cannot see or hear the host. Reserve a harmless controller button as an operator-perceived-lag marker. Exclude pause/resume windows from continuous-lag analysis unless pause behavior is the target.

Record exact entry and exit mode events so the analyzer can isolate active teleoperation segments. Verify the robot returned to the safe mode after the run.

## 7. Analyze evidence

Copy [references/config.example.json](references/config.example.json) and adapt event and field names. Run:

```bash
python scripts/analyze_teleop_lag.py RUN_DIR --config CONFIG.json
```

The script expects `samples.jsonl` and writes `generic_lag_report.md` unless `--output` is given.

Interpret jointly:

- lag/resync count and phase;
- operator markers;
- input, output, and publish interval statistics;
- processing p95/p99/max versus cycle budget;
- frame-id gap distribution;
- pause/resume and mode-switch boundaries;
- recorder drops;
- robot feedback correlation when available.

An isolated long interval is scheduler jitter unless it coincides with backlog, frame loss, persistent rate reduction, robot-feedback delay, or operator perception.

## 8. Classify conclusions

Use these labels:

- **Confirmed:** direct timestamp/event correlation reproduces the mechanism.
- **Supported:** multiple independent signals agree, but one layer is unobserved.
- **Plausible:** consistent with architecture and later experiments, but historical raw evidence is missing.
- **Excluded for this run:** instrumentation shows the condition did not occur in the measured segment.
- **Unknown:** required evidence is unavailable.

Never rewrite plausible historical causes as confirmed. If a lag disappeared without an algorithm change, compare entrypoints, service lifecycle, device configuration, preflight, process load, and experiment controls.

## 9. Report

Produce a neutral technical report containing:

- environment and topology;
- detector formula and limitations;
- historical evidence boundary;
- instrumentation and code changes;
- input-only and integrated protocols;
- numeric results;
- explanation of warnings versus perceived lag;
- confirmed, plausible, and excluded causes;
- safety outcome and final robot state;
- limitations and next measurements;
- paths to raw artifacts and analyzer configuration.

Do not claim stable absence of lag from one short run. State duration, modes, actions, rates, markers, and evidence gaps.

## Adaptation rules

- Replace FSM identifiers with the target robot's regular and teleoperation modes.
- Replace DDS with ROS, ZMQ, UDP, shared memory, or vendor middleware while preserving publish timestamps and sequence identifiers.
- Treat policy inference as a separate compute layer when a learned policy is present.
- Add robot low-state or joint-state correlation when command-to-motion latency is the question.
- Use external high-frame-rate video or a shared visible trigger when absolute end-to-end latency is required.
- Preserve the project's original safety gates and do not infer authority to enable real control.
