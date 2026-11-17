# planetary-rover — Requirements and where the code meets them

Planetary rover on a 6×9 grid with heights. Every row says what the practice asks for, **where in the project it is met** (`file::class.function`), which tests check it and the command that shows it. Figures are from the delivered project: 162 states, 126 (origin, destination) pairs, 48 tests.

## R1 – Grid environment

**Requirement:** `data/map.txt` and an own Gymnasium environment, a subclass of `gymnasium.Env`, that meets the common rules.

**Where the code meets it**

- **Data:** `src/world.py::World.load` reads and validates `data/map.txt` and `data/heights.txt` (same size, known symbols, digits), otherwise `ValueError`. Rows and columns come from the files, never from numbers written in the code.
- **Environment:** `src/rover_env.py::RoverEnv` is a subclass of `gymnasium.Env` with `__init__`, `state`, `reset` and `step`. It uses `World` and is registered as `RoverGrid-v0` with `max_episode_steps=100`.
- **Rewards:** `STEP_REWARD` (-1), `GOAL_REWARD` (+20) and `HAZARD_REWARD` (-50) in `src/rover_env.py`.
- **Movement rules:** defined only in `src/world.py::World.move`, which `RoverEnv.step` calls.
- **Extra (own addition):** `data/heights.txt` gives a height 0-9 per cell; a climb above 1 is blocked and a fall above 2 is a hazard.

**Tests (`tests/test_env.py`, 12 in total)**

- `test_check_env_clean` (1)
- `test_step_rule[rock | steep_climb | fall | crater | destination]` (5)
- `test_truncation_at_100` (1)
- `test_state_number` (1)
- `test_reset_invalid[rock | crater | outside | unknown_destination]` (4)

**Commands**

```
uv run python src/rover_env.py
uv run pytest tests/test_env.py -q
```

**Expected result**

- First command: `spaces: Discrete(162) Discrete(4)`, one line per rule, `truncated at step 100` and `check_env: ok`.
- Second command: `12 passed`.

## R2 – Trained Q table

**Requirement:** the `QTable` of Session 5, trained with random actions from `env.action_space.sample()` and saved with `np.save` in `q_table.npy`; the agent loads it with `np.load` without training again.

**Where the code meets it**

- **The table:** `src/q_table.py::QTable` is the class from Session 5, already in the project and not modified. `QTable.update` applies the Q-learning update and `QTable.best_action` gives the argmax of a state.
- **Training:** `src/train.py::RoverAgent.train` uses `env.action_space.sample()` for every action (random, no epsilon-greedy) and calls `table.update(s, a, r, s2, terminated)` at every step, with `terminated` as the done flag.
- **Saving:** `src/train.py::RoverAgent.save` uses `np.save` and writes `q_table.npy` in the project root (shape `(162, 4)`: 162 states, 4 actions).
- **Evaluation:** `src/train.py::RoverAgent.shortest_rate` gives the percentage of (origin, destination) pairs that reach the destination with `best_action` in exactly the BFS shortest number of steps (`World.shortest_steps`, used only as a reference, never for learning).
- **Loading without training:** `src/tools.py` loads the table once with `np.load("q_table.npy")`. `run_policy` never trains and never changes it.

**Tests**

- `tests/test_training.py::test_saved_table_rate`
- `tests/test_training.py::test_training_from_scratch`
- `tests/test_training.py::test_update_receives_terminated`
- `tests/test_tools.py::test_every_route_is_shortest`
- `tests/test_tools.py::test_run_policy_does_not_change_table`

**Command**

```
uv run python src/train.py
```

**Expected result**

- `shortest routes: 100.0 %` (at least 95 % is required).
- `saved q_table.npy: (162, 4)`.

## R3 – Experiment

**Requirement:** two or more configurations (alpha, gamma or number of episodes); a plot with the % of shortest routes after each block of 100 episodes, one curve per configuration, and its reading.

**Where the code meets it**

