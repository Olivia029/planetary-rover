"""Learning curves: % of shortest routes after each block of episodes."""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # draw to a file, no window
import matplotlib.pyplot as plt  # noqa: E402

from train import RoverAgent  # noqa: E402

CONFIGS = [(0.5, 0.9), (0.1, 0.9), (0.5, 0.5)]  # (alpha, gamma)
BLOCKS = 10
BLOCK_SIZE = 100
RESULTS = Path(__file__).parent.parent / "results"


def curve(alpha: float, gamma: float) -> list[float]:
    agent = RoverAgent(seed=0, alpha=alpha, gamma=gamma)
    rates = []
    for _ in range(BLOCKS):
        agent.train(BLOCK_SIZE)  # one more block of random episodes
        rates.append(agent.shortest_rate())  # measured after the block
    return rates


if __name__ == "__main__":
    episodes = [BLOCK_SIZE * (i + 1) for i in range(BLOCKS)]
    print("episodes:" + "".join(f" {e:5d}" for e in episodes))
    fig, ax = plt.subplots()
    for alpha, gamma in CONFIGS:
        label = f"alpha={alpha} gamma={gamma}"
        rates = curve(alpha, gamma)
        print(f"{label}:" + "".join(f" {r:5.1f}" for r in rates))
        ax.plot(episodes, rates, marker="o", label=label)
    ax.axhline(95, color="gray", linestyle="--", label="95 % target")
    ax.set_xlabel("training episodes")
    ax.set_ylabel("% of shortest routes")
    ax.set_ylim(0, 105)
    ax.legend()
    ax.grid(True)
    RESULTS.mkdir(exist_ok=True)
    fig.savefig(RESULTS / "learning_curves.png")
    print("saved results/learning_curves.png")
