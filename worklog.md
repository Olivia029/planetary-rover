# Worklog

### Milestone 0 - Project setup (`/setup`)
- **Asked:** ran `/setup` with no extra request: create the uv project with
  Python 3.14, install the dependencies and write `.gitignore`.
- **Written:** `pyproject.toml`, `.python-version`, `uv.lock`, `.gitignore`
  and the `.venv/` folder (git-ignored). Nothing else was created or changed:
  `src/q_table.py`, `data/`, `CLAUDE.md`, `.claude/` and `worklog.md` were
  not touched.
- **Accepted:** the creation of the four files above and the pytest section
  that Claude Code added by hand to `pyproject.toml`.
- **Rejected:** nothing.
- **Check:** `uv run python -c "import numpy, gymnasium, matplotlib, ollama;
  print('imports ok')"` printed `imports ok`, and `grep -x ".DS_Store"
  .gitignore` printed `.DS_Store`. Both pass. Claude Code shortened the
  package lists in its report, although CLAUDE.md asks for the full output;
  the commands themselves ran correctly.
- **Reviewed lines:** `pyproject.toml` line 4 (`requires-python = ">=3.14"`),
  lines 5-10 (the four dependencies), lines 12-15 (`dev` group with pytest),
  lines 17-19 (`pythonpath = ["src"]` and `testpaths = ["tests"]`); and the
  six lines of `.gitignore`.

  ### Milestone 1 - World, movement rules and BFS (`/build-world`)
- **Asked:** ran `/build-world` with no extra request: write `src/world.py`
  with the `World` class, the movement rules and the breadth-first search.
- **Written:** `src/world.py` only. `data/`, `CLAUDE.md` and
  `pyproject.toml` were not touched.
- **Accepted:** the diff that creates `src/world.py`.
- **Rejected:** nothing.
- **Check:** the output of `uv run python src/world.py` is identical to the
  expected output, line by line: 6 rows x 9 columns, places A (0, 8),
  B (0, 0), M (5, 4), 43 free cells, 126 pairs with 0 unreachable, B -> A and
  A -> B 16 steps, B -> M and M -> B 9 steps, and the five `move` examples
  (moved, blocked by the edge, blocked by a steep climb, fall, crater).
- **Reviewed lines:** `src/world.py` lines 72-82 (`move`: rock or outside,
  climb above `MAX_CLIMB`, crater or drop below `-MAX_DROP`, normal move) and
  lines 84-96 (`shortest_steps`: FIFO queue, only `"moved"` moves).

### Milestone 2 - Gymnasium environment (`/build-env`)
- **Asked:** ran `/build-env` with no extra request: write `src/rover_env.py`
  (`RoverEnv`, registered as `RoverGrid-v0`) and `tests/test_env.py`.
- **Written:** `src/rover_env.py` and `tests/test_env.py`. `src/world.py`,
  `data/`, `CLAUDE.md` and `pyproject.toml` were not touched.
- **Accepted:** the diffs that create the two files.
- **Rejected:** nothing.
- **Check:** the output of `uv run python src/rover_env.py` is identical to
  the expected output (spaces `Discrete(162)` and `Discrete(4)`; rock, steep
  climb, fall, crater and destination steps; reset state 109; truncation at
  step 100; `check_env: ok`). `uv run pytest` ends with `12 passed` and no
  warnings.
- **Reviewed lines:** `RoverEnv.reset` (destination and start with
  `self.np_random`, the `ValueError` cases), `RoverEnv.step` (hazard first,
  then destination, then a normal step), `state` (destination index times
  rows x cols plus row x cols plus column) and the `gym.register` call with
  `max_episode_steps=MAX_STEPS`.

  ### Milestone 3 - Random training and saved Q table (`/build-training`)
- **Asked:** ran `/build-training` with no extra request: write
  `src/train.py` with `RoverAgent`, train with random actions and save
  `q_table.npy`.
- **Written:** `src/train.py` and, by running its demo, `q_table.npy` in the
  project root. `src/world.py`, `src/rover_env.py`, `src/q_table.py`,
  `data/` and `CLAUDE.md` were not touched.
- **Accepted:** the diff that creates `src/train.py`.
- **Rejected:** nothing.
- **Check:** the output of `uv run python src/train.py` is identical to the
  expected output (`random training: 1500 episodes`, `shortest routes:
  100.0 %`, `saved q_table.npy: (162, 4)`). The practice requires at least
  95 %. `ls -l q_table.npy` shows 5312 bytes (162 x 4 x 8 bytes of data plus
  a 128-byte header).
