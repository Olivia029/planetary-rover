"""Q table for Q-learning: one row per state, one column per action."""
import numpy as np


class QTable:
    def __init__(self, n_states: int, n_actions: int,
                 alpha: float = 0.1, gamma: float = 0.9) -> None:
        self.q = np.zeros((n_states, n_actions))  # every cell starts at 0
        self.alpha = alpha  # learning rate
        self.gamma = gamma  # discount

    def best_action(self, s: int) -> int:
        return int(self.q[s].argmax())  # column with the largest value

    def update(self, s: int, a: int, r: float, s2: int, done: bool) -> None:
        future = 0.0 if done else self.q[s2].max()
        target = r + self.gamma * future
        error = target - self.q[s, a]
        self.q[s, a] = self.q[s, a] + self.alpha * error


if __name__ == "__main__":
    RIGHT = 1
    table = QTable(n_states=5, n_actions=2, alpha=0.5, gamma=0.9)
    for episode in range(1, 4):
        for s in range(4):  # cells 0..3, always RIGHT
            s2 = s + 1
            done = s2 == 4  # cell 4 is the goal
            r = 1.0 if done else 0.0
            table.update(s, RIGHT, r, s2, done)
        values = table.q[:4, RIGHT].round(4).tolist()  # RIGHT, cells 0..3
        print("episode", episode, "Q(s, RIGHT):", values)
