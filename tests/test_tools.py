"""Tests of the tools: list_places, run_policy and the registry."""
import json

import numpy as np
import pytest

import tools
from tools import TOOLS, list_places, run_policy


def test_list_places_in_letter_order():
    places = json.loads(list_places())
    assert places == [
        {"letter": "A", "name": "antenna", "row": 0, "col": 8},
        {"letter": "B", "name": "base", "row": 0, "col": 0},
        {"letter": "M", "name": "rock sample", "row": 5, "col": 4},
    ]


def test_route_to_rock_sample():
    result = run_policy(0, 0, "M")
    assert result["reached"] is True
    assert result["steps"] == 9
    assert result["return"] == 12.0
    assert result["path"][0] == [0, 0]
    assert result["path"][-1] == [5, 4]
    assert len(result["path"]) == result["steps"] + 1


def test_start_on_destination():
    result = run_policy(0, 0, "B")
    assert result == {"reached": True, "steps": 0, "return": 0.0,
                      "path": [[0, 0]]}


@pytest.mark.parametrize(
    ("row", "col", "destination", "message"),
    [
        (0, 3, "B", r"^\(0, 3\) is a rock$"),
        (1, 5, "B", r"^\(1, 5\) is a crater$"),
        (6, 0, "B",
         r"^\(6, 0\) is outside the map \(rows 0-5, columns 0-8\)$"),
        (0, 1, "Z", r"^unknown destination 'Z' \(use A, B, M\)$"),
    ],
    ids=["rock", "crater", "outside", "unknown_destination"],
)
def test_run_policy_errors(row, col, destination, message):
    with pytest.raises(ValueError, match=message):
        run_policy(row, col, destination)


def test_every_route_is_shortest():
    world = tools.world
    for letter, goal in world.places.items():
        for start in world.free_cells():
            if start == goal:
                continue
            result = run_policy(start[0], start[1], letter)
            assert result["reached"], (start, letter)
            assert result["steps"] == world.shortest_steps(start, goal)


def test_run_policy_does_not_change_table():
    before = tools.table.q.copy()
    run_policy(0, 0, "M")
    run_policy(0, 8, "B")
    assert np.array_equal(tools.table.q, before)


def test_registry():
    assert list(TOOLS) == ["list_places", "run_policy"]
    assert all(tool.description for tool in TOOLS.values())
    text = TOOLS["run_policy"].function(0, 1, "B")
    assert isinstance(text, str)
    assert json.loads(text) == {"reached": True, "steps": 1,
                                "return": 20.0, "path": [[0, 1], [0, 0]]}


def test_route_cut_at_100_steps(monkeypatch):
    monkeypatch.setattr(tools.table, "best_action", lambda s: 0)  # up
    result = tools.run_policy(0, 1, "M")
    assert result["reached"] is False
    assert result["steps"] == 100
    assert result["return"] == -100.0
    assert len(result["path"]) == 101
