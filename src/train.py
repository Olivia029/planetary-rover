"""RoverAgent: Q-learning with random actions, evaluation and saving."""
from pathlib import Path

import gymnasium as gym
import numpy as np

import rover_env  # noqa: F401  (registers RoverGrid-v0)
from q_table import QTable
from world import MAX_STEPS

ROOT = Path(__file__).parent.parent


class RoverAgent:
    def __init__(self, seed: int = 0, alpha: float = 0.5,
                 gamma: float = 0.9) -> None:
        self.env = gym.make("RoverGrid-v0")
        self.env.reset(seed=seed)
        self.env.action_space.seed(seed)
        n_states = self.env.observation_space.n
        self.table = QTable(n_states, 4, alpha=alpha, gamma=gamma)

    def train(self, episodes: int) -> None:
        for _ in range(episodes):
            s, _ = self.env.reset()
            done = False
            while not done:
                a = self.env.action_space.sample()  # random action
                s2, r, terminated, truncated, _ = self.env.step(a)
                self.table.update(s, a, r, s2, terminated)
                s = s2
                done = terminated or truncated

    def shortest_rate(self) -> float:
        world = self.env.unwrapped.world
        good = total = 0
        for letter, goal in world.places.items():
            for start in world.free_cells():
                if start == goal:
                    continue
                total += 1
                options = {"start": start, "destination": letter}
                s, _ = self.env.reset(options=options)
                steps, terminated = 0, False
                while not terminated and steps < MAX_STEPS:
                    a = self.table.best_action(s)
                    s, _, terminated, _, _ = self.env.step(a)
                    steps += 1
                reached = self.env.unwrapped.cell == goal
                if reached and steps == world.shortest_steps(start, goal):
                    good += 1
        return 100 * good / total

    def save(self, filename: str | Path) -> None:
        np.save(filename, self.table.q)


if __name__ == "__main__":
    agent = RoverAgent()
    agent.train(1500)
    print("random training: 1500 episodes")
    print(f"shortest routes: {agent.shortest_rate():.1f} %")
    agent.save(ROOT / "q_table.npy")
    print(f"saved q_table.npy: {agent.table.q.shape}")
