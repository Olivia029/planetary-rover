---
description: Milestone 11 - write docs/requirements.md (where the code meets each requirement) and update README.md
allowed-tools: Bash(uv run pytest:*), Bash(uv run python -c:*), Bash(wc -l:*), Bash(shasum:*), Bash(grep:*)
---

Milestone 11 of CLAUDE.md. Do only this milestone. The only file that changes
besides the new one is `README.md`, and only as step 3 says.

0. Gather the facts first: read `docs/statement.md` (the source of R1-R7, the
   common rules and the Gymnasium pieces: never write them from memory), then
   `src/`, `tests/`, the rest of `docs/`, `CLAUDE.md` and `.claude/`, and run `uv run pytest --collect-only -q` to get the real names
   of the tests. Write nothing that you have not seen in a file or in an
   output.
1. Write `docs/requirements.md`, in English, at most 150 lines, with:
   - a short "How to read it" note: every code reference is written
     `` `path::name` `` (file, then class, function or test, like
     `src/world.py::World.move`), never with line numbers;
   - table 1, the common rules of the themes (map, actions, rewards, end,
     start, state, interface): rule, how this project meets it, where;
   - table 2, the Gymnasium pieces (`gymnasium.Env`, `observation_space`,
     `action_space`, `reset(seed, options)`, `step`, `register` and `make`,
     `check_env`): what Gymnasium asks and where it is met;
   - table 3, the seven requirements R1-R7: what it demands, where the code
     meets it, the tests that check it (real names), the command that shows
     it and the result to expect (`48 passed` only if the output
     says so);
   - a section "Additions to the standard statement": the heights
     (`data/heights.txt`, `MAX_CLIMB`, `MAX_DROP`, a fall above `MAX_DROP` is
     a hazard), the map written by the student, and the viewer with its live chat;
   - a section "Who writes what": student, Claude Code, program.
2. Check the references with one command:
   `uv run python -c "..."` that reads `docs/requirements.md`, extracts every
   `` `path::name` ``, asserts that the file exists and that every dotted part
   of `name` appears as text in that file, and prints
   `citations ok: <n>` (or the first failure).
3. `README.md`: if it exists, update it and nothing else of it. If it does not
   exist (the student may have lost it), write it again following step 1 of
   `.claude/commands/finish.md` (same sections and real commands), already with
   the updates below. The updates: the expected result of the tests is
   `48 passed`; two lines in the run list, after `src/main.py`:
   `uv run python src/viewer.py` (writes `results/viewer.html`, saved
   results, no model) and `uv run python src/serve.py` (live chat, needs
   Ollama and `qwen3:4b`); and the files `docs/`, `src/viewer.py`,
   `src/serve.py` and `results/viewer.html` in the layout tree. At most 80
   lines and 80 characters per line. Say in the report which case happened.
4. Do not write any other file.
5. Run, one command at a time, and show the full output: the citation check,
   `uv run pytest -q`, `wc -l README.md docs/requirements.md CLAUDE.md`,
   `shasum -a 256 -c /tmp/before.sha` (the file of milestone 9; if it does not
   exist, run `shasum -a 256 src/*.py q_table.npy data/*` and show it), and
   `grep -rnE "/Users/|/home/" --exclude-dir=.venv --exclude-dir=.git
   --exclude-dir=.claude .` (must print nothing).

Acceptance criteria:

- `citations ok: <n>` is printed with no failure;
- `uv run pytest -q` ends with `48 passed`;
- `README.md` has at most 80 lines and says `48 passed`; `CLAUDE.md` has less
  than 200 lines; the files of `src/` and `q_table.npy` are unchanged;
- the `grep` prints nothing.

Report: the files written, the full output, a diff of `README.md`, and the
lines the student must review: the table of R1-R7 (every "where" and every
test name) and the section of additions.
