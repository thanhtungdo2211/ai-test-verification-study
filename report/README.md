# Report evidence workspace

`evidence-matrix.csv` is the source register for the literature review.  Every
claim in the final report must point to a verified source and every reported
measurement must point to a row in `results/measurements.csv` plus its raw
manifest/log.  Generated tables and charts are reproducible with
`scripts/aggregate_results.py`; do not hand-edit their values.

Use [`report-outline.md`](report-outline.md) for the section-by-section writing
plan, page budget, evidence mapping and wording limits. The outline is a
template: replace placeholders only after the corresponding run and raw
evidence are available.

The snapshot in `pilot/synthetic-evaluation/` may be used to rehearse table and
figure layout. Any draft item based on it must be visibly labelled
`PILOT — SYNTHETIC, NOT RESEARCH DATA` and replaced before submission. Pilot
scores are not evidence for any research question.
