"""The hook of .claude/settings.json, run as Claude Code runs it, against a stand-in for
pilot-sync's local endpoint: the project's write lock taken before every writing tool call, and
given back after it with the check's report."""

import contextlib
import importlib.util
import io
import json
import os
import subprocess
import sys
import threading
import time
import unittest
from pathlib import Path
from unittest import mock

from stand_in import StandIn, free_port

ROOT = Path(__file__).resolve().parents[1]
HOOK = ROOT / ".claude" / "hooks" / "pilot-sync-lock.py"
PROJECT = "/work/Projects/recipe-box"
SESSION = "5f0c2a7e-91d4-4b3a-8e6f-2d7c9a1b4e58"
WRITING_TOOLS = {"Edit", "Write", "MultiEdit", "Bash"}
TOOL_EVENTS = ("PreToolUse", "PostToolUse", "PostToolUseFailure")
RELEASES = ("PostToolUse", "PostToolUseFailure")
REPORT = (
    "recipe-box/plan.json:12: no such task: T9\n"
    "recipe-box/notes.md: not a document of the record — files are born through `add_item`\n"
    "Deferrals without a home (no plan note names these blocks):\n"
    "- B3 in recipe-box/items/7-cafe-menu.md (Café menu), to: plan\n"
)
NOT_RUN = "not run without the project's write lock: pilot-sync"


def settings_hooks() -> dict:
    return json.loads((ROOT / ".claude" / "settings.json").read_text())["hooks"]


def hook_of(event: str) -> dict:
    (entry,) = settings_hooks()[event]
    (hook,) = entry["hooks"]
    return {"matcher": entry.get("matcher"), **hook}


def hook_module():
    spec = importlib.util.spec_from_file_location("pilot_sync_lock", HOOK)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def hook_input(event: str, tool: str = "Bash", stop_hook_active: bool = False) -> dict:
    """The hook's stdin as Claude Code writes it for the event."""
    if event == "Stop":
        return {"hook_event_name": event, "stop_hook_active": stop_hook_active}
    tool_input = (
        {"command": "cexec python uv run tools/pilot.py plan task list"}
        if tool == "Bash"
        else {"file_path": f"{PROJECT}/plan.json"}
    )
    shape = {"hook_event_name": event, "tool_name": tool, "tool_input": tool_input}
    if event == "PostToolUse":
        shape["tool_response"] = {"success": True}
    if event == "PostToolUseFailure":
        shape.update(error="Exit code 1", is_interrupt=False)
    return shape


def lock_of(pid: int) -> tuple[str, dict]:
    return "/lock", {"project": PROJECT, "session": SESSION, "pid": pid}


def release_of(pid: int) -> tuple[str, dict]:
    return "/release", {"project": PROJECT, "session": SESSION, "pid": pid}


RELEASE_ALL = ("/release", {"project": PROJECT, "session": SESSION, "all": True})


def denial(reason: str) -> dict:
    return {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
        }
    }


def context(event: str, text: str) -> dict:
    return {"hookSpecificOutput": {"hookEventName": event, "additionalContext": text}}


class HookCase(unittest.TestCase):
    def setUp(self) -> None:
        self.sidecar = StandIn()
        threading.Thread(target=self.sidecar.serve_forever, daemon=True).start()
        self.addCleanup(self.sidecar.server_close)
        self.addCleanup(self.sidecar.shutdown)
        self.addCleanup(self.sidecar.released.set)
        self.port = self.sidecar.server_address[1]

    def environment(self, **overrides: str | None) -> dict[str, str]:
        environment = {
            **os.environ,
            "CLAUDE_PROJECT_DIR": str(ROOT),
            "PILOT_PROJECT": PROJECT,
            "PILOT_SESSION": SESSION,
            "PILOT_SYNC_LOCAL_PORT": str(self.port),
            **overrides,
        }
        return {name: value for name, value in environment.items() if value is not None}

    def run_hook(
        self, shape: dict, command: str | list[str] | None = None, **environment: str | None
    ) -> subprocess.CompletedProcess:
        """The hook on the event, through a shell as settings.json's command, unless another
        command is given."""
        return subprocess.run(
            hook_of(shape["hook_event_name"])["command"] if command is None else command,
            check=False,
            shell=command is None,
            cwd=ROOT,
            env=self.environment(**environment),
            input=json.dumps(shape),
            capture_output=True,
            text=True,
            timeout=30,
        )

    def run_in_process(self, shape: dict, **caps: int) -> tuple[dict | None, float]:
        """The hook's main() here, its caps as given: its output, and how long it took."""
        module = hook_module()
        stdout = io.StringIO()
        with (
            mock.patch.dict(os.environ, self.environment()),
            mock.patch.object(sys, "stdin", io.StringIO(json.dumps(shape))),
            contextlib.redirect_stdout(stdout),
            contextlib.ExitStack() as patches,
        ):
            for name, seconds in caps.items():
                patches.enter_context(mock.patch.object(module, name, seconds))
            started = time.monotonic()
            module.main()
            elapsed = time.monotonic() - started
        return (json.loads(stdout.getvalue()) if stdout.getvalue() else None), elapsed

    def output(self, completed: subprocess.CompletedProcess) -> dict | None:
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(completed.stderr, "")
        return json.loads(completed.stdout) if completed.stdout else None


