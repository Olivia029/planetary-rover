"""Local server: the viewer page plus a live chat with qwen3:4b (Ollama)."""
import json
from collections.abc import Callable
from http.server import BaseHTTPRequestHandler, HTTPServer

import ollama

from agent import Agent
from llm import OllamaModel
from model import Decision
from viewer import build_data, page

HOST = "127.0.0.1"
PORT = 8000
MODEL = "qwen3:4b"
MAX_REQUEST = 500  # characters of a chat request

type ModelFactory = Callable[[], Callable[[list[dict]], Decision]]


def path_of(route: dict) -> list[list[int]]:
    return [route["origin"]] + [move["next"] for move in route["moves"]]


def find_route(trace: list[dict], routes: list[dict]) -> dict | None:
    """The precomputed route whose path is the last run_policy path."""
    for call in reversed(trace):
        if call["tool"] != "run_policy":
            continue
        try:
            path = json.loads(call["result"])["path"]
        except (ValueError, KeyError, TypeError):  # an ERROR result
            return None
        return next((r for r in routes if path_of(r) == path), None)
    return None


def status() -> dict:
    running = installed = False
    try:
        names = [item.model for item in ollama.list().models]
        running = True
        installed = MODEL in names
    except Exception:  # Ollama closed or unexpected answer: false
        pass
    return {"live": True, "model": MODEL, "ollama": running,
            "installed": installed}


def chat(body: bytes, model_factory: ModelFactory,
         routes: list[dict]) -> dict:
    request = json.loads(body or b"{}").get("request")
    if not isinstance(request, str) or not request.strip():
        raise ValueError("the request is empty")
    if len(request) > MAX_REQUEST:
        raise ValueError(f"the request is longer than {MAX_REQUEST} "
                         f"characters")
    agent = Agent(model_factory())  # a new agent for every request
    answer = agent.run(request)
    trace = [dict(zip(("tool", "result"), line.split(" -> ", 1)))
             for line in agent.trace]
    return {"answer": answer, "trace": trace,
            "route": find_route(trace, routes)}


def make_server(model_factory: ModelFactory, port: int) -> HTTPServer:
    data = build_data()
    html = page(data).encode("utf-8")
    routes = data["routes"]

    class Handler(BaseHTTPRequestHandler):
        def send(self, code: int, body: bytes, kind: str) -> None:
            self.send_response(code)
            self.send_header("Content-Type", kind)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def send_json(self, code: int, value: dict) -> None:
            self.send(code, json.dumps(value).encode("utf-8"),
                      "application/json")

        def do_GET(self) -> None:
            if self.path == "/":
                self.send(200, html, "text/html; charset=utf-8")
            elif self.path == "/api/status":
                self.send_json(200, status())
            else:
                self.send_json(404, {"error": "not found"})

        def do_POST(self) -> None:
            if self.path != "/api/chat":
                self.send_json(404, {"error": "not found"})
                return
            try:
                length = int(self.headers.get("Content-Length", 0))
                body = self.rfile.read(length)
                self.send_json(200, chat(body, model_factory, routes))
            except Exception as error:  # the server keeps running
                self.send_json(502, {"error": str(error)})

    return HTTPServer((HOST, port), Handler)


def main() -> None:
    server = make_server(lambda: OllamaModel(MODEL), PORT)
    print(f"serving http://{HOST}:{PORT} (Ollama, model {MODEL})")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
