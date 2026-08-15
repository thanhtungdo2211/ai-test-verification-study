"""Property-based checks that do not copy candidate implementation logic."""

from __future__ import annotations

from collections.abc import Callable

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from tests_independent.oracle import reference_transfer_fee

VALID_AMOUNTS = st.integers(min_value=1, max_value=100_000_000)


@pytest.mark.independent
@given(amount_vnd=VALID_AMOUNTS, is_vip=st.booleans())
@settings(max_examples=100, deadline=None, derandomize=True)
def test_range(
    calculate_transfer_fee: Callable[[int, bool], int], amount_vnd: int, is_vip: bool
) -> None:
    result = calculate_transfer_fee(amount_vnd, is_vip)
    if is_vip:
        assert 4_000 <= result <= 40_000
    else:
        assert 5_000 <= result <= 50_000


@pytest.mark.independent
@given(
    lower=VALID_AMOUNTS,
    increment=st.integers(min_value=0, max_value=100_000_000),
    is_vip=st.booleans(),
)
@settings(max_examples=100, deadline=None, derandomize=True)
def test_monotonicity(
    calculate_transfer_fee: Callable[[int, bool], int],
    lower: int,
    increment: int,
    is_vip: bool,
) -> None:
    assert calculate_transfer_fee(lower, is_vip) <= calculate_transfer_fee(
        lower + increment, is_vip
    )


@pytest.mark.independent
@given(amount_vnd=VALID_AMOUNTS)
@settings(max_examples=100, deadline=None, derandomize=True)
def test_vip_relation(calculate_transfer_fee: Callable[[int, bool], int], amount_vnd: int) -> None:
    regular = calculate_transfer_fee(amount_vnd, False)
    vip = calculate_transfer_fee(amount_vnd, True)
    assert vip <= regular
    assert vip == reference_transfer_fee(amount_vnd, True)


@pytest.mark.independent
@given(amount_vnd=st.integers(min_value=1, max_value=500_000))
@settings(max_examples=100, deadline=None, derandomize=True)
def test_lower_plateau(calculate_transfer_fee: Callable[[int, bool], int], amount_vnd: int) -> None:
    assert calculate_transfer_fee(amount_vnd, False) == 5_000
    assert calculate_transfer_fee(amount_vnd, True) == 4_000


@pytest.mark.independent
@given(amount_vnd=st.integers(min_value=5_000_000, max_value=100_000_000))
@settings(max_examples=100, deadline=None, derandomize=True)
def test_upper_plateau(calculate_transfer_fee: Callable[[int, bool], int], amount_vnd: int) -> None:
    assert calculate_transfer_fee(amount_vnd, False) == 50_000
    assert calculate_transfer_fee(amount_vnd, True) == 40_000


@pytest.mark.independent
@given(
    amount_vnd=st.sampled_from(
        [499_999, 500_000, 500_001, 4_849_999, 4_850_000, 4_850_001, 4_999_999, 5_000_000]
    )
)
@settings(max_examples=50, deadline=None, derandomize=True)
def test_boundary_and_rounding(
    calculate_transfer_fee: Callable[[int, bool], int], amount_vnd: int
) -> None:
    for is_vip in (False, True):
        assert calculate_transfer_fee(amount_vnd, is_vip) == reference_transfer_fee(
            amount_vnd, is_vip
        )


@pytest.mark.independent
@pytest.mark.parametrize("invalid", [False, True, 1.0, "1", None, [], {}])
def test_type_contract(calculate_transfer_fee: Callable[..., int], invalid: object) -> None:
    with pytest.raises(TypeError):
        calculate_transfer_fee(invalid)


@pytest.mark.independent
@pytest.mark.parametrize("invalid_vip", [0, 1, 1.0, "true", None, [], {}])
def test_vip_type_contract(calculate_transfer_fee: Callable[..., int], invalid_vip: object) -> None:
    with pytest.raises(TypeError):
        calculate_transfer_fee(1_000, invalid_vip)


@pytest.mark.independent
@given(amount_vnd=VALID_AMOUNTS, is_vip=st.booleans())
@settings(max_examples=100, deadline=None, derandomize=True)
def test_reference_equivalence(
    calculate_transfer_fee: Callable[[int, bool], int], amount_vnd: int, is_vip: bool
) -> None:
    assert calculate_transfer_fee(amount_vnd, is_vip) == reference_transfer_fee(amount_vnd, is_vip)
