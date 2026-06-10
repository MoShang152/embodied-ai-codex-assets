# Embodied AI Codex Assets

Personal Codex assets for G1/humanoid teleoperation, data quality control, evaluation, and failure-case reuse.

## Contents

```text
skills/
  g1-teleop-eval/       Evaluate teleoperation runs and reports.
  g1-teleop-data-qc/    Classify data quality and training readiness.
  g1-failure-case/      Convert debugging incidents into reusable cases.
agents/
  eval-report-agent.md
  data-qc-agent.md
  failure-case-agent.md
templates/
  evaluation_report.md
  data_qc_report.md
  failure_case.md
install.ps1
```

## Install Skills Locally

From PowerShell:

```powershell
.\install.ps1
```

Overwrite existing installed copies:

```powershell
.\install.ps1 -Force
```

The script copies `skills/*` into:

- `$env:CODEX_HOME\skills` when `CODEX_HOME` is set.
- `$HOME\.codex\skills` otherwise.

## Typical Usage

Ask Codex:

```text
Use g1-teleop-eval to analyze this teleoperation run and produce an evidence-based report.
```

```text
Use g1-teleop-data-qc to inspect this dataset and output bad windows, segment grades, and training-use recommendations.
```

```text
Use g1-failure-case to turn this debugging incident into a reusable failure case.
```

## GitHub Setup

Create a public GitHub repository named `embodied-ai-codex-assets`, then push this local repo:

```powershell
git remote add origin https://github.com/<your-user>/embodied-ai-codex-assets.git
git branch -M main
git push -u origin main
```
