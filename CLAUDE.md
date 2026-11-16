# planetary-rover

Planetary exploration rover on a grid with heights. A Q table, trained in a
custom Gymnasium environment with random actions, decides how to go from one
cell to a named place. An LLM agent (Ollama) understands a natural-language
request, calls the table as a tool and explains the route with the tool's
numbers. The LLM never computes routes and never invents figures.

## Division of work

- **Claude Code writes the code, the tests and README.md**, one milestone at a
  time and only when the student runs that milestone's command (table at the
  end). It does not run ahead or touch files of another milestone.
- **The student runs the commands and reviews.** Every edit is shown as a
  diff (`ask` in `.claude/settings.json`) to accept or reject. Edits to
  `CLAUDE.md`, `.claude/`, `worklog.md`, `data/` and the four specification
  files in `docs/` are denied, and so is reading `.env`.
- The specification is this file plus `docs/`: contracts are met to the
  letter; nothing it or the command does not ask for is added.
- Files already written for a past milestone are never changed by a later one
  (they stay byte for byte as they are) unless the command says so.

## Where to read more (relative to the project root)

Read the file before the work that needs it; do not load it otherwise.

| File | Read it when |
|---|---|
| `docs/rules.md` | working on the map, heights, movement, rewards or states |
| `docs/contracts.md` | writing or changing any module of `src/` (1 to 6) |
| `docs/viewer.md` | milestones 9 and 10, the viewer and its live chat |
| `docs/statement.md` | milestone 11: the requirements R1-R7 and the common rules |
| `docs/requirements.md` | milestone 11 (written by Claude Code there) |

## Environment

- **Python 3.14**, pinned in `.python-version` and `requires-python`.
- **uv** for everything; never `pip` or `venv`. Flat application project
  (`--app --no-package`): code in `src/` as flat modules, no package.
- **Dependencies**: `numpy`, `gymnasium`, `matplotlib`, `ollama`; `pytest` in
  the `dev` group, with `pythonpath = ["src"]`. No other dependency.
- **Run** from the project root: `uv run python src/<module>.py`; tests with
  `uv run pytest`. Plain imports (`from world import World`).
- **Machine**: macOS on Apple Silicon; `.DS_Store` is git-ignored.
- **LLM**: local Ollama, model `qwen3:4b`, used only by `src/llm.py`.
  Everything else, tests included, works offline with no token.

## Structure

    CLAUDE.md, worklog.md, README.md, pyproject.toml, uv.lock, .python-version
    docs/rules.md, contracts.md, viewer.md, statement.md   specification
                       (student's files)
    docs/requirements.md   requirements and where the code meets them
    data/map.txt, data/heights.txt   terrain and heights (student's files)
    data/traces.txt        real output of src/main.py (student's file)
    src/q_table.py     QTable from class (already in the project)
    src/world.py       World: map, heights, movement rules, BFS reference
    src/rover_env.py   RoverEnv (gymnasium.Env) and its registration
    src/train.py       RoverAgent: random training, evaluation, np.save
    src/experiment.py  configurations and learning curves
    src/tools.py       list_places, run_policy, TOOLS registry
    src/model.py       Decision and ScriptedModel (the LLM double)
    src/llm.py         OllamaModel, the real LLM
    src/agent.py       Agent: system prompt, act, run loop
    src/main.py        entry point: agent demo
    src/viewer.py      data of the viewer and results/viewer.html
    src/serve.py       local server for the live chat (milestone 10)
    tests/             pytest, offline, with ScriptedModel
    q_table.npy        written by src/train.py
    results/           learning_curves.png, viewer.html

`world` imports no project module; `agent` imports `tools`.

## Rules in short (full text in `docs/rules.md`)

- Map 6 x 9 in `data/map.txt`: `.` free, `#` rock, `~` crater, `A` `B` `M`
  places; `data/heights.txt` gives a height 0-9 per cell.
- Actions 0 up, 1 right, 2 down, 3 left. A move is **blocked** by the edge, a
  rock or a climb above 1; a crater or a fall above 2 is a **hazard**.
- Rewards: -1 per step, +20 on the destination, -50 on a hazard.
  `terminated` on destination or hazard; `truncated` at 100 steps.
- State = destination * (rows * cols) + row * cols + col; destinations in
  letter order (`A` 0, `B` 1, `M` 2): 162 states.
- `world.py` is the only place where the movement rules are written.

## Rules the code guarantees

1. The movement rules exist only in `world.py`; the environment, the BFS and
   `run_policy` all use them.
2. `run_policy` never trains and never changes the table.
3. A tool error is an observation for the model, never a crash.
4. Every loop ends: 100 steps per route, `max_steps` per agent run.
5. Only `llm.py` and `serve.py` talk to Ollama (`serve.py` also opens a local
   port on 127.0.0.1); nothing else uses the network; no key or token is in
   the project.
6. Milestones 9 and 10 change no file of milestones 0-8 (10 may extend the
   viewer of 9); milestone 11 changes only `README.md`, as its command says.

## Tests (`tests/`, pytest, offline)

- At least six; agent tests use `ScriptedModel`; none needs Ollama or network.
- Environment: `check_env` clean; one test per rule and one of the state
  number. Tools: one test per `run_policy` error. Agent: four cases.
- A failing test means a defect in the code: never change the test to pass.

## Style

- Everything in English. Modern types, `dataclasses`, `pathlib`; modules
  find `data/` from `Path(__file__).parent.parent / "data"`.
- Executable modules end in `if __name__ == "__main__":` with the demo their
  command describes, printing exactly what it says.
- No extra dependencies, `logging` or arguments. Four-space indent, 80
  characters per line at most. No absolute paths anywhere.

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

## How to report

- Files written and the full output of each command, as printed.
- If the criterion is missed: file, line, cause and proposed diff.
- At the end, the exact lines the student must review.
