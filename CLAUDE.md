# planetary-rover

Planetary exploration rover on a grid with heights. A Q table, trained in a
custom Gymnasium environment with random actions, decides how to go from one
cell to a named place. An LLM agent (Ollama, `qwen3:4b`) understands a
request, calls the table as a tool and explains the route with the tool's
numbers. The LLM never computes routes and never invents figures.

## Division of work

- **Claude Code writes the code, the tests and README.md**, one milestone at a
  time, only when the student runs that milestone's command (table below).
- **The student runs the commands and reviews.** Every edit is shown as a
  diff (`ask` in `.claude/settings.json`). Edits to `CLAUDE.md`, `.claude/`,
  `worklog.md`, `data/` and the `docs/` specification files are denied, and so
  is reading `.env`.
- Contracts are met to the letter; nothing the spec or the command does not
  ask for is added. Files of a past milestone stay byte for byte as they are
  unless the command says so.

## Where to read more (relative to the project root)

Read the file before the work that needs it; do not load it otherwise.

| File | Read it when |
|---|---|
| `docs/rules.md` | map, heights, movement, rewards or states |
| `docs/contracts.md` | writing or changing any module of `src/` (1 to 6) |
| `docs/conventions.md` | writing code or tests: structure, style, report |
| `docs/viewer.md` | milestones 9 and 10 (viewer and live chat) |
| `docs/statement.md` | milestone 11: requirements R1-R7 and common rules |
| `docs/requirements.md` | milestone 11 (written by Claude Code there) |

## Environment

- **Python 3.14** and **uv** for everything; never `pip` or `venv`. Flat
  project (`--app --no-package`): modules in `src/`, plain imports.
- **Dependencies**: `numpy`, `gymnasium`, `matplotlib`, `ollama`; `pytest` in
  `dev` with `pythonpath = ["src"]`. No other dependency.
- **Run** from the project root: `uv run python src/<module>.py`;
  tests with `uv run pytest`.
- **LLM**: local Ollama, `qwen3:4b`. Tests work offline with no token.

## Rules the code guarantees

1. The movement rules exist only in `world.py`; the environment, the BFS and
   `run_policy` all use them.
2. `run_policy` never trains and never changes the table.
3. A tool error is an observation for the model, never a crash.
4. Every loop ends: 100 steps per route, `max_steps` per agent run.
5. Only `llm.py` and `serve.py` talk to Ollama (`serve.py` also opens a local
   port on 127.0.0.1); no key or token is in the project.
6. Milestones 9 and 10 change no file of milestones 0-8; milestone 11 changes
   only `README.md`, as its command says.

## Commands (`.claude/commands/`)

| # | Command | Writes and runs |
|---|---|---|
| 0 | `/setup` | uv project, dependencies, `.gitignore` |
| 1 | `/build-world` | `src/world.py` and its demo |
| 2 | `/build-env` | `src/rover_env.py`, environment tests |
| 3 | `/build-training` | `src/train.py`, `q_table.npy` |
| 4 | `/build-experiment` | `src/experiment.py`, learning curves |
| 5 | `/build-tools` | `src/tools.py`, tool tests |
| 6 | `/build-agent` | `model.py`, `llm.py`, `agent.py`, `main.py` |
| 7 | `/build-tests` | the remaining tests; runs `pytest` |
| 8 | `/finish` | `README.md` and the clean-start check |
| 9 | `/build-viewer` | `src/viewer.py`, its tests, `results/viewer.html` |
| 10 | `/build-chat` | `src/serve.py`, live chat with `qwen3:4b` |
| 11 | `/build-docs` | `docs/requirements.md` and its check |
