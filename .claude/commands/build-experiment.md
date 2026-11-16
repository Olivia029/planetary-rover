---
description: Milestone 4 - write src/experiment.py and draw the learning curves
allowed-tools: Bash(uv run python src/experiment.py), Bash(ls -l results/learning_curves.png)
---

Milestone 4 of CLAUDE.md. Do only this milestone.

1. Write `src/experiment.py` exactly as the contract in docs/contracts.md says:
   - constants `CONFIGS = [(0.5, 0.9), (0.1, 0.9), (0.5, 0.5)]` (alpha,
     gamma), `BLOCKS = 10` and `BLOCK_SIZE = 100`;
   - `curve(alpha, gamma) -> list[float]`: a `RoverAgent(seed=0, alpha=...,
     gamma=...)` trains 100 episodes at a time and, after each block, adds
     `shortest_rate()` to the list (10 values: after 100, 200 ... 1000
     episodes);
   - use `matplotlib` with the `Agg` backend (it draws to a file, no window).
     One line with markers per configuration, labelled
     `alpha=<a> gamma=<g>`, a dashed gray line at 95 labelled `95 % target`,
     axis labels `training episodes` and `% of shortest routes`, y axis from
     0 to 105, legend and grid;
   - the figure is saved as `results/learning_curves.png` in the project
     root (create `results/` if it does not exist), found from the module
     with `Path(__file__).parent.parent`.
2. Do not write any other file and do not change `src/train.py`,
   `src/world.py`, `src/rover_env.py`, `src/q_table.py` or `data/`. Do not
   overwrite `q_table.npy`.
3. End the module with `if __name__ == "__main__":` and a demo that prints
   exactly the lines below (a header with the episodes, one line per
   configuration with the values in format `5.1f`, then the saved file).
   Run it with `uv run python src/experiment.py`, then run
   `ls -l results/learning_curves.png`.

Expected output:

```
episodes:   100   200   300   400   500   600   700   800   900  1000
alpha=0.5 gamma=0.9:  29.4  50.8  54.8  61.9  79.4  88.9  98.4  97.6  97.6  97.6
alpha=0.1 gamma=0.9:  15.9  16.7  31.0  32.5  38.1  45.2  46.8  49.2  50.0  52.4
alpha=0.5 gamma=0.5:  25.4  44.4  49.2  53.2  55.6  63.5  77.8  79.4  86.5  86.5
saved results/learning_curves.png
```

Acceptance criteria (show the full output of both commands):

- the demo output is identical to the expected output, line by line (the
  seeds are fixed, so the numbers are always the same);
- `ls -l results/learning_curves.png` shows that the file exists and is not
  empty.

Report: the files written, the full output, and the lines the student must
review (how a block is trained and measured, and where `CONFIGS` is used).
