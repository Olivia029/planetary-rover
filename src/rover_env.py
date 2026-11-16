"""RoverEnv: Gymnasium environment of the rover on the height grid."""
from pathlib import Path

import gymnasium as gym
from gymnasium import spaces

from world import MAX_STEPS, Cell, World

DATA = Path(__file__).parent.parent / "data"
ENV_ID = "RoverGrid-v0"

STEP_REWARD = -1.0  # moved or blocked
GOAL_REWARD = 20.0  # entering the destination cell
HAZARD_REWARD = -50.0  # crater or fall


class RoverEnv(gym.Env):
    metadata = {"render_modes": []}

    def __init__(self) -> None:
        self.world = World.load(DATA / "map.txt", DATA / "heights.txt")
        self.letters = list(self.world.places)  # A 0, B 1, M 2
        n_cells = self.world.rows * self.world.cols
        self.observation_space = spaces.Discrete(len(self.letters) * n_cells)
        self.action_space = spaces.Discrete(4)
        self.cell: Cell = (0, 0)
        self.destination = self.letters[0]

    def state(self) -> int:
        dest_index = self.letters.index(self.destination)
        row, col = self.cell
        cols = self.world.cols
        return int(dest_index * (self.world.rows * cols) + row * cols + col)

    def reset(self, seed: int | None = None,
              options: dict | None = None) -> tuple[int, dict]:
        super().reset(seed=seed)
        options = options or {}
        destination = options.get("destination")
        if destination is None:
            index = self.np_random.integers(len(self.letters))
            destination = self.letters[int(index)]
        elif destination not in self.world.places:
            raise ValueError(f"unknown destination {destination!r}")
        start = options.get("start")
        if start is None:
            goal = self.world.places[destination]
            cells = [c for c in self.world.free_cells() if c != goal]
            start = cells[int(self.np_random.integers(len(cells)))]
        else:
            start = (int(start[0]), int(start[1]))
            if not self.world.inside(start):
                raise ValueError(f"start {start} is outside the map")
            if start not in self.world.free_cells():
                raise ValueError(f"start {start} is on a rock or a crater")
        self.destination = destination
        self.cell = start
        return self.state(), {}

    def step(self, action: int) -> tuple[int, float, bool, bool, dict]:
        self.cell, outcome = self.world.move(self.cell, int(action))
        if outcome == "hazard":
            return self.state(), HAZARD_REWARD, True, False, {}
        if self.cell == self.world.places[self.destination]:
            return self.state(), GOAL_REWARD, True, False, {}
        return self.state(), STEP_REWARD, False, False, {}


if ENV_ID not in gym.registry:
    gym.register(id=ENV_ID, entry_point=RoverEnv,
                 max_episode_steps=MAX_STEPS)


if __name__ == "__main__":
    from gymnasium.utils.env_checker import check_env

    env = gym.make(ENV_ID)
    print("spaces:", env.observation_space, env.action_space)
    cases = [("rock", (0, 2), "M", 1), ("steep climb", (1, 3), "M", 1),
             ("fall", (2, 5), "M", 2), ("crater", (1, 4), "M", 1),
             ("destination", (0, 1), "B", 3)]
    for label, start, destination, action in cases:
        env.reset(options={"start": start, "destination": destination})
        print(f"{label}: {env.step(action)}")
    print("reset:", env.reset(options={"start": (0, 1), "destination": "M"}))
    env.reset(options={"start": (0, 0), "destination": "M"})
    n, result = 0, (0, 0.0, False, False, {})
    while not result[3]:
        n += 1
        result = env.step(0)
    print(f"truncated at step {n}: {result}")
    check_env(gym.make(ENV_ID).unwrapped)
    print("check_env: ok")
