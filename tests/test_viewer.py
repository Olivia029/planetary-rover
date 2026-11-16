"""Tests of the viewer: routes equal run_policy, and the written page."""
import json
import re
import threading
import urllib.error
import urllib.request
from contextlib import contextmanager

import pytest

import serve
import tools
import viewer
from model import Decision, ScriptedModel

TABS = ["Map", "Route", "Policy", "Learning", "Agent"]
DATA_TAG = '<script type="application/json" id="data">'


def test_routes_match_run_policy():
    data = viewer.build_data()
    places = data["world"]["places"]
    assert len(data["routes"]) == 126
    for route in data["routes"]:
        row, col = route["origin"]
        expected = tools.run_policy(row, col, route["destination"])
        moves = route["moves"]
        path = [route["origin"]] + [move["next"] for move in moves]
        assert route["steps"] == expected["steps"] == len(moves)
        assert route["return"] == expected["return"]
        assert path == expected["path"]
        if route["reached"]:
            goal = places[route["destination"]]["cell"]
            assert moves[-1]["next"] == goal


def test_write_html(tmp_path):
    path = tmp_path / "viewer.html"
    viewer.write_html(path)
    assert list(tmp_path.iterdir()) == [path]
    html = path.read_text(encoding="utf-8")
    for tab in TABS:
        assert f">{tab}</button>" in html
    assert not re.search(r"(src|href)=.?https?:", html)
    raw = html.split(DATA_TAG, 1)[1].split("</script>", 1)[0]
    traces = json.loads(raw)["traces"]
    assert len(traces) == 4
    tools_called = [call["tool"] for call in traces[0]["trace"]]
    assert tools_called == ["list_places", "run_policy"]


@contextmanager
def running(factory):
    """A server on a free port (port 0), stopped at the end."""
    server = serve.make_server(factory, 0)
    thread = threading.Thread(target=server.serve_forever)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_address[1]}"
    finally:
        server.shutdown()
        server.server_close()
        thread.join()


def post_chat(base: str, text: str) -> dict:
    body = json.dumps({"request": text}).encode("utf-8")
    request = urllib.request.Request(
        base + "/api/chat", data=body,
        headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(request) as response:
        return json.loads(response.read())


def get_status(base: str) -> dict:
    with urllib.request.urlopen(base + "/api/status") as response:
        return json.loads(response.read())


def no_ollama():
    raise ConnectionError("Ollama is not used in tests")


def test_live_chat_with_scripted_model(monkeypatch):
    monkeypatch.setattr(serve.ollama, "list", no_ollama)
    route = Decision("tool", "run_policy",
                     {"row": 0, "col": 0, "destination": "M"})

    def factory():
        return ScriptedModel([route, Decision("answer", text="9 steps")])

    with running(factory) as base:
        reply = post_chat(base, "From the base to the rock sample?")
        status = get_status(base)
    assert reply["answer"] == "9 steps"
    assert [call["tool"] for call in reply["trace"]] == ["run_policy"]
    assert reply["route"]["steps"] == 9
    assert status["live"] is True
    assert status["model"] == "qwen3:4b"


def test_live_chat_error_keeps_server(monkeypatch):
    monkeypatch.setattr(serve.ollama, "list", no_ollama)

    def factory():
        raise RuntimeError("model unavailable")

    with running(factory) as base:
        with pytest.raises(urllib.error.HTTPError) as caught:
            post_chat(base, "Route?")
        status = get_status(base)
    assert caught.value.code == 502
    assert "error" in json.loads(caught.value.read())
    assert status["live"] is True
