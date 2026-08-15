"""Fault: accepts bool as an amount because bool subclasses int."""


def calculate_transfer_fee(amount_vnd: int, is_vip: bool = False) -> int:
    if not isinstance(amount_vnd, int) or amount_vnd <= 0:
        raise ValueError("invalid amount")
    if not isinstance(is_vip, bool):
        raise TypeError("invalid VIP flag")
    return 5_000 if amount_vnd < 500_000 else 50_000
