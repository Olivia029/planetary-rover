---
description: Milestone 5 - write src/tools.py (list_places, run_policy, TOOLS) and tests/test_tools.py
allowed-tools: Bash(uv run python src/tools.py), Bash(uv run pytest:*)
---

Milestone 5 of CLAUDE.md. Do only this milestone.

1. Write `src/tools.py` exactly as the contract in docs/contracts.md says:
   - at import: `env = gym.make("RoverGrid-v0")`, the `World` of the
     environment (`env.unwrapped.world`; do not load the map again) and a
     `QTable` whose values are read with
     `table.q = np.load(<project root> / "q_table.npy")`. Never train or
     change the table here;
   - `list_places() -> str`: JSON list with `letter`, `name`, `row` and `col`
     of each place, in letter order. Names: `A` antenna, `B` base, `M` rock
     sample;
   - `run_policy(row, col, destination) -> dict` with `reached` (bool),
     `steps` (int), `return` (float) and `path` (list of `[row, col]`, start
     included). First validate, in this order, and raise `ValueError` with
     these messages: unknown destination
     `unknown destination 'Z' (use A, B, M)`; cell outside the map
     `(6, 0) is outside the map (rows 0-5, columns 0-8)`; rock
     `(0, 3) is a rock`; crater `(1, 5) is a crater`. The limits in the
     message come from the world, not from numbers written in the code. Then
     place the rover with `env.reset(options={"start": ..., "destination":
     ...})`, apply `table.best_action` for at most `MAX_STEPS` steps, sum the
     rewards and stop on `terminated` or `truncated`. A start equal to the
     destination gives 0 steps, `reached` true, return 0.0 and a path with
     only the start. Use the movement rules of the environment; do not
     repeat them;
   - `Tool(function, description)` as a dataclass and
     `TOOLS: dict[str, Tool]` with the keys `list_places` and `run_policy`.
     The function of `run_policy` in the registry must return the `dict` as
     JSON text (`json.dumps`), because every tool returns `str`. The
     descriptions are one sentence each and say what the tool returns and
     when to use it; the one of `run_policy` says that rows and columns go
     from 0, that (0, 0) is the top-left corner, that `destination` is the
     letter of the place, and "Use it for every route and every number".
     The row and column limits in the description come from the world.
2. Write `tests/test_tools.py`, all offline and without Ollama:
   - `list_places` returns the three places in letter order;
   - one successful route (0, 0) to `M`: `reached` true, 9 steps, return
     12.0, path from [0, 0] to [5, 4] with `steps + 1` cells;
   - start on the destination: 0 steps;
   - `run_policy` errors, one parametrized test with four cases (rock,
     crater, outside, unknown destination), each checking the message with
     `pytest.raises(..., match=...)`;
   - every (origin, destination) route reaches the goal in exactly
     `World.shortest_steps` steps;
   - `run_policy` does not change `table.q` (compare a copy);
   - the registry: keys, non-empty descriptions and JSON text from
     `TOOLS["run_policy"].function(...)`.
3. End `src/tools.py` with `if __name__ == "__main__":` and a demo that
   prints exactly the lines below. Run it with
   `uv run python src/tools.py`, then run `uv run pytest`.
4. Do not write any other file and do not change `src/world.py`,
   `src/rover_env.py`, `src/train.py`, `src/experiment.py`,
   `src/q_table.py`, `data/` or `q_table.npy`.

Expected output of the demo (the first line is a single line):

```
[{"letter": "A", "name": "antenna", "row": 0, "col": 8}, {"letter": "B", "name": "base", "row": 0, "col": 0}, {"letter": "M", "name": "rock sample", "row": 5, "col": 4}]
(0, 0) -> M: True 9 12.0
path: 10 cells, from [0, 0] to [5, 4]
(0, 8) -> B: True 16 5.0
(0, 0) -> A: True 16 5.0
(0, 0) -> B: True 0 0.0
ValueError: (0, 3) is a rock
ValueError: (1, 5) is a crater
ValueError: (6, 0) is outside the map (rows 0-5, columns 0-8)
ValueError: unknown destination 'Z' (use A, B, M)
tools: list_places, run_policy
{"reached": true, "steps": 1, "return": 20.0, "path": [[0, 1], [0, 0]]}
```

How the demo is made: line 2 and 3 come from `run_policy(0, 0, "M")`
(`reached`, `steps`, `return`, then the number of cells of the path and its
first and last cell); lines 4-6 print `reached steps return` of the routes
(0, 8) to `B`, (0, 0) to `A` and (0, 0) to `B`; the four `ValueError` lines
come from `run_policy(0, 3, "B")`, `(1, 5, "B")`, `(6, 0, "B")` and
`(0, 1, "Z")`, caught with `except ValueError`; the last line is
`TOOLS["run_policy"].function(0, 1, "B")`.

Acceptance criteria (show the full output of both commands):

- the demo output is identical to the expected output, line by line;
- `uv run pytest` ends with `22 passed` and no warnings (12 of the
  environment and 10 of the tools).

Report: the files written, the full output, and the lines the student must
review (the order of the validations in `run_policy`, the loop that applies
`best_action`, and how the registry turns the `dict` into JSON).
