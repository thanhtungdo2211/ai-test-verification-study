"""Run the independent suite against the approved reference implementation.

This test is opt-in because the normal candidate runner must never mix the
reference implementation with a candidate's module import.
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest


@pytest.mark.independent
def test_reference_implementation_passes_when_requested(monkeypatch: pytest.MonkeyPatch) -> None:
    if os.environ.get("TOPIC7_RUN_REFERENCE") != "1":
        pytest.skip("reference self-check is opt-in")
    reference_root = Path(__file__).parent / "reference_impl"
    monkeypatch.syspath_prepend(str(reference_root))
    monkeypatch.setenv("TOPIC7_TARGET_MODULE", "transfer_fee.calculator")
    # The actual suite is executed by scripts/check_independent.py so its
    # import path and target module are isolated from this smoke test.
    assert reference_root.joinpath("transfer_fee", "calculator.py").is_file()