- **Reviewed lines:** `RoverAgent.train` (random action, `update` with
  `terminated`, episode ends on `terminated or truncated`) and
  `RoverAgent.shortest_rate` (a pair counts only if the rover ends on the
  destination in exactly `World.shortest_steps` steps, with a limit of
  `MAX_STEPS`).

### Milestone 4 - Learning-curve experiment (`/build-experiment`)
- **Asked:** ran `/build-experiment` with no extra request: write
  `src/experiment.py` and draw the learning curves of three configurations.
- **Written:** `src/experiment.py` and, by running its demo,
  `results/learning_curves.png`. `src/train.py`, `src/world.py`,
  `src/rover_env.py`, `src/q_table.py`, `data/`, `q_table.npy` and
  `CLAUDE.md` were not touched.
- **Accepted:** the diff that creates `src/experiment.py`.
- **Rejected:** nothing.
- **Check:** the output of `uv run python src/experiment.py` is identical to
  the expected output (three configurations, % of shortest routes after each
  block of 100 episodes up to 1000). `results/learning_curves.png` exists and
  shows three curves and the 95 % target line.
- **Reading of the curves:** alpha=0.5 gamma=0.9 passes 95 % at 700 episodes
  (98.4 %) and ends at 97.6 %. alpha=0.1 gamma=0.9 learns much more slowly
  (52.4 % after 1000 episodes): each update corrects little. alpha=0.5
  gamma=0.5 ends at 86.5 %: a strong discount gives little value to the
  distant +20, so it takes longer to spread to far cells.
- **Reviewed lines:** `curve` (train one block, then measure, without
  resetting the table) and the loop over `CONFIGS` in the demo.

### Milestone 5 - Tools (`/build-tools`)
- **Asked:** ran `/build-tools` with no extra request: write `src/tools.py`
  (`list_places`, `run_policy`, `Tool` and the `TOOLS` registry) and
  `tests/test_tools.py`.
- **Written:** `src/tools.py` and `tests/test_tools.py`. `src/world.py`,
  `src/rover_env.py`, `src/train.py`, `src/experiment.py`, `src/q_table.py`,
  `data/`, `q_table.npy` and `CLAUDE.md` were not touched.
- **Accepted:** the diffs that create the two files.
- **Rejected:** nothing.
- **Check:** the output of `uv run python src/tools.py` is identical to the
  expected output (three places as JSON; (0, 0) to M in 9 steps with return
  12.0; B to A and A to B in 16 steps with return 5.0; the four `ValueError`
  messages; the registry with `list_places` and `run_policy`). `uv run
  pytest` ends with `22 passed` and no warnings (12 of the environment and
  10 of the tools).
- **Reviewed lines:** `run_policy` (validation order: unknown destination,
  outside the map, rock, crater; then `env.reset(options=...)`; loop with
  `best_action` and a limit of `MAX_STEPS`), `run_policy_json` and the
  `TOOLS` registry (the model only reads text, so the `dict` becomes JSON).

### Milestone 6 - Agent, Ollama model and entry point (`/build-agent`)
- **Asked:** ran `/build-agent` three times. First run: write `src/model.py`,
  `src/agent.py`, `src/llm.py` and `src/main.py`. Second run, after I changed
  CLAUDE.md and the command: add the model's decision to the context as an
  `assistant` message. Third run, after I changed them again: rewrite
  `src/llm.py` with native Ollama tool calling.
- **Written:** `src/model.py`, `src/agent.py`, `src/llm.py` and `src/main.py`;
  the second and third runs changed only `src/agent.py` and `src/llm.py`.
  Milestones 0-5, `data/` and `q_table.npy` were not touched.
- **Accepted:** the diffs of the four files, and then the diff of
  `src/agent.py` and the diff of `src/llm.py`.
- **Rejected:** nothing. I checked that the second and third runs did not
  touch `model.py`, `main.py` or `tools.py`.
- **Problem 1:** with the first version, `uv run python src/main.py` looped:
  qwen3:4b called `list_places` six times and the answer was `Stopped: step
  budget exhausted.` in cases 1, 2 and 4. Cause: the context had only `user`
  messages, so the model did not see its own earlier call. Fix: add the
  decision as an `assistant` message before each Observation.
