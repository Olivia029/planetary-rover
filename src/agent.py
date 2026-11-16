"""Agent: system prompt, tool execution and the decision loop."""
import json
from collections.abc import Callable
from dataclasses import dataclass, field

import tools
from model import Decision


@dataclass
class Agent:
    model: Callable[[list[dict]], Decision]
    max_steps: int = 6
    trace: list[str] = field(default_factory=list)

    def system_prompt(self) -> str:
        world = tools.world
        lines = [
            "You are the mission assistant of a planetary exploration rover.",
            f"The map is a grid of {world.rows} rows (0-{world.rows - 1}) "
            f"and {world.cols} columns (0-{world.cols - 1}); "
            f"(0, 0) is the top-left corner.",
            "Tools:",
        ]
        lines += [f"- {tool.description}" for tool in tools.TOOLS.values()]
        lines += [
            "Rules:",
            "1. Use list_places to know the places and their cells.",
            "2. Use run_policy for every route and every number; copy its "
            "steps, return and path exactly and never compute them "
            "yourself.",
            "3. If the request names a place that list_places does not "
            "give, ask which place is meant and do not call run_policy.",
            "4. If the request is not about rover routes, say it is out of "
            "scope and do not call any tool.",
            "5. Never repeat a tool call with the same arguments: use its "
            "Observation for the next step, then answer.",
        ]
        return "\n".join(lines)

    def act(self, name: str, args: dict) -> str:
        if name not in tools.TOOLS:
            return f"ERROR: unknown tool {name}"
        try:
            return tools.TOOLS[name].function(**args)
        except Exception as error:  # a tool error is an observation
            return f"ERROR: {error}"

    def run(self, request: str) -> str:
        context = [{"role": "system", "content": self.system_prompt()},
                   {"role": "user", "content": request}]
        for n in range(1, self.max_steps + 1):
            decision = self.model(context)
            if decision.kind == "answer":
                return decision.text
            result = self.act(decision.tool, decision.args)
            self.trace.append(f"{decision.tool} -> {result}")
            print(f"[{n}] {decision.tool} -> {result[:52]}")
            call = {"kind": "tool", "tool": decision.tool,
                    "args": decision.args}
            context.append({"role": "assistant",
                            "content": json.dumps(call)})
            context.append({"role": "user",
                            "content": f"Observation: {result}"})
        return "Stopped: step budget exhausted."
