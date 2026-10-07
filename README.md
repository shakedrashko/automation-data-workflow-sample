# Synthetic CSV cleanup and review workflow

This is a self-created technical sample, not a client project. It shows a repeatable way to clean a small CSV export while preserving uncertain records for a human decision.

## What it does

- Trims surrounding whitespace and collapses repeated spaces in names and notes.
- Standardizes known category and status labels without guessing unknown values.
- Preserves every input row and its source record ID.
- Flags possible duplicates and unknown categories in a separate review file.
- Writes a machine-readable summary for a dashboard or downstream automation.

## Run

Python 3.10+ and the standard library are sufficient.

```sh
python workflow.py sample_input.csv output
python -m unittest discover -s tests
```

The command writes `cleaned.csv`, `review_flags.csv`, and `summary.json` under `output/`. The sample input contains only invented organizations and records.

## Delivery pattern

A client project would begin with the real input schema, an agreed mapping table, and acceptance checks. Unknown values remain visible for review rather than being silently changed. The handoff includes the script, sample output, and run instructions.

