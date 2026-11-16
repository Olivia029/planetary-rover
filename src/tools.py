"""Tools for the agent: list_places, run_policy and the TOOLS registry."""
import json
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

import gymnasium as gym
import numpy as np

import rover_env  # noqa: F401  (registers RoverGrid-v0)
from q_table import QTable
from world import CRATER, MAX_STEPS, ROCK

ROOT = Path(__file__).parent.parent
NAMES = {"A": "antenna", "B": "base", "M": "rock sample"}

env = gym.make("RoverGrid-v0")
world = env.unwrapped.world
table = QTable(env.observation_space.n, 4)
table.q = np.load(ROOT / "q_table.npy")  # trained table, read only


def list_places() -> str:
    places = [{"letter": letter, "name": NAMES[letter], "row": r, "col": c}
              for letter, (r, c) in world.places.items()]
    return json.dumps(places)


def run_policy(row: int, col: int, destination: str) -> dict:
    start = (int(row), int(col))
    if destination not in world.places:
        letters = ", ".join(world.places)
        raise ValueError(
            f"unknown destination {destination!r} (use {letters})")
    if not world.inside(start):
        raise ValueError(
            f"{start} is outside the map (rows 0-{world.rows - 1}, "
            f"columns 0-{world.cols - 1})")
    if world.symbol(start) == ROCK:
        raise ValueError(f"{start} is a rock")
    if world.symbol(start) == CRATER:
        raise ValueError(f"{start} is a crater")
    goal = world.places[destination]
    s, _ = env.reset(options={"start": start, "destination": destination})
    path = [list(start)]
    total, steps = 0.0, 0
    done = start == goal  # already there: 0 steps
    while not done and steps < MAX_STEPS:
        s, r, terminated, truncated, _ = env.step(table.best_action(s))
        total += r
        steps += 1
        path.append(list(env.unwrapped.cell))
        done = terminated or truncated
    reached = env.unwrapped.cell == goal
    return {"reached": reached, "steps": steps, "return": total,
            "path": path}


def run_policy_json(row: int, col: int, destination: str) -> str:
    return json.dumps(run_policy(row, col, destination))


@dataclass
class Tool:
    function: Callable[..., str]
    description: str


TOOLS: dict[str, Tool] = {
    "list_places": Tool(
        list_places,
        "list_places() returns JSON with the letter, name, row and col of "
        "every named place; use it to find which places exist and where."),
    "run_policy": Tool(
        run_policy_json,
        f"run_policy(row, col, destination) returns JSON with reached, "
        f"steps, return and path of the trained route from cell (row, col) "
        f"to a place, where rows go from 0 to {world.rows - 1}, columns "
        f"from 0 to {world.cols - 1}, (0, 0) is the top-left corner and "
        f"destination is the letter of the place. "
        f"Use it for every route and every number."),
}


if __name__ == "__main__":
    print(list_places())
    result = run_policy(0, 0, "M")
    print(f"(0, 0) -> M: {result['reached']} {result['steps']} "
          f"{result['return']}")
    path = result["path"]
    print(f"path: {len(path)} cells, from {path[0]} to {path[-1]}")
    for row, col, dest in [(0, 8, "B"), (0, 0, "A"), (0, 0, "B")]:
        result = run_policy(row, col, dest)
        print(f"({row}, {col}) -> {dest}: {result['reached']} "
              f"{result['steps']} {result['return']}")
    for row, col, dest in [(0, 3, "B"), (1, 5, "B"), (6, 0, "B"),
                           (0, 1, "Z")]:
        try:
            run_policy(row, col, dest)
        except ValueError as error:
            print(f"ValueError: {error}")
    print("tools:", ", ".join(TOOLS))
    print(TOOLS["run_policy"].function(0, 1, "B"))
