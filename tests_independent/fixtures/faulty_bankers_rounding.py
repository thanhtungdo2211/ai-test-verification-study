"""Fault: uses Python's ties-to-even rounding instead of half-up."""


def calculate_transfer_fee(amount_vnd: int, is_vip: bool = False) -> int:
    if type(amount_vnd) is not int or amount_vnd <= 0:
        raise ValueError("invalid amount")
    raw_fee = max(5_000, min(amount_vnd // 100, 50_000))
    if is_vip:
        raw_fee *= 0.8
    return int(round(raw_fee / 1_000) * 1_000)