- **Problem 2:** after that fix the answers were empty. A debug script showed
  that, in JSON mode, the model copied the first place of the Observation
  instead of a decision with a `kind`. A schema for the JSON was worse, and a
  format reminder worked in case 1 but failed in cases 2 and 4. Fix: native
  Ollama tool calling (`tools=`, `tool_calls` and `tool` messages), which the
  model is trained for.
- **Problem 3:** the answers contained the model's reasoning and `<answer>`
  tags even with `think=False`. Fix: `clean` keeps only the text after the
  last `</think>` and the content of `<answer>`.
- **Check:** `uv run python src/model.py` printed the expected four lines;
  the import check printed `imports ok`; `ollama list` shows `qwen3:4b`. With
  `uv run python src/main.py`: case 1 calls `list_places` and `run_policy`
  and answers 9 steps with the route of the tool; case 2 (cafeteria) calls
  only `list_places` and asks which place is meant; case 3 (capital of
  France) calls no tool and says it is out of scope; case 4 (row 0, column 3)
  gets `ERROR: (0, 3) is a rock` as an observation and explains it, without
  stopping the program.
- **Reviewed lines:** `Agent.act` (a tool error becomes the text
  `ERROR: <message>`), `Agent.run` (assistant message, then Observation, and
  the `max_steps` limit), the rules in `system_prompt`, and in `llm.py`
  `to_messages` (decision to `tool_calls`, Observation to `tool` message),
  `clean` and `OllamaModel.__call__`.

### Milestone 7 - Tests (`/build-tests`)
- **Asked:** ran `/build-tests` with no extra request: write the tests of the
  agent, the Ollama wrapper and the training, and add one test to
  `tests/test_tools.py`.
- **Written:** `tests/test_agent.py` (10 tests), `tests/test_llm.py` (5),
  `tests/test_training.py` (6) and one test appended to
  `tests/test_tools.py` (`test_route_cut_at_100_steps`). Nothing in `src/`,
  `data/` or `q_table.npy` was touched, and the existing tests were not
  changed.
- **Accepted:** the diffs that create the three files and the appended test.
- **Rejected:** nothing.
- **Check:** `uv run pytest -q` ends with `44 passed` and no warnings (12
  environment, 11 tools, 10 agent, 5 Ollama wrapper, 6 training).
  `uv run pytest -v` lists the four agent cases: `test_valid_route`,
  `test_unknown_place`, `test_out_of_scope` and `test_failing_tool`. With the
  Ollama app closed and the wifi off, `uv run pytest -q` still ends with
  `44 passed`: the tests need no network, no token and no model.
- **Reviewed lines:** what each agent test asserts on `answer`, `trace` and
  `model.calls`; the spy in `test_update_receives_terminated` (`done` must be
  true only for rewards +20 and -50); and the fake `ollama.chat` in
  `tests/test_llm.py`.

### Milestone 8 - README and clean-start check (`/finish`)
- **Asked:** ran `/finish` with no extra request: write `README.md` and check
  that the project starts from scratch in a clean copy.
- **Written:** `README.md` only (69 lines, none over 80 characters). Nothing
  else in the project changed.
- **Accepted:** the diff that creates `README.md`, and the commands of the
  clean-start check one by one (`rm -rf /tmp/clean-check`, the `tar` copy
  without `.venv`, caches and `.env`, `uv sync`, `uv run`, `cmp`, `wc -l`,
  `ls -A` and the `grep` for keys). The first attempt of the copy command was
  rejected at the permission prompt and approved on the second one.
- **Rejected:** nothing.
- **Check:** in the clean copy `uv sync` ended without error and `uv run
  pytest` ended with `44 passed`; every command of the README ran and printed
  what the README says, except `src/main.py`, which I ran myself; the
  retrained `q_table.npy` is identical to the delivered one (`cmp` printed
  nothing). `CLAUDE.md` has 199 lines (less than 200), there is no `.env`,
  and the `grep` for tokens found only `.claude/commands/finish.md`, which
  contains the search pattern itself (a false positive; I added
  `--exclude-dir=.claude` to the command). `uv run python src/main.py`
  answered the four requests: case 1 (9 steps, return 12.0, route of the
  tool), case 2 (cafeteria: asks which place, no `run_policy`), case 3
  (capital of France: out of scope, no tool) and case 4 (`ERROR: (0, 3) is a
  rock`, explained).
- **Reviewed lines:** the setup (lines 15-17), tests (19-23) and run (25-38)
  sections of `README.md`, and the map and rules section against
  `CLAUDE.md`.

### These milestones create the frontend:

