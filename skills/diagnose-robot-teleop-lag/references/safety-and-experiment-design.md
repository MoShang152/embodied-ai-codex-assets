# Safety and experiment design

## Required live-control gates

Before starting integrated control, verify:

- correct physical robot and network target;
- safe regular startup mode;
- read-only connectivity and mode query;
- input data shape and update readiness;
- conversion/policy output shape and finite values;
- single intended service and publisher instance;
- clear workspace and accessible emergency controls;
- explicit user confirmation for any mode switch or real command publication;
- automatic or manual return-to-safe-mode procedure.

Do not use a permissive debug flag merely to bypass a failed preflight.

## Two-stage experiment

### Stage A: input-only

Keep the robot disconnected from control. Exercise the real sensor/service/conversion stack. Suggested phases:

1. warm-up;
2. stillness;
3. slow single-axis motion;
4. faster repeated motion;
5. torso or multi-axis motion;
6. combined motion;
7. recovery stillness.

### Stage B: integrated robot

Use only low-risk motions appropriate to the robot. Enter teleoperation only after readiness. Stop publication before returning to regular mode.

When the operator cannot see the host, use count-based actions. Example:

1. enter teleoperation;
2. count ten seconds still;
3. ten slow bilateral movements;
4. ten alternating movements per side;
5. ten torso cycles;
6. ten combined movements;
7. ten moderately faster movements;
8. count ten seconds still;
9. exit teleoperation.

Reserve one unused button as a lag marker. Keep pause reserved for safety and exclude pause windows from continuous analysis.

## Stop conditions

Stop immediately if:

- mode switch verification fails;
- input becomes invalid or stale;
- commands publish in the wrong mode;
- robot balance degrades;
- repeated backlog correlates with visible delay;
- service or SDK reports device loss;
- duplicate active publishers/services appear;
- emergency controls are unavailable.

After stopping, verify the robot mode, publisher processes, service state, and artifact closure.

## Evidence integrity

- Use monotonic time for local event ordering.
- Store source-domain timestamps separately.
- Record configuration and code version or file hashes.
- Record queue drops in the recorder itself.
- Avoid synchronous logging in real-time threads.
- Preserve raw JSONL and generate reports from it.
- Mark invalid runs, reconnect runs, and safety interruptions instead of merging them into the baseline.
