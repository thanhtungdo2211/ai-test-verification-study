from decimal import ROUND_HALF_UP, Decimal, InvalidOperation
from numbers import Real

MIN_FEE = Decimal("5000")
MAX_FEE = Decimal("50000")
FEE_RATE = Decimal("0.01")
VIP_DISCOUNT_RATE = Decimal("0.20")
ROUNDING_UNIT = Decimal("1000")


def calculate_transfer_fee(amount_vnd, is_vip=False) -> int:
    """
    Calculate the transfer fee in VND.

    Rules:
    - Fee = 1% of transferred amount.
    - Minimum base fee = 5,000 VND.
    - Maximum base fee = 50,000 VND.
    - VIP customers receive a 20% discount.
    - Final fee is rounded to the nearest 1,000 VND.
    - Invalid transfer amounts are rejected.

    Parameters
    ----------
    amount_vnd : int | float | Decimal
        Transfer amount in VND. Must be finite and greater than 0.
    is_vip : bool
        Whether the customer receives the VIP discount.

    Returns
    -------
    int
        Transfer fee in VND.

    Raises
    ------
    TypeError
        If amount_vnd is not a valid numeric type or is_vip is not bool.
    ValueError
        If amount_vnd is zero, negative, NaN, or infinite.
    """
    if not isinstance(is_vip, bool):
        raise TypeError("is_vip must be a bool")

    # bool is a subclass of int, so reject it explicitly.
    if isinstance(amount_vnd, bool) or not isinstance(amount_vnd, Real | Decimal):
        raise TypeError("amount_vnd must be a numeric value")

    try:
        amount = Decimal(str(amount_vnd))
    except (InvalidOperation, ValueError) as err:
        raise TypeError("amount_vnd must be a numeric value") from err

    if not amount.is_finite():
        raise ValueError("amount_vnd must be finite")

    if amount <= 0:
        raise ValueError("amount_vnd must be greater than 0")

    # 1. Calculate nominal fee.
    fee = amount * FEE_RATE

    # 2. Apply minimum and maximum limits.
    fee = max(MIN_FEE, min(fee, MAX_FEE))

    # 3. Apply VIP discount.
    if is_vip:
        fee *= Decimal("1") - VIP_DISCOUNT_RATE

    # 4. Round to nearest 1,000 VND, with .5 rounding upward.
    rounded_fee = (fee / ROUNDING_UNIT).quantize(
        Decimal("1"), rounding=ROUND_HALF_UP
    ) * ROUNDING_UNIT

    return int(rounded_fee)
