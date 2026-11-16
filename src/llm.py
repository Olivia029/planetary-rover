"""OllamaModel: the real LLM (local Ollama), same contract as ScriptedModel."""
import inspect
import json
import re
from dataclasses import dataclass

import ollama

from model import Decision
from tools import TOOLS

JSON_TYPES = {int: "integer", float: "number", str: "string",
              bool: "boolean"}
OBSERVATION = "Observation: "


def tool_schemas() -> list[dict]:
    schemas = []
    for name, tool in TOOLS.items():
        params = inspect.signature(tool.function).parameters
        properties = {p: {"type": JSON_TYPES[params[p].annotation]}
                      for p in params}
        schemas.append({"type": "function", "function": {
            "name": name,
            "description": tool.description,
            "parameters": {"type": "object", "properties": properties,
                           "required": list(params)},
        }})
    return schemas


def to_messages(context: list[dict]) -> list[dict]:
    messages, last_tool = [], ""
    for message in context:
        content = message["content"]
        if message["role"] == "assistant":
            call = json.loads(content)
            last_tool = call["tool"]
            messages.append({"role": "assistant", "content": "",
                             "tool_calls": [{"function": {
                                 "name": call["tool"],
                                 "arguments": call["args"]}}]})
        elif message["role"] == "user" and content.startswith(OBSERVATION):
            messages.append({"role": "tool", "tool_name": last_tool,
                             "content": content.removeprefix(OBSERVATION)})
        else:
            messages.append(message)  # system and the request, as they are
    return messages


def clean(text: str) -> str:
    text = text.rsplit("</think>", 1)[-1]  # drop leaked reasoning
    match = re.search(r"<answer>(.*?)</answer>", text, re.DOTALL)
    if match:
        text = match.group(1)
    return text.strip()


@dataclass
class OllamaModel:
    name: str = "qwen3:4b"
    calls: int = 0

    def __call__(self, context: list[dict]) -> Decision:
        self.calls += 1
        reply = ollama.chat(model=self.name, messages=to_messages(context),
                            tools=tool_schemas(), think=False,
                            options={"temperature": 0})
        if reply.message.tool_calls:
            call = reply.message.tool_calls[0]
            return Decision("tool", call.function.name,
                            dict(call.function.arguments))
        return Decision("answer", text=clean(reply.message.content or ""))
