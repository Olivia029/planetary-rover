# Viewer (milestones 9 and 10)

Part of the specification of `planetary-rover`. A small app-like window that
shows the Mars grid, how the rover moves, the calculations and the results.
It is a way to look at what the project already does; it adds no behavior.
Milestone 9 builds it with saved results (no model). Milestone 10 adds a live
chat with the real model; the page must keep working without it.

## Limits

- Only new files: `src/viewer.py`, `tests/test_viewer.py` and the generated
  `results/viewer.html`. No file of milestones 0-8 changes (not even
  `README.md`: the viewer is mentioned only in `docs/requirements.md`).
- One self-contained HTML file: HTML, CSS and JavaScript inline, data inline
  as JSON. No server, no network, no CDN, no library, no new dependency.
  It opens with a double click and works offline.
- The JavaScript only draws. Every number it shows (routes, Q values,
  outcomes, rewards, curves) is computed by Python with the project's code;
  the movement rules are never written again in JavaScript.
- Plain vanilla JavaScript, a few hundred lines at most. If something does not
  fit in these limits, report it instead of growing the viewer.

## `src/viewer.py`

- `build_data() -> dict`, all of it JSON-serializable:
  - `world`: `rows`, `cols`, `symbols` (list of strings), `heights` (list of
    lists), `places` (letter -> `[row, col]` and name), `max_height`.
  - `routes`: one entry for every (origin, destination) pair of free cells
    (origin different from the destination, 126 in total), each with
    `origin`, `destination`, `reached`, `steps`, `return`, `shortest` (from
    `World.shortest_steps`) and `moves`: one item per step with `cell` (before
    the step), `state`, `q` (the four values of `table.q[state]`), `action`
    (`best_action`), `outcome` (`moved`, `blocked` or `hazard`), `reward`,
    `next` (cell after the step) and `total` (return so far).
  - `policy`: for each destination letter, for every free cell, the best
    action and the largest Q value.
  - `curves`: the three configurations of `experiment.py` with their % of
    shortest routes after each block of 100 episodes. Reuse its functions and
    constants; do not change `experiment.py`.
  - `traces`: the four cases parsed from `data/traces.txt` (`request`, list of
    `{"tool", "result"}` and `answer`).
- The steps of a route come from `env.reset(options=...)`, `table.best_action`
  and `env.step` (the same loop as `run_policy`), recording `table.q[state]`.
  `steps`, `return` and the path must equal those of `tools.run_policy`.
- `write_html(path)` writes the page. Running `uv run python src/viewer.py`
  writes `results/viewer.html` and prints: the path, the number of routes
  (126), the number of curves (3) and the number of traces (4).
- Paths are found from `Path(__file__).parent.parent`; nothing is absolute.

## Look (an app, not a web page)

- Full window layout, no scrolling of the page: a left bar with the title and
  the places, a top bar of tab buttons, a main area and a status bar at the
  bottom. Dark Mars theme (dark background, sand and rust accents).
- Heights are colors: one sequential scale from 0 to 9, dark brown for low
  ground to pale sand for high ground, with a legend. The height number is
  also written in every cell, so color is never the only cue.
- Rock: dark grey with a texture. Crater: black circle with a ring. Places:
  a round badge with the letter (`A`, `B`, `M`) and the name in the left bar.
- A badge in the status bar always says which mode is on: `Saved results -
  no model` or `Live - Ollama - qwen3:4b`.
- Buttons are real `<button>` elements, reachable with the keyboard, with a
  visible focus and a "selected" state. Works from 960 px of width.

## Tabs (buttons that change the main area)

| Tab | Shows |
|---|---|
| Map | the terrain with heights, rocks, craters and places; hovering a cell shows its symbol, height and state number for the chosen destination |
| Route | choose an origin (click a cell) and a destination; the rover moves step by step with play, pause, step, back, reset and speed; a table beside it lists, for each step so far: cell and height, the state formula with its numbers, the four Q values with the best one marked, action, outcome, reward and return; a result card gives reached, steps, return and the BFS shortest steps |
| Policy | for a chosen destination, the best arrow of every cell, with a switch to a heat map of the largest Q value |
| Learning | the three curves with the 95 % line, and a table of the values per block |
| Agent | the four cases of `data/traces.txt`: request, tool calls with their results and the answer; the tools called are marked with a badge; at the top, a switch with two buttons, `Saved results` (selected) and `Live chat`, which is disabled in milestone 9 and says how to start it: `uv run python src/serve.py` (needs Ollama and `qwen3:4b`) |