class TestTheSettings(unittest.TestCase):
    def test_the_hook_runs_around_every_writing_tool_call_and_at_the_turn_s_end(self) -> None:
        self.assertEqual(set(settings_hooks()), {*TOOL_EVENTS, "Stop"})
        command = '"$CLAUDE_PROJECT_DIR"/.claude/hooks/pilot-sync-lock.py'
        for event in TOOL_EVENTS:
            with self.subTest(event=event):
                hook = hook_of(event)
                self.assertEqual(set(hook["matcher"].split("|")), WRITING_TOOLS)
                self.assertEqual((hook["type"], hook["command"]), ("command", command))
        stop = hook_of("Stop")
        self.assertEqual(
            (stop["matcher"], stop["type"], stop["command"]), (None, "command", command)
        )

    def test_the_timeouts_sit_above_the_caps_and_the_caps_above_pilot_sync_s_bounds(self) -> None:
        module = hook_module()
        self.assertGreater(hook_of("PreToolUse")["timeout"], module.LOCK_CAP_SECONDS)
        self.assertGreater(module.LOCK_CAP_SECONDS, 60)
        for event in (*RELEASES, "Stop"):
            with self.subTest(event=event):
                self.assertGreater(hook_of(event)["timeout"], module.RELEASE_CAP_SECONDS)
        self.assertGreater(module.RELEASE_CAP_SECONDS, 5 + 5)


class TestTheLock(HookCase):
    def test_before_a_writing_call_the_session_takes_the_lock_with_its_claude_process(
        self,
    ) -> None:
        for tool in sorted(WRITING_TOOLS):
            with self.subTest(tool=tool):
                self.sidecar.asked.clear()
                self.assertIsNone(self.output(self.run_hook(hook_input("PreToolUse", tool))))
                self.assertEqual(self.sidecar.asked, [lock_of(os.getpid())])

    def test_the_claude_process_is_the_nearest_ancestor_that_is_no_shell(self) -> None:
        command = hook_of("PreToolUse")["command"]
        for how, run in (
            ("run directly", [str(HOOK)]),
            ("forked by a shell", ["sh", "-c", f"{command}; true"]),
            ("under a shell under a shell", ["sh", "-c", f"sh -c '{command}; true'; true"]),
        ):
            with self.subTest(how=how):
                self.sidecar.asked.clear()
                self.assertIsNone(self.output(self.run_hook(hook_input("PreToolUse"), run)))
                self.assertEqual(self.sidecar.asked, [lock_of(os.getpid())])

    def test_another_session_writing_denies_the_call_in_pilot_sync_s_words(self) -> None:
        self.sidecar.answers["/lock"] = (409, "another session is writing; try again\n")

        completed = self.run_hook(hook_input("PreToolUse", "Edit"))

        self.assertEqual(self.output(completed), denial("another session is writing; try again"))

    def test_a_lock_pilot_sync_refuses_denies_the_call(self) -> None:
        for status, text in (
            (400, "no running process 4242\n"),
            (500, "internal error\n"),
        ):
            with self.subTest(status=status):
                self.sidecar.answers["/lock"] = (status, text)
                completed = self.run_hook(hook_input("PreToolUse", "Write"))
                self.assertEqual(
                    self.output(completed),
                    denial(f"{NOT_RUN} answered {status}: {text.strip()}"),
                )

    def test_a_sidecar_down_denies_the_call(self) -> None:
        started = time.monotonic()
        completed = self.run_hook(hook_input("PreToolUse"), PILOT_SYNC_LOCAL_PORT=str(free_port()))

        reason = self.output(completed)["hookSpecificOutput"]["permissionDecisionReason"]
        self.assertTrue(reason.startswith(f"{NOT_RUN} did not answer: "), reason)
        self.assertLess(time.monotonic() - started, 2)

    def test_a_lock_past_the_cap_denies_the_call(self) -> None:
        self.sidecar.hold = True

        output, elapsed = self.run_in_process(hook_input("PreToolUse"), LOCK_CAP_SECONDS=1)

        self.assertEqual(output, denial(f"{NOT_RUN} did not answer: timed out"))
        self.assertGreaterEqual(elapsed, 1)
        self.assertLess(elapsed, 2)


