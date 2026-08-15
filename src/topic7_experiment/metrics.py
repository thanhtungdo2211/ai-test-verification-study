"""Pure functions for the scores defined in the preregistered study protocol."""

from __future__ import annotations

from dataclasses import dataclass, fields


def _require_count(name: str, value: int) -> None:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{name} must be an integer")
    if value < 0:
        raise ValueError(f"{name} must be non-negative")


def percentage(numerator: int, denominator: int) -> float | None:
    """Return a percentage rounded to two decimals, or None for an empty sample."""

    _require_count("numerator", numerator)
    _require_count("denominator", denominator)
    if numerator > denominator:
        raise ValueError("numerator cannot be greater than denominator")
    if denominator == 0:
        return None
    return round(numerator / denominator * 100, 2)


@dataclass(frozen=True, slots=True)
class MutationCounts:
    """Normalized mutation states used by the report.

    ``equivalent`` is a reviewed subset of ``survived`` and is therefore not
    added to ``total_generated``.
    """

    killed: int
    survived: int
    timeout: int = 0
    error: int = 0
    equivalent: int = 0

    def __post_init__(self) -> None:
        for field in fields(self):
            _require_count(field.name, getattr(self, field.name))
        if self.equivalent > self.survived:
            raise ValueError("equivalent must be a subset of survived")

    @property
    def total_generated(self) -> int:
        return self.killed + self.survived + self.timeout + self.error

    @property
    def survived_non_equivalent(self) -> int:
        return self.survived - self.equivalent

    @property
    def raw_score(self) -> float | None:
        """Killed mutants divided by all generated mutants."""

        return percentage(self.killed, self.total_generated)

    @property
    def adjusted_score(self) -> float | None:
        """Killed divided by killed plus reviewed, non-equivalent survivors."""

        denominator = self.killed + self.survived_non_equivalent
        return percentage(self.killed, denominator)
