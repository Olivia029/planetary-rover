"""Tests of RoverEnv: checker, movement rules, truncation, state number."""
import warnings

import gymnasium as gym
import pytest
from gymnasium.utils.env_checker import check_env

import rover_env  # noqa: F401  (registers RoverGrid-v0)


def make_env() -> gym.Env:
    return gym.make("RoverGrid-v0")


def test_check_env_clean():
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        check_env(make_env().unwrapped)


@pytest.mark.parametrize(
    ("start", "destination", "action", "expected"),
    [
        ((0, 2), "M", 1, (110, -1.0, False, False, {})),
        ((1, 3), "M", 1, (120, -1.0, False, False, {})),
        ((2, 5), "M", 2, (140, -50.0, True, False, {})),
        ((1, 4), "M", 1, (122, -50.0, True, False, {})),
        ((0, 1), "B", 3, (54, 20.0, True, False, {})),
    ],
    ids=["rock", "steep_climb", "fall", "crater", "destination"],
)
def test_step_rule(start, destination, action, expected):
    env = make_env()
    env.reset(options={"start": start, "destination": destination})
    assert env.step(action) == expected


def test_truncation_at_100():
    env = make_env()
    env.reset(options={"start": (0, 0), "destination": "M"})
    for n in range(1, 101):
        result = env.step(0)
        assert result[3] == (n == 100)
    assert result == (108, -1.0, False, True, {})


def test_state_number():
    env = make_env()
    state, info = env.reset(options={"start": (0, 1), "destination": "M"})
    assert state == 2 * (6 * 9) + 0 * 9 + 1 == 109
    assert info == {}


@pytest.mark.parametrize(
    ("start", "destination"),
    [((0, 3), "M"), ((1, 5), "M"), ((6, 0), "M"), ((0, 1), "Z")],
    ids=["rock", "crater", "outside", "unknown_destination"],
)
def test_reset_invalid(start, destination):
    env = make_env()
    with pytest.raises(ValueError):
        env.reset(options={"start": start, "destination": destination})
