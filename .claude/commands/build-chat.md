---
description: Milestone 10 - add the live chat (qwen3:4b with Ollama) to the viewer: src/serve.py
allowed-tools: Bash(shasum:*), Bash(uv run pytest:*), Bash(uv run python -c:*), Bash(uv run python src/viewer.py), Bash(ls:*), Bash(grep:*), Bash(ollama list)
---

Milestone 10 of CLAUDE.md. Do only this milestone. Read the section "Live
mode (milestone 10)" of `docs/viewer.md` first: it is the specification, to
the letter. The model is fixed (`qwen3:4b` with Ollama) and the page must say
so.

0. Check the starting point:
   - `test -f src/viewer.py` and `uv run pytest -q` ends with `46 passed`;
   - `shasum -a 256 src/*.py q_table.npy data/* > /tmp/before10.sha`, and
     show the output (it includes `viewer.py` as milestone 9 left it).
1. Write `src/serve.py` as the specification says: `make_server(model_factory,
   port)`, the three routes (`GET /`, `GET /api/status`, `POST /api/chat`),
   and `main()` that uses `OllamaModel` and port 8000 and prints
   `serving http://127.0.0.1:8000 (Ollama, model qwen3:4b)`. Standard library
   only; bind to `127.0.0.1`.
2. Extend `src/viewer.py` (and only that file of milestone 9) so that the page
   has the live mode: the mode switch of the Agent tab, the status check, the
   chat, the badge `Live - Ollama - qwen3:4b` and the reasons why `Live chat`
   is disabled. `results/viewer.html` must still work opened from a file, in
   saved-results mode, with no server.
3. Append the two tests of milestone 10 to `tests/test_viewer.py` without
   changing the existing ones. They use a fake model factory and port 0; no
   Ollama.
4. Do not change any file of milestones 0-8 (`llm.py`, `agent.py` and
   `tools.py` are used as they are). Do not start the server and do not run
   `src/main.py`: both need the student. Do not install anything.
5. Run, one command at a time, and show the full output:
   - `uv run python src/viewer.py` (it must print the same four lines as
     before and write `results/viewer.html`);
   - `uv run python -c "import serve; print('imports ok')"`;
   - `uv run pytest -q`;
   - `shasum -a 256 -c /tmp/before10.sha`, and then `shasum -a 256
     src/viewer.py` to show the new hash of the file of milestone 9 (it is
     the only file allowed to differ; say so);
   - `grep -nE "(src|href)=.?https?:" results/viewer.html` (must print
     nothing) and `grep -nE "/Users/|/home/" results/viewer.html src/serve.py
     src/viewer.py` (must print nothing);
   - `ollama list`.

Acceptance criteria:

- `uv run pytest -q` ends with `48 passed` and no warnings;
- `shasum -c` is OK for every file except `src/viewer.py`;
- `imports ok` is printed, the two `grep` print nothing;
- `ollama list` shows `qwen3:4b` (if not, tell the student to run
  `ollama pull qwen3:4b`).

Report: the files written, the full output, and the lines the student must
review: the routes of `serve.py` (how `/api/chat` builds `answer`, `trace` and
`route`, and the 502 on errors) and the two tests. Then list what the student
checks by hand:

1. Without the server: open `results/viewer.html`; the badge says `Saved
   results - no model`, everything works and `Live chat` is disabled with the
   reason.
2. With the server: in one terminal `uv run python src/serve.py`, then open
   `http://127.0.0.1:8000` (Ollama open); the badge says `Live - Ollama -
   qwen3:4b` and `Live chat` is enabled.
3. In the chat, send the four requests of `main.py`. The first one moves the
   rover on the Route tab (9 steps, return 12.0); the cafeteria one calls only
   `list_places`; the capital of France calls no tool; the (0, 3) one shows
   the rock error.
4. With Ollama closed, reload: `Live chat` is disabled and says that Ollama
   is not running.
