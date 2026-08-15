"""Reference transfer-fee oracle owned by the independent verifier.

The implementation uses :class:`~decimal.Decimal` throughout the calculation
so binary floating-point representation cannot decide a boundary or rounding
case.  Candidate implementations are never imported here.
"""

from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal


def reference_transfer_fee(amount_vnd: int, is_vip: bool = False) -> int:
    """Return the approved fee for a contract-valid input."""

    if type(amount_vnd) is not int:
        raise TypeError("amount_vnd must be an int, not bool")
    if amount_vnd <= 0:
        raise ValueError("amount_vnd must be positive")
    if type(is_vip) is not bool:
        raise TypeError("is_vip must be a bool")

    raw_fee = Decimal(amount_vnd) * Decimal("0.01")
    clamped_fee = min(max(raw_fee, Decimal("5000")), Decimal("50000"))
    discounted_fee = clamped_fee * Decimal("0.8") if is_vip else clamped_fee
    rounded_thousands = (discounted_fee / Decimal("1000")).quantize(
        Decimal("1"), rounding=ROUND_HALF_UP
    )
    return int(rounded_thousands * Decimal("1000"))


ACCEPTANCE_EXAMPLES: tuple[tuple[int, bool, int], ...] = (
    (1, False, 5_000),
    (1, True, 4_000),
    (500_000, False, 5_000),
    (500_000, True, 4_000),
    (4_850_000, False, 49_000),
    (4_850_000, True, 39_000),
    (5_000_000, False, 50_000),
    (5_000_000, True, 40_000),
    (9_000_000, False, 50_000),
    (9_000_000, True, 40_000),
)