- The status bar always shows the chosen origin, destination, steps and
  return, and the outcome of the last step.
- A hazard step flashes the cell and ends the animation; a blocked step shows
  the rover staying in place.

## Tests (`tests/test_viewer.py`, exactly two, offline)

1. For all 126 pairs, `steps`, `return` and the path of `build_data()` equal
   the result of `tools.run_policy`, and every `moves` list ends at the
   destination when `reached` is true.
2. `write_html(tmp_path / "viewer.html")` writes one file that contains the
   five tab names, contains no `http` source (`src=` or `href=`), and
   `traces` has four cases, the first one with the tools `list_places` and
   `run_policy`.

## Acceptance (what the command checks)

- `shasum -a 256` of `src/*.py` (without `viewer.py`), `data/*` and
  `q_table.npy` is identical before and after.
- `uv run pytest -q` ends with `46 passed`; the 44 earlier tests are unchanged.
- `uv run python src/viewer.py` prints the four lines above and
  `results/viewer.html` exists.
- The student opens the page and checks each tab by eye; Claude Code takes a
  screenshot of each tab with the Playwright browser if it is available.

## Live mode (milestone 10)

The same page can chat with the real agent. The model is fixed: **`qwen3:4b`
with Ollama**, and the page must say so everywhere the mode is visible.

- Only new file `src/serve.py` (plus changes to `src/viewer.py` and
  `tests/test_viewer.py`, the files of milestone 9). No file of milestones
  0-8 changes (`llm.py`, `agent.py` and `tools.py` are used as they are). No
  new dependency: `http.server` of the standard library.
- `uv run python src/serve.py` serves the page at `http://127.0.0.1:8000`
  (fixed port, only this computer, one request at a time) and prints
  `serving http://127.0.0.1:8000 (Ollama, model qwen3:4b)`.
- `make_server(model_factory, port)` builds the server; `main()` uses
  `OllamaModel` as the factory and port 8000. Tests use another factory and
  port 0.
- `GET /` is the same page as `results/viewer.html`.
- `GET /api/status` answers `{"live": true, "model": "qwen3:4b",
  "ollama": bool, "installed": bool}`; `ollama` is true if `ollama.list()`
  answers, `installed` if a model named `qwen3:4b` is in it. Any exception
  gives false, never an error.
- `POST /api/chat` takes `{"request": "<text>"}` (at most 500 characters),
  runs a NEW `Agent(model_factory())` and answers `{"answer", "trace",
  "route"}`: `trace` is a list of `{"tool", "result"}` split from
  `Agent.trace` at the first ` -> ` (full results, not cut), and `route` is
  the precomputed route of `build_data()` whose path equals the path returned
  by `run_policy`, or `null` (no tool route, an error, or none found). Any
  exception gives HTTP 502 and `{"error": "<message>"}`; the server keeps
  running.
- The page asks `/api/status` when it opens. If it cannot reach it (opened
  from a file, for example), it stays in saved-results mode. `Live chat` is
  enabled only if `ollama` and `installed` are true; otherwise it stays
  disabled and says why: not started with `serve.py`, Ollama not running, or
  `ollama pull qwen3:4b` needed.
- Chat: a text box and a Send button; while waiting it shows "qwen3:4b is
  thinking..." (answers can take minutes). Each reply shows its tool calls
  with their results and the answer, under the label `qwen3:4b via Ollama`,
  and a note: the numbers come from the tools, not from the model. If `route`
  is not null, the Route tab is set to that route and the rover moves.
  An error is shown in the chat, in plain words.
- Nothing is saved: closing the page loses the chat.

### Tests of milestone 10 (two more, offline, no Ollama)

1. With `make_server` and a factory that returns `ScriptedModel([Decision(
   "tool", "run_policy", {"row": 0, "col": 0, "destination": "M"}),
   Decision("answer", text="9 steps")])`, a `POST /api/chat` returns the
   answer `9 steps`, a trace with the tool `run_policy` and a route with
   9 steps; `GET /api/status` has `live` true and `model` `qwen3:4b`.
2. With a factory that raises, `POST /api/chat` returns 502 with an `error`,
   and a later `GET /api/status` still answers.

### Acceptance of milestone 10

- `shasum -a 256 -c` is OK for the files of milestones 0-8.
- `uv run pytest -q` ends with `48 passed`.
- `uv run python -c "import serve; print('imports ok')"` prints `imports ok`.
  Claude Code does not start the server (it blocks) and does not call
  Ollama; the student starts it and checks the page.
