# Conventions: structure, tests, style and report

Part of the specification of `planetary-rover`. `CLAUDE.md` says when to
read it.

## Structure

    CLAUDE.md, worklog.md, README.md, pyproject.toml, uv.lock, .python-version
    docs/rules.md, contracts.md, conventions.md, viewer.md, statement.md
                       specification (student's files)
    docs/requirements.md   requirements and where the code meets them
    data/map.txt, data/heights.txt   terrain and heights (student's files)
    data/traces.txt        real output of src/main.py (student's file)
    src/q_table.py     QTable from class (already in the project)
    src/world.py       World: map, heights, movement rules, BFS reference
    src/rover_env.py   RoverEnv (gymnasium.Env) and its registration
    src/train.py       RoverAgent: random training, evaluation, np.save
    src/experiment.py  configurations and learning curves
    src/tools.py       list_places, run_policy, TOOLS registry
    src/model.py       Decision and ScriptedModel (the LLM double)
    src/llm.py         OllamaModel, the real LLM
    src/agent.py       Agent: system prompt, act, run loop
    src/main.py        entry point: agent demo
    src/viewer.py      data of the viewer and results/viewer.html
    src/serve.py       local server for the live chat (milestone 10)
    tests/             pytest, offline, with ScriptedModel
    q_table.npy        written by src/train.py
    results/           learning_curves.png, viewer.html

`world` imports no project module; `agent` imports `tools`.

## Tests (`tests/`, pytest, offline)

- At least six; agent tests use `ScriptedModel`; none needs Ollama or network.
- Environment: `check_env` clean; one test per rule and one of the state
  number. Tools: one test per `run_policy` error. Agent: four cases.
- A failing test means a defect in the code: never change the test to pass.

## Style

- Everything in English. Modern types, `dataclasses`, `pathlib`; modules
  find `data/` from `Path(__file__).parent.parent / "data"`.
- Executable modules end in `if __name__ == "__main__":` with the demo their
  command describes, printing exactly what it says.
- No extra dependencies, `logging` or arguments. Four-space indent, 80
  characters per line at most. No absolute paths anywhere.
- macOS on Apple Silicon; `.DS_Store` is git-ignored.

## How to report

- Files written and the full output of each command, as printed.
- If the criterion is missed: file, line, cause and proposed diff.
- At the end, the exact lines the student must review.