- **Configurations:** `src/experiment.py::CONFIGS = [(0.5, 0.9), (0.1, 0.9), (0.5, 0.5)]`, each one an `(alpha, gamma)` pair. Three configurations, so the requirement of two or more is met. Seeds are fixed, so every run gives the same numbers.
- **Curve:** `src/experiment.py::curve` trains one block of 100 episodes with `RoverAgent.train` and then measures `RoverAgent.shortest_rate()`, repeated for each block (10 blocks, up to 1000 episodes).
- **Plot:** one curve per configuration, saved as `results/learning_curves.png`; the values are also printed in the terminal.
- **Reading of the plot:** written in `worklog.md` (milestone 4). It explains how alpha and gamma change the speed of learning and which configuration reaches 95 % first.

**Tests**

- `tests/test_training.py::test_same_seed_same_table` (fixed seeds give the same table).
- The plot itself is checked by eye.

**Command**

```
uv run python src/experiment.py
```

**Expected result**

- Three lines of 10 values (% of shortest routes after each block of 100 episodes).
- `saved results/learning_curves.png`.
- `alpha=0.5 gamma=0.9` is 98.4 % at 700 episodes.

## R4 – Tools

**Requirement:** `list_places()` and `run_policy(...)`, each with its description; a test for each error of `run_policy`.

**Where the code meets it**

- **Both tools** are in `src/tools.py`:
  - `list_places()` returns a JSON list of `{"letter", "name", "row", "col"}` for the places (`A` antenna, `B` base, `M` rock sample), in letter order.
  - `run_policy(row, col, destination)` returns `reached`, `steps`, `return` and `path` (list of `[row, col]`, start included). It first validates the input, then places the rover with `env.reset(options=...)` and applies `best_action` for at most 100 steps. If the start is the destination, it takes 0 steps.
- **Validation:** `run_policy` raises a `ValueError` with a clear message for four errors: unknown destination, cell outside the map, rock and crater.
- **Descriptions and JSON:** `src/tools.py::TOOLS` is the registry, a `dict` of `Tool(function, description)`. Each tool has its own description, which the agent puts in its system prompt and Ollama receives as the tool definition. `run_policy_json` turns the `dict` result into JSON, because tools return `str`.
- **The table** is loaded once with `np.load("q_table.npy")`; it is never trained or modified.

**Tests (`tests/test_tools.py`, 11 in total)**

- `test_run_policy_errors[rock | crater | outside | unknown_destination]` (4, one per error)
- `test_list_places_in_letter_order`
- `test_route_to_rock_sample`
- `test_start_on_destination`
- `test_every_route_is_shortest`
- `test_run_policy_does_not_change_table`
- `test_registry`
- `test_route_cut_at_100_steps`

**Commands**

```
uv run python src/tools.py
uv run pytest tests/test_tools.py -q
```

**Expected result**

- First command: `(0, 0) -> M: True 9 12.0` and the four `ValueError` lines.
- Second command: `11 passed`.

## R5 – LLM agent

**Requirement:** the agent translates the request, calls the tools and answers with their figures; it asks if the place does not exist; out of its domain it does not call `run_policy`. Four cases are checked (answer and tools called) and two real traces are shown.

**Where the code meets it**

- **Agent loop:** `src/agent.py::Agent` with `max_steps=6`:
  - `system_prompt()` sets the rover-assistant role, the grid size and one line per tool description. It also gives the rules: `run_policy` gives every route and number, copied and never computed; for an unknown place, ask which one and do not call `run_policy`; if the request is not about rover routes, say it is out of scope and call no tool; never repeat a call with the same arguments.
  - `act(name, args)` runs a tool. An unknown tool or a tool exception becomes an `"ERROR: ..."` observation for the model and never a crash.
  - `run(request)` loops: it asks the model, runs the tool it chose, adds the result to the context as an observation and stops with the model's answer. Past `max_steps` it returns `"Stopped: step budget exhausted."`, so every loop ends.
- **The real LLM:** `src/llm.py::OllamaModel` (`qwen3:4b`, `think=False`, temperature 0, native Ollama tool calling). It is the only module, with `serve.py`, that talks to Ollama. The model translates the request into a tool call and writes the answer from the tool's numbers; the LLM never computes routes.
- **Test double:** `src/model.py::ScriptedModel` gives fixed decisions, so the agent is tested without Ollama.
- **Four cases:** `src/main.py::REQUESTS`: a valid route, an unknown place, an out-of-scope request and a failing tool. The answer and the tools called are checked for each one.
- **Real traces:** the real output of `src/main.py` is saved in `data/traces.txt`; two of the traces are in `informe.pdf`.

