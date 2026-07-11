.PHONY: sync lint format format-check test typecheck check pre-commit clean

sync:
	uv sync --all-groups

lint:
	uv run ruff check .

format:
	uv run ruff format .

format-check:
	uv run ruff format --check .

test:
	uv run pytest

typecheck:
	uv run mypy

check: lint format-check test typecheck

pre-commit:
	uv run pre-commit run --all-files

clean:
	rm -rf .pytest_cache .mypy_cache .ruff_cache dist build htmlcov
