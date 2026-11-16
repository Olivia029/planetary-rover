"""Tests of RoverAgent: training, evaluation and the saved table."""
from pathlib import Path

import numpy as np

from train import RoverAgent

ROOT = Path(__file__).parent.parent


def test_same_seed_same_table():
    first, second = RoverAgent(seed=0), RoverAgent(seed=0)
    first.train(30)
    second.train(30)
    assert np.array_equal(first.table.q, second.table.q)
    assert np.any(first.table.q != 0)


def test_saved_table_shape():
    agent = RoverAgent()
    q = np.load(ROOT / "q_table.npy")
    assert q.shape == (agent.env.observation_space.n, 4)


def test_saved_table_rate():
    agent = RoverAgent()
    agent.table.q = np.load(ROOT / "q_table.npy")
    assert agent.shortest_rate() >= 95.0


def test_save_round_trip(tmp_path):
    agent = RoverAgent()
    agent.train(10)
    filename = tmp_path / "q.npy"
    agent.save(filename)
    assert np.array_equal(np.load(filename), agent.table.q)


def test_training_from_scratch():
    agent = RoverAgent()
    agent.train(1500)
    assert agent.shortest_rate() >= 95.0


def test_update_receives_terminated():
    agent = RoverAgent()
    calls = []
    update = agent.table.update

    def spy(s, a, r, s2, done):
        calls.append((r, done))
        update(s, a, r, s2, done)

    agent.table.update = spy
    agent.train(20)
    assert calls
    assert all(done == (r != -1.0) for r, done in calls)
