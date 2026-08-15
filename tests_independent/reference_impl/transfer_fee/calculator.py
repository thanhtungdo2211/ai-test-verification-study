"""Deliberately boring reference implementation for test-suite self-checks."""

from tests_independent.oracle import reference_transfer_fee


def calculate_transfer_fee(amount_vnd: int, is_vip: bool = False) -> int:
    return reference_transfer_fee(amount_vnd, is_vip)
