.PHONY: sync format lint test coverage check validate

sync:
	uv sync --locked

format:
	uv run ruff format .
	uv run ruff check --fix .

lint:
	uv run ruff format --check .
	uv run ruff check .

test:
	uv run pytest

coverage:
	uv run pytest --cov=topic7_experiment --cov-branch --cov-report=term-missing

validate:
	uv run topic7 validate-data

check: lint coverage validate

