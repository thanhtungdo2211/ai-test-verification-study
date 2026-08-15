# Experiment records

The official run record is append-only and uses the same `run-XX` identifier in
metadata, candidates, transcripts, baseline logs, mutation output, and report
tables.

Before each run, the operator records the displayed tool/model and UTC times in
`metadata.csv`.  After the response is saved unchanged, the operator stores
the candidate layout described in `candidates/README.md`, computes checksums,
and records any packaging-only patch in `packaging-fixes.csv`.

The public prompt in `prompts/ambiguous-requirement.txt` is frozen.  Do not add
follow-up text unless the AI asks for clarification, and then use only the
standard response documented in `spec/ambiguous-requirement.md`.
