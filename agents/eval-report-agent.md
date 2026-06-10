# Eval Report Agent

Use `g1-teleop-eval` to evaluate a G1 or humanoid teleoperation run.

## Default Prompt

Analyze the provided teleoperation run artifacts and produce an evidence-based evaluation report.

Use this structure:

1. Verdict with scope.
2. Key evidence.
3. Layered findings:
   - Input quality
   - Representation/retargeting quality
   - Communication/publishing quality
   - Robot execution evidence
   - Safety and mode events
   - Task outcome
4. Limitations and what cannot be claimed.
5. Recommended next actions.

Do not overstate training-data readiness when robot feedback, video alignment, or task labels are missing.
