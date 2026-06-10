# Data QC Rules

Use these defaults unless the project defines stricter thresholds.

## Bad Windows

- Long pose gap: mark gap time plus 0.5 s before and after.
- Command spike: mark event time plus 1.0 s before and after.
- Outlier suppressed: mark event time plus 0.5 s before and after, or label if the dataset intentionally includes protected behavior.
- FSM/mode transition: mark 2.0 s before and after.
- Pause/resume: exclude pause and mark 1.0 s after resume.
- Emergency stop: exclude the event and surrounding recovery window.
- Manual intervention: label at minimum; exclude from normal success trajectories.

## Quality Grades

- A: No severe gaps/spikes/outliers, task success, complete fields, no manual intervention, stable robot feedback when available.
- B: Minor isolated issue that can be clipped or labeled; remaining trajectory is clean.
- C: Abnormal but uncertain root cause; requires video/log review.
- D: Severe data quality issue; useful only for debugging or failure analysis.
- F: Dangerous, semantically wrong, wrong coordinate frame, wrong robot command direction, or unsafe to reproduce.

## Review Triggers

Require human review when:

- A protected event occurs during a task-critical stage.
- Robot active balance changes task semantics.
- External support equipment visibly affects motion.
- The log lacks robot feedback but the claim depends on execution quality.
- The trajectory is intended for high-dynamic or contact-rich training.
