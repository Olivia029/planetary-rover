---
description: Milestone 7 - write the tests of the agent, the model wrapper and the training; run pytest
allowed-tools: Bash(uv run pytest:*)
---

Milestone 7 of CLAUDE.md. Do only this milestone.

Write three new test files and add one test to an existing one. Every test is
offline: no Ollama, no network, no token. A failing test means a defect in
the code: never change a test to make it pass; report it instead.

1. `tests/test_agent.py`, with `ScriptedModel` (a helper
   `make_agent(script, max_steps=6)` returns `Agent(ScriptedModel(script),
   max_steps)`; `PLACES = Decision("tool", "list_places")` and `ROUTE =
   Decision("tool", "run_policy", {"row": 0, "col": 0, "destination": "M"})`).
   Ten tests:
   - valid route: script `[PLACES, ROUTE, answer "9 steps"]`; `run` returns
     `"9 steps"`; the tool names of `trace` are `list_places`, `run_policy`;
     `trace[1]` starts with `run_policy -> {"reached": true, "steps": 9,
     "return": 12.0`; `model.calls == 3`;
   - unknown place: script `[PLACES, answer "Which place do you mean?"]`;
     the answer is returned and `trace` has only `list_places`;
   - out of scope: script `[answer "Out of scope."]`; `trace == []` and
     `model.calls == 1`;
   - failing tool: `run_policy` with row 0, col 3, destination `B`, then an
     answer; `trace == ["run_policy -> ERROR: (0, 3) is a rock"]` and the
     answer is returned (the run goes on);
   - unknown tool `cancel`: `trace == ["cancel -> ERROR: unknown tool
     cancel"]`;
   - wrong arguments (`run_policy` with only `row`): `trace[0]` starts with
     `run_policy -> ERROR: `;
   - step budget: script `[PLACES]` with `max_steps=3`; `run` returns
     `"Stopped: step budget exhausted."`, `model.calls == 3`, `len(trace) ==
     3`;
   - system prompt: it contains the `description` of every tool in
     `TOOLS`, `0-5`, `0-8`, `top-left` and `out of scope`;
   - context: a spy model (a plain function that stores a copy of the context
     at each call; first call returns `PLACES`, second returns an answer);
     the roles of the second context are `["system", "user", "assistant",
     "user"]`, the assistant content contains `"tool": "list_places"` and the
     last message starts with `Observation: `;
   - trace line (use `capsys`): the first printed line starts with
     `[1] list_places -> [{` and has exactly `len("[1] list_places -> ") + 52`
     characters.
2. `tests/test_llm.py`, with a fake `ollama.chat` installed with
   `monkeypatch.setattr(llm.ollama, "chat", ...)` and a helper `reply(content,
   tool_calls)` that returns a `SimpleNamespace` with a `message` that has
   `content` and `tool_calls`. Five tests:
   - `tool_schemas`: the names are `list_places` and `run_policy`;
     `list_places` has no properties; `run_policy` has `row` and `col` of type
     `integer`, `destination` of type `string`, and `required` is
     `["row", "col", "destination"]`;
   - `to_messages`: a context with system, user, an assistant message (JSON
     `{"kind": "tool", "tool": "list_places", "args": {}}`) and a user message
     `Observation: [1, 2]` gives the roles `system`, `user`, `assistant`,
     `tool`; the assistant message has `tool_calls == [{"function": {"name":
     "list_places", "arguments": {}}}]` and the last one is `{"role": "tool",
     "tool_name": "list_places", "content": "[1, 2]"}`;
   - `clean`: reasoning before `</think>` is dropped; the content of
     `<answer>...</answer>` is kept alone; a plain text stays as it is;
   - a fake reply with a tool call (`run_policy`, row 0, col 0, destination
     `M`) gives `Decision("tool", "run_policy", {...})`; `calls == 1`; the
     call to `chat` had `model == "qwen3:4b"`, `think is False` and
     `options == {"temperature": 0}`;
   - a fake reply with text `reasoning\n</think>\n\n<answer>\nOut of
     scope.\n</answer>` gives `Decision("answer", text="Out of scope.")`.
3. `tests/test_training.py`, with `RoverAgent` and the project root found from
   the test file. Six tests:
   - same seed, same table: two agents with `seed=0` trained 30 episodes have
     equal `table.q`, and the table is not all zeros;
   - the saved `q_table.npy` has the shape `(observation_space.n, 4)`;
   - the saved table (loaded into `agent.table.q`) gives `shortest_rate() >=
     95.0`;
   - `save` to `tmp_path` writes a file that loads back equal;
   - training from scratch: `train(1500)` then `shortest_rate() >= 95.0`;
   - `update` receives `terminated`: wrap `agent.table.update` with a spy that
     records `(r, done)`, train 20 episodes, and assert that for every call
     `done == (r != -1.0)` (only the goal, +20, and the hazard, -50, end the
     episode).
4. Append one test to `tests/test_tools.py`, without changing the existing
   ones: a route that never arrives is cut at 100 steps. Use `monkeypatch` to
   make `tools.table.best_action` always return 0 (up, blocked at the top
   edge) and call `tools.run_policy(0, 1, "M")`; assert `reached is False`,
   `steps == 100`, `return == -100.0` and `len(path) == 101`.
5. Do not change any file in `src/`, `data/` or `q_table.npy`. Run
   `uv run pytest -v` and then `uv run pytest -q`.

Acceptance criteria (show the full output of both commands):

- `uv run pytest -q` ends with `44 passed` and no warnings (12 of the
  environment, 11 of the tools, 10 of the agent, 5 of the model wrapper and 6
  of the training);
- `uv run pytest -v` lists every test by name, so the student can check that
  the four agent cases (valid route, unknown place, out of scope, failing
  tool) are there.

Report: the files written, the full output, and the lines the student must
review (what each of the four agent cases asserts, and the spy in the
`update` test).
