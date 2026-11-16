---
description: Milestone 2 - write src/rover_env.py and tests/test_env.py
allowed-tools: Bash(uv run python src/rover_env.py), Bash(uv run pytest:*), Bash(ls:*)
---

Milestone 2 of CLAUDE.md. Do only this milestone.

1. Write `src/rover_env.py` with `RoverEnv(gymnasium.Env)` exactly as the
   contract in docs/contracts.md says. It uses `World` for every movement decision
   (never repeat the rules). `step` returns a Python `int` state and a
   `float` reward. Register it as `RoverGrid-v0` with
   `max_episode_steps=100`, only once (check `gym.registry` first).
2. Write `tests/test_env.py`, one test per criterion, all offline:
   - `check_env` with no error or warning, run on
     `gym.make("RoverGrid-v0").unwrapped` (an environment built directly has
     no spec and `check_env` warns);
   - rock, steep climb, fall, crater and destination, each with the exact
     `step` tuple shown below;
   - truncation exactly at step 100;
   - the state number of the example below;
   - `reset` raises `ValueError` for a start on a rock, on a crater, outside
     the map, and for an unknown destination (four cases of one
     parametrized test).
3. End `src/rover_env.py` with `if __name__ == "__main__":` and a demo that
   prints exactly the lines below. Run it with
   `uv run python src/rover_env.py`, then run `uv run pytest`.
4. Do not write any other file and do not change `src/world.py` or `data/`.

Expected output of the demo:

```
spaces: Discrete(162) Discrete(4)
rock: (110, -1.0, False, False, {})
steep climb: (120, -1.0, False, False, {})
fall: (140, -50.0, True, False, {})
crater: (122, -50.0, True, False, {})
destination: (54, 20.0, True, False, {})
reset: (109, {})
truncated at step 100: (108, -1.0, False, True, {})
check_env: ok
```

How each line is made (destination `M` unless noted; `reset` with
`options={"start": ..., "destination": ...}`):

- rock: start (0, 2), action 1 (right) into the rock at (0, 3);
- steep climb: start (1, 3), action 1;
- fall: start (2, 5), action 2 (down);
- crater: start (1, 4), action 1;
- destination: start (0, 1), destination `B`, action 3 (left);
- reset: start (0, 1), destination `M`;
- truncated: start (0, 0), destination `M`, action 0 (up) repeated until
  `truncated` is `True`; print the step number and the last tuple.

Acceptance criteria (show the full output of both commands):

- the demo output is identical to the expected output, line by line;
- `uv run pytest` ends with `12 passed` and no warnings.

Report: the files written, the full output, and the lines the student must
review (`reset`, the order of the checks in `step`, and the registration).