class TestTheRelease(HookCase):
    def test_after_a_call_ran_or_failed_its_hold_goes_back_and_the_report_reaches_the_agent(
        self,
    ) -> None:
        self.sidecar.answers["/release"] = (200, REPORT)
        for event in RELEASES:
            for tool in sorted(WRITING_TOOLS):
                with self.subTest(event=event, tool=tool):
                    self.sidecar.asked.clear()
                    completed = self.run_hook(hook_input(event, tool))
                    self.assertEqual(self.output(completed), context(event, REPORT))
                    self.assertEqual(self.sidecar.asked, [release_of(os.getpid())])

    def test_an_empty_report_puts_nothing_before_the_agent(self) -> None:
        for event in RELEASES:
            with self.subTest(event=event):
                self.sidecar.asked.clear()
                self.assertIsNone(self.output(self.run_hook(hook_input(event))))
                self.assertEqual(self.sidecar.asked, [release_of(os.getpid())])

    def test_a_release_with_no_answer_or_an_error_status_is_not_yet_checked(self) -> None:
        completed = self.run_hook(hook_input("PostToolUse"), PILOT_SYNC_LOCAL_PORT=str(free_port()))
        text = self.output(completed)["hookSpecificOutput"]["additionalContext"]
        self.assertTrue(
            text.startswith("not yet checked: recipe-box/ (pilot-sync did not answer: "), text
        )

        self.sidecar.answers["/release"] = (400, 'not a project folder of the tree: "x"\n')
        completed = self.run_hook(hook_input("PostToolUseFailure"))
        self.assertEqual(
            self.output(completed),
            context(
                "PostToolUseFailure",
                "not yet checked: recipe-box/ (pilot-sync answered 400: not a project folder"
                ' of the tree: "x")\n',
            ),
        )

    def test_a_release_past_the_cap_is_not_yet_checked(self) -> None:
        self.sidecar.hold = True

        output, elapsed = self.run_in_process(hook_input("PostToolUse"), RELEASE_CAP_SECONDS=1)

        self.assertEqual(
            output,
            context(
                "PostToolUse",
                "not yet checked: recipe-box/ (pilot-sync did not answer: timed out)\n",
            ),
        )
        self.assertLess(elapsed, 2)


class TestTheTurnSEnd(HookCase):
    def test_the_stop_gives_back_every_hold_of_the_session_and_its_report_reaches_the_agent(
        self,
    ) -> None:
        self.sidecar.answers["/release"] = (200, REPORT)

        completed = self.run_hook(hook_input("Stop"))

        self.assertEqual(self.output(completed), context("Stop", REPORT))
        self.assertEqual(self.sidecar.asked, [RELEASE_ALL])

    def test_an_empty_report_lets_the_turn_end(self) -> None:
        self.assertIsNone(self.output(self.run_hook(hook_input("Stop"))))
        self.assertEqual(self.sidecar.asked, [RELEASE_ALL])

    def test_a_stop_a_stop_hook_kept_going_gives_back_every_hold_unchecked_and_lets_the_turn_end(
        self,
    ) -> None:
        # A pilot-sync older than the query checks and answers the report: still dropped.
        self.sidecar.answers["/release?check=false"] = (200, REPORT)

        completed = self.run_hook(hook_input("Stop", stop_hook_active=True))

        self.assertIsNone(self.output(completed))
        self.assertEqual(self.sidecar.asked, [("/release?check=false", RELEASE_ALL[1])])


class TestTheSession(HookCase):
    def test_a_session_without_pilot_project_takes_no_lock_and_posts_nothing(self) -> None:
        self.sidecar.answers = {"/lock": (409, "never\n"), "/release": (200, REPORT)}
        for event in (*TOOL_EVENTS, "Stop"):
            with self.subTest(event=event):
                completed = self.run_hook(hook_input(event), PILOT_PROJECT=None)
                self.assertIsNone(self.output(completed))
        self.assertEqual(self.sidecar.asked, [])

    def test_with_no_port_set_the_hook_asks_3510_the_port_the_catalog_gives_the_sidecar(
        self,
    ) -> None:
        try:
            default = StandIn(3510)
        except OSError as error:
            self.skipTest(
                f"127.0.0.1:3510 is taken here, as pilot-sync takes it in the store: {error}"
            )
        threading.Thread(target=default.serve_forever, daemon=True).start()
        self.addCleanup(default.server_close)
        self.addCleanup(default.shutdown)

        for shape in (hook_input("PreToolUse"), hook_input("PostToolUse"), hook_input("Stop")):
            with self.subTest(event=shape["hook_event_name"]):
                self.assertIsNone(self.output(self.run_hook(shape, PILOT_SYNC_LOCAL_PORT=None)))
        self.assertEqual(
            default.asked, [lock_of(os.getpid()), release_of(os.getpid()), RELEASE_ALL]
        )
        self.assertEqual(self.sidecar.asked, [])


if __name__ == "__main__":
    unittest.main()
