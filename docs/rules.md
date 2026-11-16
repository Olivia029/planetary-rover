# Rules: data, movement, rewards and states

Part of the specification of `planetary-rover`. `CLAUDE.md` has the summary.

## Data (`data/`, UTF-8)

- `map.txt`: 6 rows x 9 columns, one row per line. `.` free, `#` rock
  (obstacle), `~` crater (hazard), one uppercase letter per named place:
  `A` antenna, `B` base, `M` rock sample.
- `heights.txt`: same size, one digit 0-9 per cell (height level); the
  height of `#` cells is ignored.
- `traces.txt`: the real output of `uv run python src/main.py`, pasted by the
  student (four cases). Only the viewer reads it.
- Rows, columns and number of states come from the files, never as
  numbers written in the code.

## Movement rules (`world.py` is the only place that defines them)

- Actions: 0 up, 1 right, 2 down, 3 left. `MAX_CLIMB = 1`, `MAX_DROP = 2`,
  `MAX_STEPS = 100`.
- A move goes to a neighbor with `delta = height(neighbor) - height(cell)`:
  1. outside the map or `#` -> **blocked** (stays in its cell);
  2. `delta > MAX_CLIMB` (too steep to climb) -> **blocked**;
  3. neighbor is `~`, or `delta < -MAX_DROP` (a fall) -> **hazard** (enters
     the neighbor cell);
  4. otherwise **moved**.
- The map says what a cell is (rock, crater, place); the heights say how high
  it is. Both layers are read by `World.move` and by nothing else.
- Places (`A`, `B`, `M`) are free cells. Stepping on a place that is not the
  destination is an ordinary step.

## Rewards and end of the episode

- -1 for moved and blocked; +20 on entering the destination cell;
  -50 on hazard.
- `terminated` on destination or hazard; `truncated` at `MAX_STEPS`
  (`max_episode_steps` in `register`).
- `reset` draws a destination and a free start cell other than the
  destination, so that training visits every cell.

## States

- Destinations are numbered by letter order: `A` 0, `B` 1, `M` 2.
  State = `dest_index * (rows * cols) + row * cols + col` (162 states).

## Reference route

- Breadth-first search over **moved** moves only, never entering a crater.
  It is directed: climbing and descending differ, so A to B can differ
  from B to A.
