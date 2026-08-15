# Reproduction checklist

Run this checklist from a clean checkout before release.  Check an item only
after saving its output or evidence path.

- [ ] `uv sync --locked` succeeds under Python 3.12.
- [ ] `uv run python scripts/check_independent.py` passes the reference and
      rejects discount-order, banker-rounding, and bool-validation fixtures.
- [ ] Every official run has an immutable transcript, candidate tree,
      assumptions file, checksum, and metadata row.
- [ ] `scripts/run_tests.py` has produced AI-only and full/independent logs for
      every executable candidate.
- [ ] Mutation output records tool version, command, runtime, and every mutant
      state; timeout/error are not counted as killed.
- [ ] `uv run python scripts/aggregate_results.py --force` regenerates the
      canonical CSV and figures without manual edits.
- [ ] `uv run topic7 validate-data` passes and every report number traces to a
      raw artifact.
- [ ] A second person reruns the commands from a clean environment and signs
      the release record.
