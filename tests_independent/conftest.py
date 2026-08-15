"""Target loader for running the same independent suite on each candidate."""

from __future__ import annotations

import importlib
import os
from collections.abc import Callable

import pytest


@pytest.fixture(scope="session")
def calculate_transfer_fee() -> Callable[..., int]:
    """Load a candidate's public function without importing private helpers.

    ``TOPIC7_TARGET_MODULE`` is optional for local oracle development.  The
    candidate runner supplies it (or uses the public default module) when an
    actual candidate is under test.
    """

    module_name = os.environ.get("TOPIC7_TARGET_MODULE", "transfer_fee.calculator")
    try:
        module = importlib.import_module(module_name)
    except ModuleNotFoundError as exc:
        missing_name = exc.name or ""
        if missing_name == module_name or module_name.startswith(f"{missing_name}."):
            pytest.skip(
                f"candidate module {module_name!r} is not available; set PYTHONPATH to a candidate",
                allow_module_level=False,
            )
        raise
    function = getattr(module, "calculate_transfer_fee", None)
    if not callable(function):
        raise TypeError(f"{module_name} does not expose calculate_transfer_fee")
    return function
