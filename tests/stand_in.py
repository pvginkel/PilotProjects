"""A stand-in for pilot-sync's local endpoint on 127.0.0.1, `POST /lock` and
`POST /release`, which the store's hooks call."""

import http.server
import json
import socket
import threading


class StandIn(http.server.ThreadingHTTPServer):
    """The local endpoint: answers each POST with the pair `answers` holds for
    its route, 200 and nothing when it holds none, after `released` is set when
    `hold` is; `asked` has each call's route and JSON body, in order."""

    def __init__(self, port: int = 0) -> None:
        super().__init__(("127.0.0.1", port), Handler)
        self.answers: dict[str, tuple[int, str]] = {}
        self.hold = False
        self.released = threading.Event()
        self.asked: list[tuple[str, dict]] = []


class Handler(http.server.BaseHTTPRequestHandler):
    server: StandIn

    def do_POST(self) -> None:
        body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        self.server.asked.append((self.path, body))
        if self.server.hold:
            self.server.released.wait(10)
            return
        status, text = self.server.answers.get(self.path, (200, ""))
        answer = text.encode()
        self.send_response(status)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(answer)))
        self.end_headers()
        self.wfile.write(answer)

    def log_message(self, format: str, *args: object) -> None:
        pass


def free_port() -> int:
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0))
        return probe.getsockname()[1]
