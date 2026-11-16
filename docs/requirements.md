# Requirements and where the code meets them

Written by Claude Code in milestone 11 from `docs/statement.md` (the source of
the common rules, the Gymnasium pieces and R1-R7), the code in `src/`, the
tests in `tests/` and the outputs of the commands.

## How to read it

Every code reference is written as the file path, two colons and the name of
the class, function, constant or test inside it, for example
`src/world.py::World.move`.
There are no line numbers, so the references stay true when lines move. A
test with several cases (`[rock]`, `[crater]`, ...) is cited by its function
name. Run every command from the project root.

## 1. Common rules of the themes

| Rule | How this project meets it | Where |
|---|---|---|
| Map | `data/map.txt`, 6 rows x 9 columns: `.` free, `#` rock (obstacle), `~` crater (hazard), places `A` antenna, `B` base, `M` rock sample; read and validated, sizes taken from the file | `src/world.py::World.load` |
| Actions | 0 up, 1 right, 2 down, 3 left; against the edge or a rock the move is `blocked` and the rover stays in its cell | `src/world.py::MOVES`, `src/world.py::World.move` |
| Rewards | -1 for a moved or blocked step, +20 on entering the destination, -50 on a hazard | `src/rover_env.py::STEP_REWARD`, `src/rover_env.py::GOAL_REWARD`, `src/rover_env.py::HAZARD_REWARD`, `src/rover_env.py::RoverEnv.step` |
| End | `terminated` on the destination or a hazard; `truncated` at step 100, added by `gym.make` from `max_episode_steps` | `src/rover_env.py::RoverEnv.step`, `src/rover_env.py::gym.register`, `src/world.py::MAX_STEPS` |
| Start | `reset` draws a destination and a free start cell (not the destination) with `self.np_random`; with `options` it starts at a given cell and destination, which `run_policy` uses | `src/rover_env.py::RoverEnv.reset`, `src/tools.py::run_policy` |
| State | destination x (rows x columns) + row x columns + column, destinations in letter order (`A` 0, `B` 1, `M` 2): 162 states | `src/rover_env.py::RoverEnv.state` |
| Interface | an own Gymnasium environment, a subclass of `gymnasium.Env` with `reset` and `step`, registered as `RoverGrid-v0` | `src/rover_env.py::RoverEnv`, `src/rover_env.py::ENV_ID` |

## 2. The Gymnasium pieces

| Piece | What Gymnasium asks | Where it is met |
|---|---|---|
| `gymnasium.Env` | the environment class inherits from it | `src/rover_env.py::RoverEnv` |
| `observation_space` | `spaces.Discrete(n)`, states 0 to n - 1 | `Discrete(162)`, built from the number of places, rows and columns in `src/rover_env.py::RoverEnv.observation_space` |
| `action_space` | `spaces.Discrete(4)`; `sample()` gives a random action | `src/rover_env.py::RoverEnv.action_space`; sampled in `src/train.py::RoverAgent.train` |
| `reset(seed, options)` | calls `super().reset(seed=seed)`, draws with `self.np_random`, returns `(state, info)`; with `options` starts where told | `src/rover_env.py::RoverEnv.reset` |
| `step(action)` | returns `(state, reward, terminated, truncated, info)` | `src/rover_env.py::RoverEnv.step` |
| `register` and `make` | `register(id, entry_point, max_episode_steps=100)`; `make(id)` adds the limit | `src/rover_env.py::gym.register`; `gym.make` in `src/train.py::RoverAgent`, `src/tools.py::env` |
| `check_env` | from `gymnasium.utils.env_checker`; checks spaces, types and seeds | `tests/test_env.py::test_check_env_clean` (warnings turned into errors); `uv run python src/rover_env.py` prints `check_env: ok` |

## 3. The seven requirements

