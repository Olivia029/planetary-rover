---
description: Milestone 0 - create the uv project, dependencies and .gitignore
allowed-tools: Bash(uv init:*), Bash(uv python pin:*), Bash(uv add:*), Bash(uv run:*), Bash(grep:*), Bash(ls:*)
---

Milestone 0 of CLAUDE.md. Do only this milestone.

1. Run `uv init --bare --no-package --python 3.14` in the project root,
   then `uv python pin 3.14`. Check that `.python-version` contains `3.14`.
2. Run `uv add numpy gymnasium matplotlib ollama` and
   `uv add --dev pytest`.
3. Add to `pyproject.toml`:
   `[tool.pytest.ini_options]` with `pythonpath = ["src"]` and
   `testpaths = ["tests"]`. Keep `requires-python = ">=3.14"`.
4. Write `.gitignore` with exactly these lines: `.venv/`, `__pycache__/`,
   `.pytest_cache/`, `.DS_Store`, `.env`, `*.pyc`.
5. Do not create any other file. `src/q_table.py` already exists: do not
   change it.

Acceptance criterion (run both and show the full output):

- `uv run python -c "import numpy, gymnasium, matplotlib, ollama; print('imports ok')"`
  prints `imports ok`.
- `grep -x ".DS_Store" .gitignore` prints `.DS_Store`.

Report: files written or changed, the output of each command, and the lines
of `pyproject.toml` the student must review.
