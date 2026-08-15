"""Example-based acceptance tests derived only from the frozen oracle."""

from __future__ import annotations

import pytest

from tests_independent.oracle import ACCEPTANCE_EXAMPLES, reference_transfer_fee


@pytest.mark.independent
@pytest.mark.parametrize("amount_vnd,is_vip,expected", ACCEPTANCE_EXAMPLES)
def test_acceptance_examples(
    calculate_transfer_fee: object,
    amount_vnd: int,
    is_vip: bool,
    expected: int,
) -> None:
    function = calculate_transfer_fee
    assert callable(function)
    assert function(amount_vnd, is_vip) == expected


@pytest.mark.independent
@pytest.mark.parametrize("amount_vnd", [0, -1])
def test_non_positive_amounts_raise_value_error(
    calculate_transfer_fee: object, amount_vnd: int
) -> None:
    with pytest.raises(ValueError):
        calculate_transfer_fee(amount_vnd)  # type: ignore[operator]


@pytest.mark.independent
@pytest.mark.parametrize("amount_vnd", [1.5, "1000", True, None])
def test_invalid_amount_types_raise_type_error(
    calculate_transfer_fee: object, amount_vnd: object
) -> None:
    with pytest.raises(TypeError):
        calculate_transfer_fee(amount_vnd)  # type: ignore[operator]


@pytest.mark.independent
@pytest.mark.parametrize("is_vip", [0, 1, None, "yes"])
def test_invalid_vip_types_raise_type_error(calculate_transfer_fee: object, is_vip: object) -> None:
    with pytest.raises(TypeError):
        calculate_transfer_fee(1_000, is_vip)  # type: ignore[operator]


def test_reference_examples_are_self_consistent() -> None:
    for amount_vnd, is_vip, expected in ACCEPTANCE_EXAMPLES:
        assert reference_transfer_fee(amount_vnd, is_vip) == expected
