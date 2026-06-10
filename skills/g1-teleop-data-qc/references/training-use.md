# Training Use Decisions

Use data according to its grade and labels.

## A Grade

Use in the main training set.

## B Grade

Use after clipping bad windows or adding labels. Keep the original raw record for audit.

## C Grade

Hold out for human review. Do not add to the main training set until the root cause and intended use are clear.

## D Grade

Use only for failure analysis, debugging, threshold tuning, or detector development.

## F Grade

Do not train on it. Do not reproduce it unless a controlled safety review approves a narrow diagnostic replay.

## Failure Data

Failure data can be valuable for:

- Failure detection.
- Recovery policy research.
- Reward/model critique.
- Dataset filtering.
- Policy boundary analysis.

It must be explicitly labeled and kept separate from normal successful demonstrations.
