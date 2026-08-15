"""Fault: applies the VIP discount before the min/max clamp."""

from decimal import ROUND_HALF_UP, Decimal


def calculate_transfer_fee(amount_vnd: int, is_vip: bool = False) -> int:
    if not isinstance(amount_vnd, int) or amount_vnd <= 0:
        raise ValueError("invalid amount")
    raw_fee = Decimal(amount_vnd) * Decimal("0.01")
    if is_vip:
        raw_fee *= Decimal("0.8")
    clamped = min(max(raw_fee, Decimal("5000")), Decimal("50000"))
    return int((clamped / Decimal("1000")).quantize(Decimal("1"), rounding=ROUND_HALF_UP) * 1000)
