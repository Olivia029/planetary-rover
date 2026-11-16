---
description: Milestone 3 - write src/train.py, train with random actions and save q_table.npy
allowed-tools: Bash(uv run python src/train.py), Bash(ls -l q_table.npy)
---

Milestone 3 of CLAUDE.md. Do only this milestone.

1. Write `src/train.py` with `RoverAgent(seed=0, alpha=0.5, gamma=0.9)` exactly
   as the contract in docs/contracts.md says, following `CliffAgent` from class:
   - `__init__`: `gym.make("RoverGrid-v0")`, `env.reset(seed=seed)`,
     `env.action_space.seed(seed)` and a `QTable` with
     `n_states = env.observation_space.n` and 4 actions;
   - `train(episodes)`: random actions from `env.action_space.sample()` and
     `table.update(s, a, r, s2, terminated)` at every step; the episode ends
     with `terminated or truncated`;
   - `shortest_rate() -> float`: for every destination and every free cell
     other than the destination cell, reset with
     `options={"start": ..., "destination": ...}`, follow
     `table.best_action` for at most 100 steps, and count the pair as good if
     the rover reaches the destination in exactly `World.shortest_steps`
     steps; return the percentage. Use the `World` of the environment
     (`env.unwrapped.world`); do not load the map again;
   - `save(filename)`: `np.save(filename, self.table.q)`.
2. Do not write any other file and do not change `src/world.py`,
   `src/rover_env.py`, `src/q_table.py` or `data/`.
3. End `src/train.py` with `if __name__ == "__main__":` and a demo that
   trains 1500 episodes with the default configuration, prints exactly the
   lines below and saves `q_table.npy` in the project root. Run it with
   `uv run python src/train.py`, then run `ls -l q_table.npy`.

Expected output:

```
random training: 1500 episodes
shortest routes: 100.0 %
saved q_table.npy: (162, 4)
```

Acceptance criteria (show the full output of both commands):

- the demo output is identical to the expected output, line by line (the
  minimum required by the practice is 95.0 %; with the fixed seed the value
  is 100.0 %);
- `ls -l q_table.npy` shows a file of 5312 bytes (162 x 4 values x 8 bytes
  plus the 128-byte header).

Report: the file written, the full output, and the lines the student must
review (`train`, and how `shortest_rate` decides that a route is the shortest).
