"""A stand-in for pilot-sync's local check, `GET /check?path=` on 127.0.0.1, which the
tests of the hook and of pilot.py share."""

import http.server
import socket
import threading
import urllib.parse


class StandIn(http.server.ThreadingHTTPServer):
    """The local check: answers each `GET /check` with `status` and `body`, after
    `released` is set when `hold` is."""

    def __init__(self, port: int = 0) -> None:
        super().__init__(("127.0.0.1", port), Handler)
        self.status = 200
        self.body = ""
        self.hold = False
        self.released = threading.Event()
        self.asked: list[tuple[str, dict]] = []


class Handler(http.server.BaseHTTPRequestHandler):
    server: StandIn

    def do_GET(self) -> None:
        url = urllib.parse.urlsplit(self.path)
        self.server.asked.append((url.path, urllib.parse.parse_qs(url.query)))
        if self.server.hold:
            self.server.released.wait(10)
            return
        body = self.server.body.encode()
        self.send_response(self.server.status)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args: object) -> None:
        pass


def check_of(path: str) -> tuple[str, dict]:
    return "/check", {"path": [path]}


def free_port() -> int:
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0))
        return probe.getsockname()[1]