### Milestone 9 - Viewer with saved results (`/build-viewer`)
- **Asked:** ran `/build-viewer` with no extra request: write `src/viewer.py`
  and `tests/test_viewer.py` and generate `results/viewer.html`. The first
  attempt stopped at step 0 because `data/traces.txt` was empty (I had not
  saved it); after saving the output of `src/main.py` there, I ran it again.
- **Written:** `src/viewer.py`, `tests/test_viewer.py` (two tests) and
  `results/viewer.html`. No file of milestones 0-8 changed.
- **Accepted:** the diffs that create the first two files.
- **Rejected:** nothing.
- **Check:** `uv run python src/viewer.py` printed `routes: 126`, `curves: 3`
  and `traces: 4`; `uv run pytest -q` ends with `46 passed`; `shasum -c`
  reported OK for the 14 files of milestones 0-8 and `data/`; both `grep`
  commands printed nothing. After its own check of the tabs, Claude Code
  widened the height scale to the digits 0-9 and made the step table fit
  beside the grid.
- **Reviewed lines:** `record_route` (same loop as `run_policy`, recording
  each step), `parse_traces`, and the two tests of `tests/test_viewer.py`.
- **By eye:** I opened `results/viewer.html` and checked the five tabs
  (Map, Route, Policy, Learning, Agent).


### Milestone 10 - Live chat with qwen3:4b (`/build-chat`)
- **Asked:** ran `/build-chat` with no extra request: add the live chat to the
  viewer with a local server, fixed to `qwen3:4b` with Ollama.
- **Written:** `src/serve.py`; `src/viewer.py` extended (mode switch, status
  check, chat, `page(data)`); two tests appended to `tests/test_viewer.py`.
  No file of milestones 0-8 changed.
- **Accepted:** the diffs of the three files.
- **Rejected:** nothing.
- **Check:** `uv run pytest -q` ends with `48 passed`; `imports ok`; `shasum -c`
  is OK for every file except `src/viewer.py`, which the milestone extends;
  both `grep` commands printed nothing.
- **Reviewed lines:** the routes of `serve.py` (`chat`, `find_route`, the 502 on
  errors), `status`, and the two tests.
- **By eye:** without the server the badge says `Saved results - no model` and
  `Live chat` is disabled; with `uv run python src/serve.py` the badge says
  `Live - Ollama - qwen3:4b` and the four requests of `main.py` work in the
  chat (the first moves the rover on the Route tab).

### Milestone 11 - Requirements document and README (`/build-docs`)
- **Asked:** ran `/build-docs` two times. First run: write
  `docs/requirements.md` and update `README.md`. It stopped before writing
  anything, because the requirements R1-R7 and the common rules were in no
  file of the project and `README.md` was missing. Second run, after I added
  `docs/statement.md` (my English summary of the statement), protected it in
  `.claude/settings.json` and changed the command so that it reads that file
  and writes the README again if it is missing: it wrote both files.
- **Written:** `docs/requirements.md` (86 lines) and `README.md` (76 lines,
  written again following step 1 of `/finish`, because the milestone-8 file
  was no longer in the project, with `48 passed`, the commands of the viewer
  and the live chat, and the new files in the layout). I also wrote
  `docs/statement.md` myself. No file of `src/`, `tests/`, `data/` or
  `q_table.npy` was touched.
- **Accepted:** the diffs that create `docs/requirements.md` and `README.md`.
- **Rejected:** nothing.
- **Problem:** the citation check failed once: the note "How to read it"
  wrote the format `path::name` itself, and the checker read it as a
  reference. Claude Code reworded the note in words and the check passed.
- **Check:** the citation check printed `citations ok: 82`; `uv run pytest -q`
  ends with `48 passed`; `README.md` has 76 lines and no line over 80
  characters; `CLAUDE.md` has 134 lines (less than 200); `shasum -c` was OK
  for every file of milestones 0-8 and `data/`; the `grep` for absolute paths
  printed nothing. 25 lines of `docs/requirements.md` are over 80 characters,
  all of them table rows, which cannot be wrapped.
- **Decision:** rule 5 of `CLAUDE.md` said that only `llm.py` uses the network.
  Since milestone 10, `serve.py` also talks to Ollama and opens a local port
  on 127.0.0.1, so I changed the rule to name both.
- **Reviewed lines:** the table of R1-R7 in `docs/requirements.md` (every
  "where" and every test name against `uv run pytest --collect-only -q`) and
  the section "Additions to the standard statement" (heights, own map,
  viewer and live chat).
