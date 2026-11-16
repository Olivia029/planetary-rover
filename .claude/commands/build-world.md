---
description: Milestone 1 - write src/world.py (map, heights, movement rules, BFS)
allowed-tools: Bash(uv run python src/world.py), Bash(ls:*)
---

Milestone 1 of CLAUDE.md. Do only this milestone.

1. Write `src/world.py` with the `World` class exactly as the contract in
   docs/contracts.md says: `load`, `rows`, `cols`, `places`, `move`, `symbol`,
   `height`, `free_cells` and `shortest_steps`. Define the constants
   `MAX_CLIMB`, `MAX_DROP` and `MAX_STEPS` and the movement rules there, and
   nowhere else. `shortest_steps` is a breadth-first search with a FIFO queue
   that follows only `"moved"` moves and never enters a crater.
2. Do not write any other file and do not read or change `data/`.
3. End the module with `if __name__ == "__main__":` and a demo that prints
   exactly the lines below (cells and tuples printed with Python's default
   format). Then run it with `uv run python src/world.py`.

Expected output:

```
grid: 6 rows x 9 columns
places: A (0, 8), B (0, 0), M (5, 4)
free cells: 43
pairs: 126, unreachable: 0
B -> A: 16 steps
A -> B: 16 steps
B -> M: 9 steps
M -> B: 9 steps
move((0, 1), 1) -> ((0, 2), 'moved')
move((0, 0), 0) -> ((0, 0), 'blocked')
move((1, 3), 1) -> ((1, 3), 'blocked')
move((2, 5), 2) -> ((3, 5), 'hazard')
move((1, 4), 1) -> ((1, 5), 'hazard')
```

`pairs` counts every (origin, destination) with the origin a free cell other
than the destination cell; `unreachable` counts the pairs with no route.

Acceptance criterion: the printed output is identical to the expected output,
line by line. Show the full output.

Report: the file written, the full output, and the lines the student must
review (the four outcomes of `move` and the BFS loop).
