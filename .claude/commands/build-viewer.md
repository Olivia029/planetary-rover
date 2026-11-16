---
description: Milestone 9 - write src/viewer.py, tests/test_viewer.py and results/viewer.html
allowed-tools: Bash(shasum:*), Bash(uv run pytest:*), Bash(uv run python src/viewer.py), Bash(ls:*), Bash(test:*), Bash(grep:*)
---

Milestone 9 of CLAUDE.md. Do only this milestone. Read `docs/viewer.md`,
`docs/rules.md` and `docs/contracts.md` first: the viewer is specified there
to the letter.

0. Before writing anything, check the starting point:
   - `test -f data/traces.txt`: if it does not exist, stop and tell the
     student (it is the student's file; do not create it);
   - `uv run pytest -q` must end with `44 passed`;
   - `shasum -a 256 src/*.py q_table.npy data/* > /tmp/before.sha` and show
     the output.
1. Write `src/viewer.py` as `docs/viewer.md` says: `build_data()`,
   `write_html(path)`, the parser of `data/traces.txt` and, at the end,
   `if __name__ == "__main__":` that writes `results/viewer.html` and prints
   exactly these four lines:

   ```
   viewer: results/viewer.html
   routes: 126
   curves: 3
   traces: 4
   ```

   It imports and reuses `world`, `rover_env`, `tools`, `train` and
   `experiment`; it does not copy their rules and does not change them. If a
   function of those modules does not fit what the viewer needs, stop and
   report it instead of changing that module.
2. Write `tests/test_viewer.py` with exactly the two tests of
   `docs/viewer.md`. Do not change any existing test.
3. Do not write any other file. Do not run `src/main.py` (it needs Ollama).
   Do not install anything.
4. Run, one command at a time, and show the full output:
   - `uv run python src/viewer.py`;
   - `uv run pytest -q`;
   - `shasum -a 256 -c /tmp/before.sha`;
   - `ls -l results/viewer.html`;
   - `grep -nE "(src|href)=.?https?:" results/viewer.html` (must print
     nothing);
   - `grep -nE "/Users/|/home/" results/viewer.html src/viewer.py` (must
     print nothing).

Acceptance criteria:

- `viewer.py` prints the four lines above, in that order;
- `uv run pytest -q` ends with `46 passed` and no warnings;
- `shasum -c` reports `OK` for every file (nothing of milestones 0-8 changed);
- `results/viewer.html` exists and the two `grep` commands print nothing.

Report: the files written, the full output of the commands, and the lines the
student must review: how a route is recorded in `build_data` (the loop with
`env.step`, and why its `steps`, `return` and path equal those of
`run_policy`), `parse_traces`, and the two tests. Then list what the student
checks by opening `results/viewer.html` (`open results/viewer.html`):

- Map: heights shown as colors and as numbers; rocks, craters and places;
- Route: B to M plays 9 steps and the status bar ends at return 12.0; a route
  from the cell (0, 3) cannot be chosen (rock);
- Policy: the arrows change when the destination changes;
- Learning: three curves, the best one above the 95 % line from 700 episodes;
- Agent: four cases, the second one with only `list_places`; the `Live chat`
  button is disabled and says how to start it;
- the status bar says `Saved results - no model`.
