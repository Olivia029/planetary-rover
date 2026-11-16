---
description: Milestone 6 - write src/model.py, src/llm.py, src/agent.py and src/main.py
allowed-tools: Bash(uv run python src/model.py), Bash(uv run python -c:*), Bash(ollama list)
---

Milestone 6 of CLAUDE.md. Do only this milestone.

1. Write `src/model.py` as in class (Topic 2, `ScriptedModel`):
   `Decision(kind, tool="", args={}, text="")` as a dataclass and
   `ScriptedModel(script)` as a dataclass with `calls`; it returns the
   decisions in order and repeats the last one. It imports nothing from the
   project.
2. Write `src/agent.py`, `Agent(model, max_steps=6)`, exactly as the contract
   in docs/contracts.md says, with `trace: list[str]`:
   - `system_prompt()`: built from `tools.TOOLS` and `tools.world`: the role,
     the map size (rows and columns from the world, (0, 0) top-left), one line
     `- <description>` per tool, and the four rules of system_prompt in docs/contracts.md (use `list_places` for places and cells; `run_policy` for every route and number, copied and never computed; unknown place: ask which one and do not call `run_policy`; not about rover routes: out of scope, no tool),
     plus a fifth rule: `Never repeat a tool call with the same arguments:
     use its Observation for the next step, then answer.`;
   - `act(name, args) -> str`: unknown tool gives
     `"ERROR: unknown tool <name>"`; any exception of the tool gives
     `"ERROR: <message>"`. It never raises;
   - `run(request) -> str`: context `[system, user]`; at each step ask the
     model; `answer` returns its text; `tool` calls `act`, appends
     `"<tool> -> <result>"` to `trace`, prints `[n] <tool> -> <result[:52]>`,
     and then adds TWO messages to the context, in this order: first the
     decision of the model as `{"role": "assistant", "content":
     json.dumps({"kind": "tool", "tool": <tool>, "args": <args>})}`, then
     `{"role": "user", "content": "Observation: <result>"}`. The assistant
     message is essential: without it the model does not see that it already
     called the tool and repeats the same call until the budget runs out; past
     `max_steps` it returns `"Stopped: step budget exhausted."`.
   `agent.py` has no demo.
3. Write `src/llm.py` with `OllamaModel(name="qwen3:4b")` as a dataclass with
   `calls`, same contract as `ScriptedModel` (callable `model(context) ->
   Decision`). It imports `Decision` from `model` and `TOOLS` from `tools`. It
   uses NATIVE Ollama tool calling (the `ollama` package, no token); the
   hand-made JSON protocol does not work with a 4B model (it copies the last
   Observation instead of deciding). Write three helpers and the class:
   - `tool_schemas() -> list[dict]`: one OpenAI-style schema per `TOOLS`
     entry: `{"type": "function", "function": {"name": <key>, "description":
     <tool.description>, "parameters": {"type": "object", "properties":
     ..., "required": [...]}}}`. The properties come from
     `inspect.signature(tool.function).parameters`, mapping the annotations
     `int` to `"integer"`, `float` to `"number"`, `str` to `"string"` and
     `bool` to `"boolean"`; all parameters are required;
   - `to_messages(context) -> list[dict]`: the system message as it is; a
     message with role `assistant` (its content is the JSON text of the
     decision: `kind`, `tool`, `args`) becomes `{"role": "assistant",
     "content": "", "tool_calls": [{"function": {"name": <tool>,
     "arguments": <args>}}]}` and remembers the tool name; a `user` message
     that starts with `Observation: ` becomes `{"role": "tool", "tool_name":
     <last tool name>, "content": <text without the prefix>}`; any other
     message is copied;
   - `clean(text) -> str`: the model sometimes leaks its reasoning. Keep only
     what follows the last `</think>`; if the rest contains
     `<answer>...</answer>`, keep only the content between the tags; strip
     spaces;
   - `OllamaModel.__call__`: add 1 to `calls`; `ollama.chat(model=self.name,
     messages=to_messages(context), tools=tool_schemas(), think=False,
     options={"temperature": 0})`; if `reply.message.tool_calls` is not
     empty, take the first call and return `Decision("tool", call.function.name,
     dict(call.function.arguments))`; otherwise return
     `Decision("answer", text=clean(reply.message.content or ""))`.
   Do not use `format="json"` or a `FORMAT` text. `llm.py` has no demo and is
   the only module that uses the network.
4. Write `src/main.py`: a list `REQUESTS` with these four requests, in this
   order, and a `main()` that creates one `OllamaModel`, and for each
   request prints `=== case <n> ===` and `request: <text>`, creates a **new**
   `Agent(model)`, runs it and prints `answer: <text>`. The agent prints the
   tool lines itself. No arguments.
   1. `The rover is at the base. How does it reach the rock sample, and how
      many steps does it take?`
   2. `Take the rover from the base to the cafeteria.`
   3. `What is the capital of France?`
   4. `The rover is at row 0, column 3. How does it reach the base?`
5. Do not write any other file and do not change the files of milestones 0-5,
   `data/` or `q_table.npy`. Do not write tests yet (milestone 7).
6. Run `uv run python src/model.py` and
   `uv run python -c "import agent, llm, main; print('imports ok')"`, and
   `ollama list`. Do NOT run `src/main.py`: the student runs it, because it
   calls the real model and can take several minutes.

Expected output of `uv run python src/model.py`:

```
Decision(kind='tool', tool='list_places', args={}, text='')
Decision(kind='answer', tool='', args={}, text='done')
Decision(kind='answer', tool='', args={}, text='done')
calls: 3
```

The demo of `model.py` builds `ScriptedModel([Decision("tool",
"list_places"), Decision("answer", text="done")])`, calls it three times with
`[]` and prints each decision, then `calls:` and the counter.

Acceptance criteria (show the full output of the three commands):

- the output of `model.py` is identical to the expected output;
- the import check prints `imports ok`;
- `ollama list` shows `qwen3:4b` (if not, tell the student to run
  `ollama pull qwen3:4b`).

Report: the files written, the full output, and the lines the student must
review (`Agent.act`, `Agent.run`, the rules in `system_prompt`, and how
`OllamaModel` builds the request and parses the reply).
