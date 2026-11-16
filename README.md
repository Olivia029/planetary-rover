# planetary-rover

A planetary exploration rover moves on a grid with heights. A Q table, trained
with random actions in a custom Gymnasium environment, decides how to go from
any cell to a named place. An LLM agent (local Ollama) understands a request,
calls the table as a tool and explains the route with the tool's numbers.

## Requirements
- [uv](https://docs.astral.sh/uv/); it installs the Python of
  `.python-version` (3.14).
- For the agent and the live chat only: the Ollama app running, with the
  model downloaded by `ollama pull qwen3:4b`. No token and no `.env` needed.

## Setup and tests

    uv sync
    uv run pytest

The tests are offline (no Ollama, no network). Expected result: `48 passed`.

## Run
    uv run python src/world.py       # grid, places, BFS distances, moves
    uv run python src/rover_env.py   # spaces, one step per rule, check_env
    uv run python src/train.py       # prints the rate, rewrites q_table.npy
    uv run python src/experiment.py  # writes results/learning_curves.png
    uv run python src/tools.py       # list_places, routes and tool errors
    uv run python src/model.py       # ScriptedModel demo, prints 3 decisions
    uv run python src/main.py        # agent answers four requests (real LLM)
    uv run python src/viewer.py      # writes results/viewer.html (no model)
    uv run python src/serve.py       # live chat at http://127.0.0.1:8000

- `train.py` trains 1500 episodes with random actions; the seed is fixed, so
  `q_table.npy` is always the same.
- `main.py` needs Ollama and takes a few minutes; the model's answers vary.

## Viewer

- **Saved results:** open `results/viewer.html` in a browser (`viewer.py`
  rebuilds it); the badge says `Saved results - no model`.
- **Live chat:** run `serve.py`, wait for `serving http://127.0.0.1:8000` and
  open that address. With Ollama and `qwen3:4b` the badge says
  `Live - Ollama - qwen3:4b`; otherwise the Agent tab says what is missing.
  Stop it with Ctrl+C; restart it after rebuilding the page.
- **Tabs:** Map (terrain, rocks, craters, heights), Route (Run, Pause, Step,
  Back, Reset, with each step's state, Q values and reward), Policy, Learning
  and Agent (saved traces or the chat, answers with bold and code).
- **Requirements:** each tab lists the requirements it shows (R1-R5) with
  their files; R6 and R7 are listed in the left panel as not shown. The text
  comes from `docs/requirements.md`: run `viewer.py` after editing it.

## Project layout

    docs/              statement, specification and requirements.md
    data/              map.txt, heights.txt, traces.txt (main.py output)
    src/world.py       map, heights, movement rules, BFS reference
    src/rover_env.py   RoverEnv (Gymnasium), registered as RoverGrid-v0
    src/q_table.py     QTable
    src/train.py       RoverAgent: random training, evaluation, save
    src/experiment.py  configurations and learning curves
    src/tools.py       list_places, run_policy, TOOLS registry
    src/model.py       Decision and ScriptedModel (the LLM double)
    src/llm.py         OllamaModel (native Ollama tool calling)
    src/agent.py       Agent: system prompt, act, run loop
    src/main.py        agent demo
    src/viewer.py      viewer data and page
    src/serve.py       local server for the live chat
    tests/             pytest, offline
    q_table.npy        trained Q table (only read by the tools and the agent)
    results/           learning_curves.png, viewer.html

## Map and rules
- Map 6 x 9: `.` free, `#` rock, `~` crater, `A` antenna, `B` base, `M` sample.
- Heights 0-9 per cell; the rover climbs at most 1 and descends at most 2.
- A rock, the edge or a climb over 1 blocks the move (the rover stays).
- Rewards: -1 move or block; +20 destination; -50 crater or drop over 2 (end).
- State = destination (A 0, B 1, M 2) x 54 cells + cell: 162 states.
- An episode or a route is cut at 100 steps.
