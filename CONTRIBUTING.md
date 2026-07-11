# Contributing

## Required Reading

Before changing code or documentation, read `README.md`, `AGENTS.md`, and the relevant files in `docs/`.

## Local Setup

```bash
uv sync --all-groups
uv run ruff check .
uv run pytest
uv run mypy
```

## Engineering Rules

- Do not add trading strategies in Phase 1.
- Do not download stock data in Phase 1.
- Do not connect brokers or real order systems.
- Put configurable parameters under `configs/` and typed settings models.
- Add tests for core logic.
- Never fake test results, market data, or experiment records.
