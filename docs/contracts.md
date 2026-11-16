# Module contracts

Part of the specification of `planetary-rover`. The movement rules are in
`docs/rules.md`; the viewer is in `docs/viewer.md`.

**`world.py`.** `World.load(map_path, heights_path)` validates both files
(same size, known symbols, digits), else `ValueError`. Attributes `rows`,
`cols`, `places` (letter -> (row, col), sorted by letter).
`move(cell, action) -> (cell, outcome)` with outcome `"moved"`, `"blocked"`
or `"hazard"`; `symbol(cell)`; `height(cell)`; `free_cells()` (not `#`, not
`~`); `shortest_steps(start, goal) -> int | None` (BFS).

**`rover_env.py`.** `RoverEnv(gymnasium.Env)`: `observation_space =
Discrete(n_places * rows * cols)`, `action_space = Discrete(4)`.
`reset(seed=None, options=None)` calls `super().reset(seed=seed)`; it draws
destination and start (a free cell other than the destination) with
`self.np_random`, or with `options={"start": (row, col), "destination":
"B"}` starts there (`ValueError` for a rock, crater or outside start, or an
unknown destination). Returns `(state, {})`. `step(action)` returns
`(state, reward, terminated, truncated, {})`. Registered as `RoverGrid-v0`
with `max_episode_steps=100`.

**`train.py`.** `RoverAgent(seed=0, alpha=0.5, gamma=0.9)`, like
`CliffAgent`: `gym.make`, `env.reset(seed=seed)`, `env.action_space.seed(seed)`
and a `QTable`. `train(episodes)`: `env.action_space.sample()` and
`table.update(s, a, r, s2, terminated)` at every step. `shortest_rate() ->
float`: percentage of (origin, destination) pairs (free cells except the
destination) that reach it with `best_action` in exactly `shortest_steps`
steps (limit 100). `save(filename)` uses `np.save`. Running the module
trains, prints the rate and saves `q_table.npy`.

**`experiment.py`.** At least two configurations (`alpha`, `gamma`), fixed
seeds. Per configuration: blocks of 100 episodes, `shortest_rate()` after
each; one curve each in `results/learning_curves.png`; prints the values.

**`tools.py`.** Tools return `str` (JSON). The table is loaded once with
`np.load("q_table.npy")`; it is never trained or modified.
`list_places()`: JSON list of `{"letter", "name", "row", "col"}` (`A`
antenna, `B` base, `M` rock sample). `run_policy(row, col, destination) ->
dict` with `reached` (bool), `steps` (int), `return` (float) and `path`
(list of `[row, col]`, start included): validates, places the rover with
`env.reset(options=...)`, applies `best_action` for at most 100 steps (start
equal to destination: 0 steps). `ValueError` with a clear message for: cell
outside the map, rock, crater, unknown destination. `Tool(function,
description)`, `TOOLS: dict[str, Tool]`; the registry turns the `dict` into
JSON.

**`model.py`.** As in class: `Decision(kind, tool="", args={}, text="")`
(`kind` `"tool"` or `"answer"`); `ScriptedModel(script)` returns the
decisions in order, repeats the last, keeps `calls`. A model is any callable
`model(context: list[dict]) -> Decision`.

**`llm.py`.** `OllamaModel(name="qwen3:4b")`, same contract; `think=False`,
temperature 0, native Ollama tool calling (`tools=` built from `TOOLS` with
`inspect`). Context -> Ollama messages (assistant decision -> `tool_calls`,
`Observation` -> `tool`); a tool call is a tool `Decision`, else the text
answer without `<think>` blocks or `<answer>` tags. Keeps `calls`.

**`agent.py`.** `Agent(model, max_steps=6)`.
- `system_prompt()`: rover mission assistant, grid size (rows 0-5, columns
  0-8, (0, 0) top-left), one line per tool description, and the rules:
  `list_places` gives places and cells; `run_policy` gives every route and
  number, copied, never computed; unknown place: ask which one and do not
  call `run_policy`; not about rover routes: say it is out of scope, no tool;
  never repeat a tool call with the same arguments: use its Observation next.
- `act(name, args) -> str`: unknown tool gives `"ERROR: unknown tool <name>"`;
  a tool exception gives `"ERROR: <message>"`. `act` never raises.
- `run(request) -> str`: context `[system, user]`; each step asks the model;
  `answer` returns its text; `tool` calls `act`, appends `"<tool> -> <result>"`
  to `trace`, prints `[n] <tool> -> <result[:52]>`, and adds to the context the
  decision as an `assistant` message (JSON `kind`, `tool`, `args`) and then
  `"Observation: <result>"` as `user`. Past `max_steps` it returns
  `"Stopped: step budget exhausted."`.
