# Role assignment

Fill in the names before the official runs.  The role boundaries are part of
the bias-control protocol, not merely project administration.

| Code | Role | Member | Required review |
|---|---|---|---|
| M1 | Research Lead / Requirement Owner | TBD | Signs the oracle with M3; does not revise it after seeing results. |
| M2 | Experiment Engineer / AI Operator | TBD | Runs six clean AI sessions; does not see the hidden oracle beforehand. |
| M3 | Independent Verification Engineer | TBD | Freezes acceptance/property tests before opening candidates. |
| M4 | Mutation & Data Engineer | TBD | Runs mutation and generates tables/figures; does not unilaterally remove equivalents. |

Cross-review: M2 and M4 review reproduction scripts, M1 reviews mutant
classifications, and the whole group reviews the report.  The final editor is
recorded in the release notes.
