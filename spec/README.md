# Experiment specifications

This directory contains material that is safe to publish before candidate generation.

- `ambiguous-requirement.md` is the frozen requirement supplied to coding AI.
- The hidden oracle must initially be stored under `private/oracle/`, which is ignored by Git.
- `acceptance-oracle.md` is the reviewed v1.0 evidence copy in this scaffold;
  candidate operators must still run in an external clean context and must not
  receive this file until candidate outputs and independent tests are frozen.

The existing project documents in `docs/` discuss the intended oracle. Therefore official candidate-generation AI must run in a clean external context and receive only the exact prompt file, never repository access.
