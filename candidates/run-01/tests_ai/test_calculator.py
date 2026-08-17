from decimal import Decimal

import pytest
from transfer_fee import calculate_transfer_fee

# ---------------------------------------------------------------------------
# Normal customers
# ---------------------------------------------------------------------------


def test_minimum_fee():
    # 100,000 * 1% = 1,000 -> minimum 5,000
    assert calculate_transfer_fee(100_000) == 5_000


def test_exact_minimum_fee():
    # 500,000 * 1% = 5,000
    assert calculate_transfer_fee(500_000) == 5_000


def test_fee_between_min_and_max():
    # 1,000,000 * 1% = 10,000
    assert calculate_transfer_fee(1_000_000) == 10_000


def test_exact_maximum_fee():
    # 5,000,000 * 1% = 50,000
    assert calculate_transfer_fee(5_000_000) == 50_000


def test_maximum_fee():
    # 10,000,000 * 1% = 100,000 -> capped at 50,000
    assert calculate_transfer_fee(10_000_000) == 50_000


# ---------------------------------------------------------------------------
# Rounding
# ---------------------------------------------------------------------------


def test_round_down_to_nearest_1000():
    # 1,040,000 * 1% = 10,400 -> 10,000
    assert calculate_transfer_fee(1_040_000) == 10_000


def test_round_up_to_nearest_1000():
    # 1,060,000 * 1% = 10,600 -> 11,000
    assert calculate_transfer_fee(1_060_000) == 11_000


def test_half_rounds_up():
    # 1,050,000 * 1% = 10,500 -> 11,000
    assert calculate_transfer_fee(1_050_000) == 11_000


# ---------------------------------------------------------------------------
# VIP customers
# ---------------------------------------------------------------------------


def test_vip_regular_fee():
    # Base fee:
    # 1,000,000 * 1% = 10,000
    #
    # VIP:
    # 10,000 * 80% = 8,000
    assert calculate_transfer_fee(1_000_000, is_vip=True) == 8_000


def test_vip_minimum_base_fee():
    # Raw fee = 1,000
    # Minimum base fee = 5,000
    # VIP discount = 4,000
    assert calculate_transfer_fee(100_000, is_vip=True) == 4_000


def test_vip_maximum_base_fee():
    # Raw fee = 100,000
    # Maximum base fee = 50,000
    # VIP discount = 40,000
    assert calculate_transfer_fee(10_000_000, is_vip=True) == 40_000


def test_vip_rounding_down():
    # Base:
    # 1,300,000 * 1% = 13,000
    #
    # VIP:
    # 13,000 * 80% = 10,400 -> 10,000
    assert calculate_transfer_fee(1_300_000, is_vip=True) == 10_000


def test_vip_rounding_up():
    # Base:
    # 1,340,000 * 1% = 13,400
    #
    # VIP:
    # 13,400 * 80% = 10,720 -> 11,000
    assert calculate_transfer_fee(1_340_000, is_vip=True) == 11_000


def test_vip_half_rounds_up():
    # Base:
    # 1,312,500 * 1% = 13,125
    #
    # VIP:
    # 13,125 * 80% = 10,500 -> 11,000
    assert calculate_transfer_fee(1_312_500, is_vip=True) == 11_000


# ---------------------------------------------------------------------------
# Supported numeric types
# ---------------------------------------------------------------------------


def test_float_amount():
    assert calculate_transfer_fee(1_000_000.0) == 10_000


def test_decimal_amount():
    assert calculate_transfer_fee(Decimal("1000000")) == 10_000


# ---------------------------------------------------------------------------
# Invalid amounts
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "amount",
    [
        0,
        -1,
        -100_000,
        Decimal("0"),
        Decimal("-100"),
    ],
)
def test_zero_and_negative_amounts_rejected(amount):
    with pytest.raises(ValueError):
        calculate_transfer_fee(amount)


@pytest.mark.parametrize(
    "amount",
    [
        float("nan"),
        float("inf"),
        float("-inf"),
        Decimal("NaN"),
        Decimal("Infinity"),
        Decimal("-Infinity"),
    ],
)
def test_non_finite_amounts_rejected(amount):
    with pytest.raises(ValueError):
        calculate_transfer_fee(amount)


@pytest.mark.parametrize(
    "amount",
    [
        None,
        "1000000",
        "",
        [],
        {},
        object(),
        True,
        False,
    ],
)
def test_non_numeric_amounts_rejected(amount):
    with pytest.raises(TypeError):
        calculate_transfer_fee(amount)


# ---------------------------------------------------------------------------
# Invalid VIP flag
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "is_vip",
    [
        1,
        0,
        "yes",
        "false",
        None,
        [],
    ],
)
def test_invalid_vip_flag_rejected(is_vip):
    with pytest.raises(TypeError):
        calculate_transfer_fee(1_000_000, is_vip=is_vip)
