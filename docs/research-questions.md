# Research questions

These questions are frozen for the Topic 7 experiment.  They are deliberately
phrased as questions rather than hypotheses so that the report can faithfully
describe a null result.

1. When given the intentionally ambiguous transfer-fee requirement, does an AI
   operator ask for clarification or record the ambiguity and its assumptions?
2. Do coverage and mutation scores from tests generated in the same context as
   an implementation track the implementation's performance against an
   independently approved acceptance oracle?
3. Does separating requirement ownership, implementation, independent testing,
   and mutation review improve fault detection compared with the AI-generated
   test suite alone?

## Pre-registered measures

- RQ1: `clarification_asked`, `ambiguities_detected`, and the assumptions in
  each run's `ASSUMPTIONS.md` (from `experiments/metadata.csv`).
- RQ2: line/branch coverage, AI-only mutation score, acceptance score, and
  property failures (from `results/measurements.csv` and raw logs).
- RQ3: the change in killed, surviving, timeout, error, and reviewed-equivalent
  mutants between the AI-only and combined suites.

The experiment does not infer causality from six observations.  It reports
effect sizes and counterexamples with the protocol limitations made explicit.
