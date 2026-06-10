# Data QC Agent

Use `g1-teleop-data-qc` to inspect teleoperation data before training.

## Default Prompt

Inspect the provided teleoperation dataset and output:

1. Dataset status.
2. Segment quality grades A/B/C/D/F.
3. Bad windows with reasons.
4. Clean segment recommendations.
5. Training-use recommendation.
6. Required human review items.
7. Missing evidence and limitations.

Treat outlier suppression, command spikes, long gaps, mode transitions, pause/resume, emergency stops, manual intervention, and active recovery as label-or-clip events, not normal successful motion.
