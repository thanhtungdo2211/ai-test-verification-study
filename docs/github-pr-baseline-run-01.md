# PR: Baseline run-01

## Summary

This PR adds the frozen `run-01` candidate and its baseline/mutation evidence,
plus the runner fixes required to preserve and parse that evidence.

- Closes #`run-01-issue-number`
- Run ID: `run-01`
- Candidate status: executable
- AI implementation and AI-generated expected values: unchanged
- Packaging-only change: `candidates/run-01/src/transfer_fee/__init__.py`
- Raw transcript: `experiments/transcripts/run-01.response.txt`

## Evidence included

```text
candidates/run-01/
experiments/transcripts/run-01.response.txt
experiments/packaging-fixes.csv
experiments/packaging-fixes/run-01-init.patch
results/baseline/run-01/
results/baseline/run-01-attempt-01/
results/mutation-ai-only/run-01/
results/mutation-ai-only/run-01-attempt-01/
results/mutation-independent/run-01/
```

## Protocol checks

- [ ] `experiments/metadata.csv` contains the complete `run-01` row.
- [ ] Tool, displayed model, UTC timestamps and operator are recorded from the
  actual AI session.
- [ ] Raw transcript was saved before arranging candidate files.
- [ ] No repository, hidden oracle or independent tests were sent to the AI.
- [ ] No candidate business logic or expected value was edited.
- [ ] Any packaging-only fix has a separate patch and CSV entry.

## Verification

Commands run:

```text
<paste exact commands and outcomes here>
```

The maintainer should regenerate `results/measurements.csv` from metadata and
raw evidence after this PR is reviewed; this PR does not hand-edit reported
measurements.
