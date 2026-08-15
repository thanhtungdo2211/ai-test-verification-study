# Acceptance oracle — version 1.0

Status: frozen on 2026-08-15.  This file is part of the final evidence package
only after all candidate-generation transcripts and independent tests have
been frozen.  Candidate operators must not receive it during Phase 1.

## Contract

`calculate_transfer_fee(amount_vnd: int, is_vip: bool = False) -> int`

1. `amount_vnd` must have the exact type `int` (therefore `bool` is invalid) and
   must be greater than zero.  Wrong types raise `TypeError`; non-positive
   integers raise `ValueError`.
2. `is_vip` must have the exact type `bool`; all other values raise `TypeError`.
3. Compute `amount_vnd * 0.01` using exact decimal arithmetic.
4. Clamp that raw fee to the inclusive interval `[5_000, 50_000]`.
5. If `is_vip` is true, multiply the clamped fee by `0.8`.
6. Round once, at the end, to the nearest 1,000 VND using
   `ROUND_HALF_UP`, and return an `int`.

The reference implementation in `tests_independent/oracle.py` is executable
documentation of these rules.  Independent tests must assert expected values
from this oracle rather than copying candidate implementation helpers.

## Acceptance table

| amount_vnd | is_vip | expected |
|---:|:---:|---:|
| 1 | false | 5,000 |
| 1 | true | 4,000 |
| 500,000 | false | 5,000 |
| 500,000 | true | 4,000 |
| 4,850,000 | false | 49,000 |
| 4,850,000 | true | 39,000 |
| 5,000,000 | false | 50,000 |
| 5,000,000 | true | 40,000 |
| 9,000,000 | false | 50,000 |
| 9,000,000 | true | 40,000 |

The invalid-input set includes `0`, `-1`, `1.5`, `"1000"`, `True`, and `None`
for `amount_vnd`, plus `is_vip=0`, `is_vip=1`, and `is_vip=None`.

| Input condition | Required exception |
|---|---|
| `amount_vnd` is not exactly `int` (including `bool`) | `TypeError` |
| `amount_vnd <= 0` | `ValueError` |
| `is_vip` is not exactly `bool` | `TypeError` |

## Review record

| Reviewer | Date (UTC) | Decision |
|---|---|---|
| M1 (TBD) | 2026-08-15 | Pending named-member signature |
| M3 (TBD) | 2026-08-15 | Pending named-member signature |

After both signatures are supplied, compute and record the SHA-256 of this file
in the decision log.  Any later change is a protocol deviation, never a silent
edit.
