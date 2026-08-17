# Candidate PR body template

## Candidate run

- Run ID: `run-XX`
- Issue: `Closes #<issue-number>`
- Operator: `<name>`
- Tool: `<tool>`
- Displayed model: `<model>`
- Started (UTC): `<timestamp>`
- Ended (UTC): `<timestamp>`
- Candidate status: `executable` / `non-executable`

## Protocol record

- [ ] New, clean external AI conversation was used.
- [ ] The frozen prompt was sent exactly, without repository/oracle context.
- [ ] Clarification asked: `yes` / `no`
- [ ] Ambiguities detected: `<number or NA>`
- [ ] Standard follow-up used: `yes` / `no`
- [ ] Raw transcript was saved before arranging files.
- [ ] Raw transcript: `experiments/transcripts/run-XX.response.txt`
- [ ] Raw transcript SHA-256: `<sha256>`

## Candidate integrity

- [ ] AI implementation is unchanged.
- [ ] AI-generated expected values/tests are unchanged.
- [ ] `ASSUMPTIONS.md` is preserved or records that the AI did not provide one.
- [ ] Packaging-only fix: `none` / `<path and reason>`
- [ ] No hidden oracle or independent test was used to alter the candidate.

## Files in this PR

```text
candidates/run-XX/
experiments/transcripts/run-XX.response.txt
experiments/metadata.csv
experiments/packaging-fixes.csv       # only if applicable
experiments/packaging-fixes/run-XX-*.patch # only if applicable
```

The maintainer will run evaluation after merge. This PR does not claim test,
coverage or mutation results.