**Tests (`tests/test_agent.py`, 10 in total)**

- The four cases: `test_valid_route`, `test_unknown_place`, `test_out_of_scope`, `test_failing_tool`.
- Plus: `test_unknown_tool`, `test_wrong_arguments`, `test_step_budget`, `test_system_prompt`, `test_context_has_assistant_and_observation`, `test_trace_line`.

**Commands**

```
uv run pytest tests/test_agent.py -q
uv run python src/main.py
```

`src/main.py` needs Ollama running with `qwen3:4b`; the tests do not.

**Expected result**

- First command: `10 passed`, offline.
- Second command: four cases printed with their tool calls and answers. The model's wording varies between runs, but the numbers always come from the tools.

## R6 – Tests

**Requirement:** six or more tests, with an LLM double (a fake model that gives fixed answers, like `ScriptedModel` of Topic 2); `uv run pytest` passes without network or token.

**Where the code meets it**

- **The LLM double:** `src/model.py::Decision` (`kind`, `tool`, `args`, `text`) and `src/model.py::ScriptedModel`, which returns the fixed decisions in order, repeats the last one and keeps `calls`.
- **Agent tests:** `tests/test_agent.py` drives `Agent` with `ScriptedModel`, so no model is needed.
- **Viewer tests:** `tests/test_viewer.py` (4): routes equal `run_policy`, page written, live chat with a scripted model, and a failing model (HTTP 502, the server keeps running).
- **LLM wrapper tests:** `tests/test_llm.py` (5): `test_tool_schemas`, `test_to_messages`, `test_clean`, `test_tool_call`, `test_answer_is_cleaned`. They fake `ollama.chat` with `monkeypatch`, so Ollama is never called.
- **Offline:** nothing in `tests/` uses the network, Ollama or a token; Ollama can be closed.

**Tests by file (48 in total)**

| File | Tests |
|---|---|
| `tests/test_env.py` | 12 |
| `tests/test_tools.py` | 11 |
| `tests/test_agent.py` | 10 |
| `tests/test_llm.py` | 5 |
| `tests/test_training.py` | 6 |
| `tests/test_viewer.py` | 4 |
| **Total** | **48** |

**Commands**

```
uv run pytest -q
uv run pytest --collect-only -q
```

**Expected result**

- `48 passed`, with no network, no Ollama and no token.
- The second command lists the 48 collected tests.

## R7 – Own specification

**Requirement:** `CLAUDE.md` under 200 lines, `.claude/settings.json` with `ask` and `deny`, one command per milestone and `worklog.md`.

**Where the project meets it**

- **`CLAUDE.md`:** 71 lines, only the essentials: description, division of work, a table that points to the other files, environment, the rules the code guarantees and the table of commands. The rest is split into `docs/` and read only when needed (relative paths from the project root):
  - `docs/rules.md`: map, heights, movement, rewards and states.
  - `docs/contracts.md`: contracts of the modules of `src/`.
  - `docs/conventions.md`: structure, tests, style and how to report.
  - `docs/viewer.md`: viewer and live chat.
  - `docs/statement.md`: requirements R1-R7 and common rules.
- **`.claude/settings.json`:**
  - `ask` on `Edit` and `Write`: every edit is shown as a diff to accept or reject.
  - `deny` on `Edit` and `Write` for `CLAUDE.md`, `.claude/**`, `worklog.md`, `data/**` and the five specification files in `docs/`.
  - `deny` on reading `.env` and `.env.*`.
- **`.claude/commands/`:** 12 commands, one per milestone, from `/setup` (0) to `/build-docs` (11), as listed in the table of `CLAUDE.md`.
- **`worklog.md`:** for each milestone, what was asked, what was accepted and what was rejected.

**Tests:** none; it is read at delivery.

**Commands**

```
wc -l CLAUDE.md
cat .claude/settings.json
ls .claude/commands
```
