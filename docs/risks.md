# Risk register

| ID | Risk | Likelihood/impact | Mitigation and evidence |
|---|---|---|---|
| R-001 | Candidate-generating AI sees the hidden oracle. | High/very high | Run candidates in a clean external context; keep the oracle outside that context and verify the supplied file list. |
| R-002 | A candidate does not import or compile. | Medium/medium | Retain it in the dataset; permit only logged packaging fixes in `experiments/packaging-fixes.csv`. |
| R-003 | Mutation testing is too slow. | Medium/high | Pilot runtime, record the pre-registered subset rule, and run coverage/acceptance for all six runs. |
| R-004 | Equivalent mutants are misclassified. | Medium/high | Preserve raw states and require a written rationale plus a second reviewer. |
| R-005 | Hypothesis finds a flaky failure. | Low/medium | Pin dependencies, use deterministic settings, and retain the minimized example in the test output. |
| R-006 | High coverage is interpreted as correctness. | High/high | Present coverage beside acceptance/property outcomes and counterexamples in every results table. |
| R-007 | A source or claim in the report is fabricated or unverifiable. | Medium/very high | Track every claim in `report/evidence-matrix.csv`; verify the original DOI/URL with two reviewers. |

The register is append-only.  If a mitigation fails, add a dated update instead
of replacing the original assessment.
