"""Entry point: the agent answers four requests with the real LLM."""
from agent import Agent
from llm import OllamaModel

REQUESTS = [
    "The rover is at the base. How does it reach the rock sample, and how "
    "many steps does it take?",
    "Take the rover from the base to the cafeteria.",
    "What is the capital of France?",
    "The rover is at row 0, column 3. How does it reach the base?",
]


def main() -> None:
    model = OllamaModel()
    for n, request in enumerate(REQUESTS, start=1):
        print(f"=== case {n} ===")
        print(f"request: {request}")
        agent = Agent(model)
        print(f"answer: {agent.run(request)}")


if __name__ == "__main__":
    main()
