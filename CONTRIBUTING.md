# Contributing

Thanks for helping improve litecache.

## Setup

1. Fork and clone the repository.
2. Create a virtual environment.
3. Install the project with `python -m pip install -e ".[dev]"`.
4. Create a focused branch for your change.

## Checks

Before opening a pull request, run:

```bash
ruff check .
mypy
pytest
```

Please include tests for behavior changes. Keep the package dependency-free
unless a runtime dependency provides a clear and substantial benefit.

## Pull requests

Explain the motivation and observable behavior of the change. Keep unrelated
refactors separate so reviews remain small and clear.
