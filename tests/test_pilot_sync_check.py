"""The hook of .claude/settings.json, run as Claude Code runs it, against a stand-in for
pilot-sync's local check."""

import http.server
import json
import os
import socket
import subprocess
import threading
import time
import unittest
import urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def hook_command() -> dict:
    settings = json.loads((ROOT / ".claude" / "settings.json").read_text())
    (entry,) = settings["hooks"]["PostToolUse"]
    (hook,) = entry["hooks"]
    return {"matcher": entry["matcher"], **hook}


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


class HookTest(unittest.TestCase):
    def setUp(self) -> None:
        self.sidecar = StandIn()
        threading.Thread(target=self.sidecar.serve_forever, daemon=True).start()
        self.port = self.sidecar.server_address[1]

    def tearDown(self) -> None:
        self.sidecar.released.set()
        self.sidecar.shutdown()
        self.sidecar.server_close()

    def run_hook(self, tool: str, file_path: str) -> tuple[subprocess.CompletedProcess, float]:
        event = {
            "hook_event_name": "PostToolUse",
            "tool_name": tool,
            "tool_input": {"file_path": file_path},
            "tool_response": {"filePath": file_path, "success": True},
        }
        environment = {**os.environ, "CLAUDE_PROJECT_DIR": str(ROOT)}
        environment.pop("PILOT_SYNC_LOCAL_PORT", None)
        if self.port is not None:
            environment["PILOT_SYNC_LOCAL_PORT"] = str(self.port)
        started = time.monotonic()
        completed = subprocess.run(
            hook_command()["command"],
            check=False,
            shell=True,
            cwd=ROOT,
            env=environment,
            input=json.dumps(event),
            capture_output=True,
            text=True,
            timeout=10,
        )
        return completed, time.monotonic() - started

    def assert_silent(self, completed: subprocess.CompletedProcess) -> None:
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(completed.stdout, "")
        self.assertEqual(completed.stderr, "")

    def test_settings_run_the_hook_after_every_edit_and_write_within_5_seconds(self) -> None:
        hook = hook_command()
        self.assertEqual(set(hook["matcher"].split("|")), {"Edit", "Write"})
        self.assertEqual(hook["type"], "command")
        self.assertEqual(hook["timeout"], 5)

    def test_a_path_outside_the_tree_is_not_asked_about(self) -> None:
        self.sidecar.body = "never printed\n"
        for path in (
            "/work/PilotProjects/CLAUDE.md",
            "/work/ProjectsOld/recipes/plan.md",
            "/work/Projects",
            "/tmp/notes.md",
        ):
            with self.subTest(path=path):
                completed, _ = self.run_hook("Write", path)
                self.assert_silent(completed)
        self.assertEqual(self.sidecar.asked, [])

    def test_an_empty_answer_prints_nothing(self) -> None:
        path = "/work/Projects/recipe-box/plan & notes #2.md"
        completed, _ = self.run_hook("Edit", path)
        self.assert_silent(completed)
        self.assertEqual(self.sidecar.asked, [check_of(path)])

    def test_an_answer_with_text_reaches_the_agent(self) -> None:
        self.sidecar.body = (
            "recipe-box/plan.md:12: no such task: T9\n"
            "Deferrals without a home (no plan note names these blocks):\n"
            "- B3 in recipe-box/design.md (Café menu), to: plan\n"
        )
        for tool in ("Edit", "Write"):
            with self.subTest(tool=tool):
                completed, _ = self.run_hook(tool, "/work/Projects/recipe-box/plan.md")
                self.assertEqual(completed.returncode, 0, completed.stderr)
                self.assertEqual(
                    json.loads(completed.stdout),
                    {
                        "hookSpecificOutput": {
                            "hookEventName": "PostToolUse",
                            "additionalContext": self.sidecar.body,
                        }
                    },
                )
        self.assertEqual(self.sidecar.asked, [check_of("/work/Projects/recipe-box/plan.md")] * 2)

    def test_an_error_answer_prints_nothing(self) -> None:
        for status in (400, 404, 500):
            with self.subTest(status=status):
                self.sidecar.status = status
                self.sidecar.body = f"answered {status}\n"
                completed, _ = self.run_hook("Write", "/work/Projects/draft-7/brief.md")
                self.assert_silent(completed)

    def test_with_no_port_set_the_hook_asks_3510_the_port_the_catalog_gives_the_sidecar(
        self,
    ) -> None:
        try:
            default = StandIn(3510)
        except OSError as error:
            self.skipTest(f"127.0.0.1:3510 is taken here, as pilot-sync takes it in the store: {error}")
        threading.Thread(target=default.serve_forever, daemon=True).start()
        self.addCleanup(default.server_close)
        self.addCleanup(default.shutdown)
        default.body = "recipe-box/plan.md:12: no such task: T9\n"
        self.port = None
        completed, _ = self.run_hook("Write", "/work/Projects/recipe-box/plan.md")
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(
            json.loads(completed.stdout)["hookSpecificOutput"]["additionalContext"], default.body
        )
        self.assertEqual(default.asked, [check_of("/work/Projects/recipe-box/plan.md")])

    def test_a_sidecar_down_prints_nothing(self) -> None:
        self.port = free_port()
        completed, elapsed = self.run_hook("Write", "/work/Projects/recipe-box/plan.md")
        self.assert_silent(completed)
        self.assertLess(elapsed, 1)

    def test_a_sidecar_past_the_3_second_cap_prints_nothing_before_the_hook_timeout(
        self,
    ) -> None:
        self.sidecar.hold = True
        completed, elapsed = self.run_hook("Edit", "/work/Projects/recipe-box/plan.md")
        self.assert_silent(completed)
        self.assertEqual(self.sidecar.asked, [check_of("/work/Projects/recipe-box/plan.md")])
        self.assertGreaterEqual(elapsed, 3)
        self.assertLess(elapsed, 4)


if __name__ == "__main__":
    unittest.main()
