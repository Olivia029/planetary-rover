# Statement of the practice (summary written by the student)

Source of the requirements R1-R7 and of the common rules of the themes. It is
the student's own English summary of the course statement; the examples of the
office theme are left out. Claude Code reads it, never changes it.

## Common rules of the themes

All themes follow the same rules; only the map changes. The state number joins
the cell and the destination, as the FrozenLake state joined row and column.

| Element | Rule |
|---|---|
| Map | `data/map.txt`, one row per line: `.` free, `#` obstacle, `~` hazard and one capital letter per named place |
| Actions | 0 up, 1 right, 2 down, 3 left; against the edge or an obstacle the robot stays in its cell |
| Rewards | -1 per step, so that the shortest route is the best; +20 on reaching the destination; -50 on entering the hazard, so that it avoids it |
| End | `terminated` on reaching the destination or the hazard; `truncated` if cut at 100 steps |
| Start | `reset` picks a destination and a free cell at random, so that training goes through all of them; `run_policy` gives a specific origin and destination |
| State | destination x (rows x columns) + row x columns + column, with the destinations numbered in alphabetical order |
| Interface | an own Gymnasium environment: a subclass of `gymnasium.Env` with `reset` and `step` |

**Why the destination is part of the state.** In the same cell, the best action
depends on where the robot is going. So the Q table has one row for every cell
and every destination, and 4 columns, one per action.

## Seven minimum requirements

Below these minimums the practice cannot pass.

| Requirement | What it demands | How it is checked |
|---|---|---|
| R1 Grid environment | `data/map.txt` and an own Gymnasium environment, a subclass of `gymnasium.Env`, that meets the common rules | `check_env` without errors, a test per rule of `step` and another of the state number |
| R2 Trained Q table | the `QTable` of Session 5, trained with random actions from `env.action_space.sample()` and saved with `np.save` in `q_table.npy`; the agent loads it with `np.load` without training again | of all the (origin cell, destination) pairs, 95 % or more reach the destination by the shortest route, given by the breadth-first search of Session 1 |
| R3 Experiment | two or more configurations: alpha, gamma or number of episodes | a plot with the % of shortest routes after each block of 100 episodes, one curve per configuration, and its reading |
| R4 Tools | `list_places()` and `run_policy(...)`, each with its description | a test for each error of `run_policy` |
| R5 LLM agent | translates the request, calls the tools and answers with their figures; asks if the place does not exist; out of its domain it does not call `run_policy` | four cases in which the answer and the tools called are checked; two real traces |
| R6 Tests | six or more, with an LLM double: a fake model that gives fixed answers, like `ScriptedModel` of Topic 2 | `uv run pytest` passes without network or token |
| R7 Own specification | `CLAUDE.md` under 200 lines, `.claude/settings.json` with `ask` and `deny`, one command per milestone and `worklog.md` | they are read at delivery; the log says what was asked and what was rejected |

## An own Gymnasium environment

| Piece | What Gymnasium demands |
|---|---|
| `gymnasium.Env` | the class of the environment inherits from it |
| `observation_space` | `spaces.Discrete(n)`: the states are the integers 0 to n - 1 |
| `action_space` | `spaces.Discrete(4)`; its `sample()` gives a random action |
| `reset(seed, options)` | calls `super().reset(seed=seed)`, draws the destination and the cell with `self.np_random` and returns `(state, info)`; with `options`, it starts where it is told |
| `step(action)` | returns `(state, reward, terminated, truncated, info)` |
| `register` and `make` | `gymnasium.register(id, entry_point, max_episode_steps=100)`; `gymnasium.make(id)` adds the limit and sets `truncated` at step 100 |
| `check_env` | from `gymnasium.utils.env_checker`: checks spaces, types and seeds before training |

With the Gymnasium interface the training loop of the practice works unchanged:
`reset`, `env.action_space.sample()`, `step` and `update`.

## Who writes what

| Who | Files |
|---|---|
| The student | `CLAUDE.md`, `.claude/settings.json`, one command per milestone in `.claude/commands/`, `worklog.md` and `informe.pdf`; copies `data/map.txt` from the sheet of the theme |
| Claude Code, with each command | `pyproject.toml` and `uv.lock`, the code of `src/` (environment, training, tools and agent), the tests of `tests/` and `README.md` |
| The program, when training | `q_table.npy` |
