import pytest

from topic7_experiment.metrics import MutationCounts, percentage


@pytest.mark.parametrize(
    ("numerator", "denominator", "expected"),
    [(8, 10, 80.0), (1, 3, 33.33), (0, 0, None), (0, 5, 0.0)],
)
def test_percentage(numerator: int, denominator: int, expected: float | None) -> None:
    assert percentage(numerator, denominator) == expected


@pytest.mark.parametrize("value", [-1, 1.5, True])
def test_percentage_rejects_invalid_counts(value: object) -> None:
    with pytest.raises((TypeError, ValueError)):
        percentage(value, 2)  # type: ignore[arg-type]


def test_percentage_rejects_numerator_above_denominator() -> None:
    with pytest.raises(ValueError, match="greater"):
        percentage(3, 2)


def test_mutation_counts_calculates_both_scores() -> None:
    counts = MutationCounts(killed=70, survived=20, timeout=5, error=5, equivalent=5)

    assert counts.total_generated == 100
    assert counts.survived_non_equivalent == 15
    assert counts.raw_score == 70.0
    assert counts.adjusted_score == 82.35


def test_mutation_counts_empty_scores_are_unknown() -> None:
    counts = MutationCounts(killed=0, survived=0)

    assert counts.raw_score is None
    assert counts.adjusted_score is None


def test_mutation_counts_rejects_invalid_equivalent_subset() -> None:
    with pytest.raises(ValueError, match="subset"):
        MutationCounts(killed=1, survived=1, equivalent=2)


@pytest.mark.parametrize("field", ["killed", "survived", "timeout", "error", "equivalent"])
def test_mutation_counts_rejects_negative_fields(field: str) -> None:
    values = {"killed": 0, "survived": 0, "timeout": 0, "error": 0, "equivalent": 0}
    values[field] = -1
    with pytest.raises(ValueError, match="non-negative"):
        MutationCounts(**values)
