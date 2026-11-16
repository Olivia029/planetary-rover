"""Decision and ScriptedModel, the offline double of the LLM."""
from dataclasses import dataclass, field


@dataclass
class Decision:
    kind: str  # "tool" or "answer"
    tool: str = ""
    args: dict = field(default_factory=dict)
    text: str = ""


@dataclass
class ScriptedModel:
    script: list[Decision]
    calls: int = 0

    def __call__(self, context: list[dict]) -> Decision:
        index = min(self.calls, len(self.script) - 1)  # repeat the last one
        self.calls += 1
        return self.script[index]


if __name__ == "__main__":
    model = ScriptedModel([Decision("tool", "list_places"),
                           Decision("answer", text="done")])
    for _ in range(3):
        print(model([]))
    print("calls:", model.calls)