| Req. | What it demands | Where the code meets it | Tests | Command | Expected result |
|---|---|---|---|---|---|
| R1 Grid environment | `data/map.txt` and an own `gymnasium.Env` that meets the common rules | `src/world.py::World.move`, `src/rover_env.py::RoverEnv` | `tests/test_env.py::test_check_env_clean`, `tests/test_env.py::test_step_rule` (rock, steep climb, fall, crater, destination), `tests/test_env.py::test_truncation_at_100`, `tests/test_env.py::test_state_number`, `tests/test_env.py::test_reset_invalid` | `uv run python src/rover_env.py` | `spaces: Discrete(162) Discrete(4)`, one tuple per rule, `truncated at step 100`, `check_env: ok` |
| R2 Trained Q table | the `QTable` of class, trained with `env.action_space.sample()`, saved with `np.save` in `q_table.npy`; the agent loads it with `np.load` and never trains | `src/q_table.py::QTable.update`, `src/train.py::RoverAgent.train`, `src/train.py::RoverAgent.save`, `src/train.py::RoverAgent.shortest_rate`, `src/tools.py::np.load` | `tests/test_training.py::test_saved_table_rate`, `tests/test_training.py::test_training_from_scratch`, `tests/test_training.py::test_update_receives_terminated`, `tests/test_tools.py::test_every_route_is_shortest`, `tests/test_tools.py::test_run_policy_does_not_change_table` | `uv run python src/train.py` | `shortest routes: 100.0 %` (at least 95 % required), `saved q_table.npy: (162, 4)` |
| R3 Experiment | two or more configurations; % of shortest routes after each block of 100 episodes, one curve each, and its reading | `src/experiment.py::CONFIGS`, `src/experiment.py::curve`; the reading is in `worklog.md` (milestone 4) | `tests/test_training.py::test_same_seed_same_table` (fixed seeds give the same table); the plot is checked by eye | `uv run python src/experiment.py` | three lines of 10 values, `saved results/learning_curves.png`; `alpha=0.5 gamma=0.9` is 98.4 at 700 episodes |
| R4 Tools | `list_places()` and `run_policy(...)` with descriptions; a test per error of `run_policy` | `src/tools.py::list_places`, `src/tools.py::run_policy`, `src/tools.py::TOOLS` | `tests/test_tools.py::test_run_policy_errors` (rock, crater, outside, unknown destination), `tests/test_tools.py::test_list_places_in_letter_order`, `tests/test_tools.py::test_route_to_rock_sample`, `tests/test_tools.py::test_start_on_destination`, `tests/test_tools.py::test_route_cut_at_100_steps`, `tests/test_tools.py::test_registry` | `uv run python src/tools.py` | `(0, 0) -> M: True 9 12.0` and the four `ValueError` lines |
| R5 LLM agent | calls the tools and answers with their figures; asks if the place does not exist; out of domain no `run_policy`; four cases checked; two real traces | `src/agent.py::Agent.system_prompt`, `src/agent.py::Agent.act`, `src/agent.py::Agent.run`, `src/llm.py::OllamaModel`, `src/main.py::REQUESTS` | `tests/test_agent.py::test_valid_route`, `tests/test_agent.py::test_unknown_place`, `tests/test_agent.py::test_out_of_scope`, `tests/test_agent.py::test_failing_tool` | `uv run python src/main.py` (needs Ollama) | four cases; the real output is saved in `data/traces.txt` (four traces); the model's wording varies |
| R6 Tests | six or more, with an LLM double; `uv run pytest` passes with no network or token | `src/model.py::ScriptedModel`; the fake `ollama.chat` in `tests/test_llm.py::test_tool_call` | all of `tests/`: 48 collected by `uv run pytest --collect-only -q` | `uv run pytest -q` | `48 passed` |
| R7 Own specification | `CLAUDE.md` under 200 lines, `.claude/settings.json` with `ask` and `deny`, one command per milestone, `worklog.md` | `CLAUDE.md`, `.claude/settings.json`, `.claude/commands/` (12 commands, `setup` to `build-docs`), `worklog.md` | none (read at delivery) | `wc -l CLAUDE.md` | under 200 lines |

## Additions to the standard statement

- **Heights.** `data/heights.txt` gives a height 0-9 per cell (the height of a
  rock is ignored). A move is `blocked` if it climbs more than
  `src/world.py::MAX_CLIMB` (1). A drop of more than `src/world.py::MAX_DROP`
  (2) is a fall: a hazard, like a crater (-50, end of the episode). All of it
  is in `src/world.py::World.move`; tests
  `tests/test_env.py::test_step_rule` (cases `steep_climb` and `fall`).
- **Directed reference route.** Because climbing and descending differ, the
  breadth-first search `src/world.py::World.shortest_steps` follows only
  `moved` steps and never enters a crater, so A to B can differ from B to A.
- **The map written by the student.** `data/map.txt` and `data/heights.txt`
  are the student's files (CLAUDE.md); the code takes rows, columns and the
  number of states from them, never as numbers written in the code.
- **Viewer.** `src/viewer.py::build_data` computes every route with the loop
  of `run_policy`, the policy, the curves of `src/experiment.py::curve` and
  the traces of `data/traces.txt` (`src/viewer.py::parse_traces`);
  `src/viewer.py::write_html` writes the self-contained
  `results/viewer.html` (saved results, no model). Tests
  `tests/test_viewer.py::test_routes_match_run_policy` and
  `tests/test_viewer.py::test_write_html`.
- **Live chat.** `src/serve.py::make_server` serves the same page at
  `http://127.0.0.1:8000` and a chat with `qwen3:4b` via Ollama; every reply
  runs a new `src/agent.py::Agent`. `src/serve.py::status` asks the local
  Ollama with `ollama.list()`, as `docs/viewer.md` requires. Tests
  `tests/test_viewer.py::test_live_chat_with_scripted_model` and
  `tests/test_viewer.py::test_live_chat_error_keeps_server`, offline.

## Who writes what

| Who | Files |
|---|---|
| The student | `CLAUDE.md`, `.claude/` (settings and one command per milestone), `worklog.md`, `informe.pdf`, `data/` (map, heights and the traces pasted from `src/main.py`), and `docs/rules.md`, `docs/contracts.md`, `docs/viewer.md`, `docs/statement.md` |
| Claude Code, with each command | `pyproject.toml`, `uv.lock`, `.gitignore`, the code of `src/` (except `src/q_table.py`, the `QTable` from class), the tests of `tests/`, `README.md` and this file |
| The program | `q_table.npy` (`src/train.py`), `results/learning_curves.png` (`src/experiment.py`), `results/viewer.html` (`src/viewer.py`) |
