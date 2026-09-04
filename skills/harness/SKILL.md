---
name: harness
description: "Establish or review a lightweight project harness for iterative repository work: classify L0-L3, agree goals and acceptance criteria, then incrementally document rules, evidence, and repeatable checks. Use when starting a new project or when repeated iterations need a clearer delivery loop; skip one-off tiny edits."
---

# Harness skill

Use this skill when the user explicitly starts a new project or asks to make an existing repository easier to work on repeatedly. The skill establishes a small, repository-local work protocol; it does not implement the project itself.

## Operating principles

- Treat harness work as a conversation and an incremental change, not an automatic repository reorganization.
- Inspect the repository's existing rules and documentation before proposing anything.
- Preserve existing structure, especially in shared repositories. Add only the smallest useful harness layer.
- Do not write files until the user confirms the proposed harness level and change scope. Follow any stricter approval protocol in the repository's `AGENTS.md`.
- Separate repository-wide rules from workstream-specific state. Do not copy a complete harness for every project in the same repository.
- Prefer evidence-producing checks over prose claims. For hardware or real-robot repositories, begin with read-only inspection and require explicit confirmation before release, enable, or other risky actions.

## Workflow

### 1. Discover the current project

Inspect, when present:

- repository root, `git status`, and the active branch;
- applicable `AGENTS.md` files;
- `README`, `docs/PROJECT_STATUS.md`, `docs/WORKLOG.md`, runbooks, reports, and references;
- existing tests, validation commands, `scripts/`, and `artifacts/` conventions;
- signs that the repository is shared and that the user has limited permission to change its structure.

Distinguish observed facts from assumptions. Do not move, rename, or rewrite existing files during discovery.

### 2. Identify the workstream and choose a level

Agree with the user on a canonical project/workstream name and one primary tag for the work. Tags are extensible: a new project may add a new tag; an existing project's iterations keep the same tag; retired tags remain historical and are never reused for a different project. If the repository already has a tag registry, use it. Otherwise propose one before creating entries.

Use the lowest level that gives the project a reliable delivery loop:

- **L0 — direct task:** one-shot or very small change, clear verification, no persistent project state needed.
- **L1 — light task harness:** repeated edits or a short delivery cycle; needs a task brief and measurable acceptance criteria.
- **L2 — project harness:** multiple modules, hardware integration, recurring tests, or meaningful regression risk; needs project status, acceptance, evidence/artifact conventions, and possibly repeatable scripts.
- **L3 — exploration harness:** long-running or open-ended exploration with multiple experiments; adds experiment IDs, checkpoints, decision records, and durable result summaries.

Ask only questions that materially affect the harness proposal, such as:

- What outcome must be delivered, and what is explicitly out of scope?
- Is this a new workstream or a continuation of an existing one and tag?
- Which checks are automatic, manual, simulated, or real-hardware only?
- What repository structure may be changed, given collaboration and permissions?
- What evidence is required for completion?

### 3. Propose the harness delta

Before editing, show a concise proposal containing:

- the selected level and why it is sufficient;
- the canonical tag;
- files or directories to add or adjust;
- acceptance and verification changes;
- explicit exclusions, including structure moves or broad cleanup.

Prefer existing locations. Typical mappings are:

```text
AGENTS.md              durable repository-wide rules
docs/PROJECT_STATUS.md current project/repository status
docs/WORKLOG.md        one personal chronological log, separated by project tags
docs/runbooks/         repeatable operating procedures
docs/reference/        stable reference material and matrices
docs/reports/          completed work and evidence-backed conclusions
scripts/               repeatable checks or evidence collection
artifacts/             logs, recordings, screenshots, and test outputs
```

Do not create every item by default. For L0, the correct change may be none. For L1, a task brief and acceptance section may be enough. For L2/L3, add only the missing pieces.

### Communication contract for project `AGENTS.md`

When this skill creates or materially updates a project `AGENTS.md`, include a compact communication contract so future model conversations use the same predictable shape. Keep the headings and order below; adapt only the surrounding project-specific wording:

```md
## Required compact proposal format

For any implementation task, first output a concise proposal only. Do not edit files before explicit approval.

### 1. 问题

State the problem to solve in 1-3 short bullets.

### 2. 范围

List only the files likely to change.

### 3. 改法

List the key concrete changes in 1-4 short bullets.

### 4. 不做

List important exclusions, such as broad refactors, unrelated formatting, dependency changes, or speculative abstractions.

### 5. 验证

List 1-3 narrow commands or checks.
```

The same generated `AGENTS.md` should define the post-approval handoff format:

```md
## Final response after approved implementation

### 修改总结

Summarize what changed.

### 涉及文件

List changed files and the key changed area in each.

### 验证结果

List commands run and their results.

### 注意事项

Mention only material risks, limitations, or follow-up items.
```

Also include these lightweight output rules unless the repository already has an equivalent or stricter version:

```md
## Compact output rules

- Use the user's language by default and keep responses concise and reviewable.
- Prefer concrete paths, symbols, commands, and observed results.
- Separate repository facts, assumptions, and unresolved questions.
- Avoid repeated reasoning, broad background, and low-value status text.
- Report only material risks, limitations, and follow-up items.
```

Use this contract for implementation and change tasks, not for simple explanations or read-only lookups. If an existing `AGENTS.md` already has an equivalent contract, preserve it; if it has a conflicting local contract, discuss the conflict before changing it. Do not overwrite unrelated repository rules merely to impose this format.

### 4. Apply the confirmed scope

After confirmation:

- update or add only the approved files;
- preserve existing content and shared-repository conventions;
- keep the personal worklog in its single agreed location rather than creating per-project worklogs;
- use one primary project tag per continuous task and normalize temporary aliases before completion;
- write acceptance criteria that can be checked, not aspirations;
- make scripts safe and repeatable; default hardware checks to read-only;
- record artifact paths and the distinction between verified facts, observations, hypotheses, and remaining risks.

Do not silently expand from harness setup into unrelated implementation, refactoring, dependency changes, or broad documentation cleanup.

### 5. Verify and hand off

Run the narrowest relevant checks. At minimum, inspect the resulting diff and run `git diff --check`; run a script help/dry-run or focused test when one was added or changed. Confirm that referenced paths exist and that no old path was left behind after an approved move.

After implementation and verification, append a concise entry to the single personal worklog using the canonical project tag. If work was interrupted, record the incomplete state. Report what changed, what was verified, what remains uncertain, and where evidence was saved.

## Completion condition

The skill is complete when the user has agreed to a level and scope, the approved repository-local protocol is written, the relevant acceptance/evidence path is clear, and the changes have passed the narrow verification checks. A harness is not complete merely because more folders or documents were created.
