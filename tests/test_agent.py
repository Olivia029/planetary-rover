"""Tests of the Agent with ScriptedModel: offline, no Ollama."""
from agent import Agent
from model import Decision, ScriptedModel
from tools import TOOLS

PLACES = Decision("tool", "list_places")
ROUTE = Decision("tool", "run_policy",
                 {"row": 0, "col": 0, "destination": "M"})


def make_agent(script: list[Decision], max_steps: int = 6) -> Agent:
    return Agent(ScriptedModel(script), max_steps)


def tool_names(agent: Agent) -> list[str]:
    return [line.split(" -> ")[0] for line in agent.trace]


def test_valid_route():
    agent = make_agent([PLACES, ROUTE, Decision("answer", text="9 steps")])
    assert agent.run("From the base to the rock sample?") == "9 steps"
    assert tool_names(agent) == ["list_places", "run_policy"]
    assert agent.trace[1].startswith(
        'run_policy -> {"reached": true, "steps": 9, "return": 12.0')
    assert agent.model.calls == 3


def test_unknown_place():
    agent = make_agent(
        [PLACES, Decision("answer", text="Which place do you mean?")])
    answer = agent.run("Take the rover to the cafeteria.")
    assert answer == "Which place do you mean?"
    assert tool_names(agent) == ["list_places"]


def test_out_of_scope():
    agent = make_agent([Decision("answer", text="Out of scope.")])
    assert agent.run("What is the capital of France?") == "Out of scope."
    assert agent.trace == []
    assert agent.model.calls == 1


def test_failing_tool():
    agent = make_agent([
        Decision("tool", "run_policy",
                 {"row": 0, "col": 3, "destination": "B"}),
        Decision("answer", text="(0, 3) is a rock."),
    ])
    assert agent.run("From row 0, column 3 to the base?") == \
        "(0, 3) is a rock."
    assert agent.trace == ["run_policy -> ERROR: (0, 3) is a rock"]


def test_unknown_tool():
    agent = make_agent([Decision("tool", "cancel"),
                        Decision("answer", text="done")])
    agent.run("Cancel the mission.")
    assert agent.trace == ["cancel -> ERROR: unknown tool cancel"]


def test_wrong_arguments():
    agent = make_agent([Decision("tool", "run_policy", {"row": 0}),
                        Decision("answer", text="done")])
    agent.run("Route?")
    assert agent.trace[0].startswith("run_policy -> ERROR: ")


def test_step_budget():
    agent = make_agent([PLACES], max_steps=3)
    assert agent.run("Loop forever.") == "Stopped: step budget exhausted."
    assert agent.model.calls == 3
    assert len(agent.trace) == 3


def test_system_prompt():
    prompt = make_agent([PLACES]).system_prompt()
    for tool in TOOLS.values():
        assert tool.description in prompt
    for text in ["0-5", "0-8", "top-left", "out of scope"]:
        assert text in prompt


def test_context_has_assistant_and_observation():
    contexts = []

    def spy(context: list[dict]) -> Decision:
        contexts.append([dict(message) for message in context])
        return PLACES if len(contexts) == 1 else Decision("answer", text="ok")

    Agent(spy).run("Where are the places?")
    second = contexts[1]
    assert [m["role"] for m in second] == ["system", "user", "assistant",
                                          "user"]
    assert '"tool": "list_places"' in second[2]["content"]
    assert second[-1]["content"].startswith("Observation: ")


def test_trace_line(capsys):
    make_agent([PLACES, Decision("answer", text="ok")]).run("Places?")
    first = capsys.readouterr().out.splitlines()[0]
    assert first.startswith("[1] list_places -> [{")
    assert len(first) == len("[1] list_places -> ") + 52
