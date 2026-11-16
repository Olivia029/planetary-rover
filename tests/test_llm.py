"""Tests of the Ollama wrapper with a fake ollama.chat: offline."""
import json
from types import SimpleNamespace

import llm
from model import Decision


def reply(content: str, tool_calls: list | None) -> SimpleNamespace:
    message = SimpleNamespace(content=content, tool_calls=tool_calls)
    return SimpleNamespace(message=message)


def test_tool_schemas():
    schemas = {s["function"]["name"]: s["function"]
               for s in llm.tool_schemas()}
    assert list(schemas) == ["list_places", "run_policy"]
    assert schemas["list_places"]["parameters"]["properties"] == {}
    params = schemas["run_policy"]["parameters"]
    assert params["properties"] == {"row": {"type": "integer"},
                                    "col": {"type": "integer"},
                                    "destination": {"type": "string"}}
    assert params["required"] == ["row", "col", "destination"]


def test_to_messages():
    call = {"kind": "tool", "tool": "list_places", "args": {}}
    context = [{"role": "system", "content": "S"},
               {"role": "user", "content": "R"},
               {"role": "assistant", "content": json.dumps(call)},
               {"role": "user", "content": "Observation: [1, 2]"}]
    messages = llm.to_messages(context)
    assert [m["role"] for m in messages] == ["system", "user", "assistant",
                                            "tool"]
    assert messages[2]["tool_calls"] == [
        {"function": {"name": "list_places", "arguments": {}}}]
    assert messages[3] == {"role": "tool", "tool_name": "list_places",
                           "content": "[1, 2]"}


def test_clean():
    assert llm.clean("I think...\n</think>\nNine steps.") == "Nine steps."
    assert llm.clean("x</think> <answer> Out. </answer> y") == "Out."
    assert llm.clean("Plain text.") == "Plain text."


def test_tool_call(monkeypatch):
    seen = {}
    args = {"row": 0, "col": 0, "destination": "M"}

    def fake_chat(**kwargs):
        seen.update(kwargs)
        call = SimpleNamespace(function=SimpleNamespace(
            name="run_policy", arguments=args))
        return reply("", [call])

    monkeypatch.setattr(llm.ollama, "chat", fake_chat)
    model = llm.OllamaModel()
    context = [{"role": "system", "content": "S"},
               {"role": "user", "content": "R"}]
    assert model(context) == Decision("tool", "run_policy", args)
    assert model.calls == 1
    assert seen["model"] == "qwen3:4b"
    assert seen["think"] is False
    assert seen["options"] == {"temperature": 0}


def test_answer_is_cleaned(monkeypatch):
    text = "reasoning\n</think>\n\n<answer>\nOut of scope.\n</answer>"
    monkeypatch.setattr(llm.ollama, "chat",
                        lambda **kwargs: reply(text, None))
    model = llm.OllamaModel()
    context = [{"role": "system", "content": "S"},
               {"role": "user", "content": "R"}]
    assert model(context) == Decision("answer", text="Out of scope.")
