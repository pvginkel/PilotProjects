"""tools/pilot.py, run as the brain runs it, on a copy of an invented project folder
(tests/fixtures/tree, shaped as PilotApp's docs/projection.md has the store's tree) and
against a stand-in for pilot-sync's local check."""

import fcntl
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from datetime import UTC, datetime
from pathlib import Path

from stand_in import StandIn, check_of, free_port

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools" / "pilot.py"
FIXTURE = Path(__file__).resolve().parent / "fixtures" / "tree"

STORAGE = "4a8c2e19-7b3f-4d05-a6e1-9f2b8c4d0e63"
OLD = "9c1d4f7a-2e8b-4a36-b5c0-3e7f1a9d6b82"
KEY = "b2e7a3c9-6d14-4f8e-9a2b-5c0d8e1f7a46"
IMPORTER = "e6f0b9d3-1c7a-4e25-8d3f-7a9b2c6e0d18"
NOTES = "3b9e6a14-8f2c-4d7b-a1e5-0c4f9b2d8e75"

LINES = {
    1: "1 · opening · Recipe box · done 2026-10-10T08:05:00Z (turn_ended)"
    " · items/1-recipe-box.md · 0e5b7c21-3a9d-4f62-8b14-6c2e9d0a7f31",
    2: "2 · decision · Storage format · done 2026-10-12T09:40:00Z (answered by dana)"
    f" · step t1 · items/2-storage-format.md · {STORAGE}",
    3: f"3 · question · Old recipes · open · step t2 · items/3-old-recipes.md · {OLD}",
    4: "4 · action · Put the backup key in the vault · open · for dana · urgent"
    f" · items/4-put-the-backup-key-in-the-vault.md · {KEY}",
    5: f"5 · work · Write the importer · open · step t2 · no document · {IMPORTER}",
    6: f"6 · document · Import notes · open · inbox/6-import-notes.md · {NOTES}",
}


def canonical(plan: dict) -> str:
    return json.dumps(plan, indent=2, ensure_ascii=False) + "\n"


def pilot_module():
    spec = importlib.util.spec_from_file_location("pilot", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class PilotCase(unittest.TestCase):
    def setUp(self) -> None:
        work = tempfile.TemporaryDirectory()
        self.addCleanup(work.cleanup)
        self.tree = Path(work.name) / "Projects"
        shutil.copytree(FIXTURE, self.tree)
        self.folder = self.tree / "recipe-box"
        self.plan_path = self.folder / "plan.json"
        self.fixture_plan = json.loads(self.plan_path.read_text())
        self.sidecar = StandIn()
        threading.Thread(target=self.sidecar.serve_forever, daemon=True).start()
        self.addCleanup(self.sidecar.server_close)
        self.addCleanup(self.sidecar.shutdown)
        self.addCleanup(self.sidecar.released.set)
        self.port = self.sidecar.server_address[1]

    def environment(self, **overrides: str | None) -> dict[str, str]:
        environment = {
            **os.environ,
            "PILOT_PROJECT": str(self.folder),
            "PILOT_SYNC_LOCAL_PORT": str(self.port),
            **overrides,
        }
        return {name: value for name, value in environment.items() if value is not None}

    def command(self, *args: str) -> list[str]:
        return [sys.executable, str(SCRIPT), *args]

    def pilot(self, *args: str, stdin: str = "", **environment: str | None):
        return subprocess.run(
            self.command(*args),
            check=False,
            cwd=ROOT,
            env=self.environment(**environment),
            input=stdin,
            capture_output=True,
            text=True,
            timeout=30,
        )

    def files(self) -> dict[str, bytes]:
        return {
            path.relative_to(self.tree).as_posix(): path.read_bytes()
            for path in sorted(self.tree.rglob("*"))
            if path.is_file()
        }

    def plan(self) -> dict:
        return json.loads(self.plan_path.read_text())

    def assert_refused(self, *args: str, says: tuple[str, ...], stdin: str = "") -> None:
        before, asked = self.files(), list(self.sidecar.asked)
        completed = self.pilot(*args, stdin=stdin)
        self.assertEqual(completed.returncode, 2, completed)
        self.assertEqual(completed.stdout, "")
        for words in says:
            self.assertIn(words, completed.stderr)
        self.assertEqual(self.files(), before)
        self.assertEqual(self.sidecar.asked, asked)

    def assert_written(self, completed: subprocess.CompletedProcess) -> None:
        """Exit 0, the plan canonical, and its check asked once."""
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(completed.stderr, "")
        self.assertEqual(self.plan_path.read_text(), canonical(self.plan()))
        self.assertEqual(self.sidecar.asked, [check_of(str(self.plan_path))])
        self.assertTrue(completed.stdout.endswith("checked recipe-box/plan.json: clean\n"))

    def put_plan(self, plan: dict) -> None:
        self.plan_path.write_text(canonical(plan))


class TestTheFrame(PilotCase):
    def test_the_project_folder_is_pilot_project(self) -> None:
        completed = self.pilot("items", "list", "--kind", "work")

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(completed.stdout, LINES[5] + "\n")

    def test_project_names_the_folder_over_pilot_project(self) -> None:
        completed = self.pilot(
            "--project",
            str(self.folder),
            "items",
            "list",
            "--kind",
            "work",
            PILOT_PROJECT=str(self.tree / "soup-club"),
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(completed.stdout, LINES[5] + "\n")

    def test_with_no_project_folder_a_verb_is_refused(self) -> None:
        completed = self.pilot("plan", "task", "list", PILOT_PROJECT=None)

        self.assertEqual(completed.returncode, 2)
        self.assertIn("--project", completed.stderr)
        self.assertIn("$PILOT_PROJECT", completed.stderr)

    def test_a_project_folder_that_is_not_there_is_refused(self) -> None:
        completed = self.pilot("plan", "task", "list", PILOT_PROJECT=str(self.tree / "soup-club"))

        self.assertEqual(completed.returncode, 2)
        self.assertIn(f"--project: {self.tree / 'soup-club'} is no folder", completed.stderr)

    def test_a_usage_error_exits_2_naming_the_flag_and_writes_nothing(self) -> None:
        for args, flag in (
            (("plan", "task", "add", "--title", "Bake"), "--id"),
            (
                ("plan", "task", "add", "--id", "t4", "--title", "Bake", "--status", "later"),
                "--status",
            ),
            (
                (
                    "plan",
                    "task",
                    "add",
                    "--id",
                    "t4",
                    "--title",
                    "Bake",
                    "--before",
                    "t1",
                    "--after",
                    "t2",
                ),
                "--after",
            ),
            (("plan", "set", "--ticket", "RB-1", "--no-ticket"), "--no-ticket"),
            (("items", "list", "--waiting"), "--waiting"),
        ):
            with self.subTest(args=args):
                self.assert_refused(*args, says=(flag,))

    def test_the_help_is_every_verb_s_usage_rendered_from_the_one_parser(self) -> None:
        completed = self.pilot("--help")

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(completed.stdout, pilot_module().usage_text() + "\n")
        usages = [line for line in completed.stdout.splitlines() if line.startswith("pilot.py ")]
        self.assertEqual(
            usages,
            [
                "pilot.py [--project <folder>] <verb> …",
                "pilot.py check <path>",
                "pilot.py items list [--open] [--kind <code>]",
                "pilot.py items show <id|path>",
                "pilot.py plan task add --id <id> --title <text>"
                " [--status pending|in_progress|done] [--before <id>|--after <id>]",
                "pilot.py plan task set <id> [--title <text>] [--status pending|in_progress|done]",
                "pilot.py plan task remove <id>",
                "pilot.py plan task list",
                "pilot.py plan note add [--task <id>] --summary <line> [--ref <block id>]..."
                " <content|->",
                "pilot.py plan note strike <id>",
                "pilot.py plan note list [--task <id>]",
                "pilot.py plan set [--ticket <id>|--no-ticket] [--repo owner/Name|--no-repo]",
            ],
        )
        for usage in usages[1:]:
            with self.subTest(usage=usage):
                verb = usage.removeprefix("pilot.py ").split(" <")[0].split(" [")[0].split(" --")[0]
                helped = self.pilot(*verb.split(), "--help")
                self.assertEqual(helped.stdout.splitlines()[0], f"usage: {usage}")


class TestTheWrite(PilotCase):
    def test_a_write_replaces_the_file_whole_keeping_its_mode(self) -> None:
        self.plan_path.chmod(0o640)
        inode = self.plan_path.stat().st_ino
        names = sorted(path.name for path in self.folder.iterdir())

        self.assert_written(self.pilot("plan", "task", "add", "--id", "t4", "--title", "Bake"))

        self.assertNotEqual(self.plan_path.stat().st_ino, inode)
        self.assertEqual(self.plan_path.stat().st_mode & 0o7777, 0o640)
        self.assertEqual(sorted(path.name for path in self.folder.iterdir()), names)

    def test_a_writer_waits_for_the_lock_on_the_project_folder(self) -> None:
        held = os.open(self.folder, os.O_RDONLY | os.O_DIRECTORY)
        self.addCleanup(os.close, held)
        fcntl.flock(held, fcntl.LOCK_EX)
        before = self.plan_path.read_bytes()
        writer = subprocess.Popen(
            self.command("plan", "task", "add", "--id", "t4", "--title", "Bake"),
            cwd=ROOT,
            env=self.environment(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        self.addCleanup(writer.kill)
        time.sleep(1)

        self.assertIsNone(writer.poll())
        self.assertEqual(self.plan_path.read_bytes(), before)

        fcntl.flock(held, fcntl.LOCK_UN)
        _, stderr = writer.communicate(timeout=30)
        self.assertEqual(writer.returncode, 0, stderr)
        self.assertEqual([task["id"] for task in self.plan()["tasks"]], ["t1", "t2", "t3", "t4"])

    def test_writers_on_one_folder_never_interleave(self) -> None:
        writers = [
            subprocess.Popen(
                self.command("plan", "task", "add", "--id", f"w{number}", "--title", "Bake"),
                cwd=ROOT,
                env=self.environment(),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            for number in range(8)
        ]
        for writer in writers:
            self.assertEqual(writer.wait(timeout=60), 0)

        self.assertEqual(
            sorted(task["id"] for task in self.plan()["tasks"]),
            ["t1", "t2", "t3", *(f"w{number}" for number in range(8))],
        )


class TestTheCheck(PilotCase):
    def write(self, **environment: str | None) -> subprocess.CompletedProcess:
        return self.pilot("plan", "task", "set", "t3", "--status", "in_progress", **environment)

    def test_a_writing_verb_ends_with_the_check_of_the_file_it_wrote(self) -> None:
        completed = self.write()

        self.assert_written(completed)
        self.assertEqual(
            completed.stdout,
            "task t3: Publish the card view (in_progress)\nchecked recipe-box/plan.json: clean\n",
        )

    def test_a_save_error_naming_the_file_exits_1(self) -> None:
        for body in (
            "recipe-box/plan.json: task `t2` is removed while its notes `n1` are open\n",
            "recipe-box/plan.json:4: the plan is not JSON: Expecting value\n",
        ):
            with self.subTest(body=body):
                self.sidecar.body = body
                completed = self.write()
                self.assertEqual(completed.returncode, 1, completed.stderr)
                self.assertTrue(
                    completed.stdout.endswith(
                        f"checked recipe-box/plan.json: a Save Error names it\n{body}"
                    )
                )

    def test_another_file_s_lines_a_local_note_and_the_deferrals_leave_the_exit_0(self) -> None:
        self.sidecar.body = (
            "recipe-box/items/3-old-recipes.md:14: block Q1: `to: t9` names neither `plan`"
            " nor a task in the plan\n"
            "recipe-box/plan.json.orig: not a document of the record — files are born"
            " through `add_item`\n"
            "recipe-box/plan.json: a read-only view; re-projected\n"
            "Deferrals without a home (no plan note names these blocks):\n"
            f"- {OLD}/Q1 in recipe-box/items/3-old-recipes.md (Old recipes), to: t2\n"
        )

        completed = self.write()

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertTrue(
            completed.stdout.endswith(
                "checked recipe-box/plan.json: no Save Error names it; the check says\n"
                + self.sidecar.body
            )
        )

    def test_not_yet_checked_exits_3(self) -> None:
        self.sidecar.body = "not yet checked: recipe-box/plan.json\n"

        completed = self.write()

        self.assertEqual(completed.returncode, 3, completed.stderr)
        self.assertTrue(
            completed.stdout.endswith(
                "not yet checked: recipe-box/plan.json\n"
                "the next check shows it: `pilot.py check plan.json`\n"
            )
        )
        self.assertEqual(self.plan()["tasks"][2]["status"], "in_progress")

    def test_a_sidecar_that_does_not_answer_is_not_yet_checked(self) -> None:
        completed = self.write(PILOT_SYNC_LOCAL_PORT=str(free_port()))

        self.assertEqual(completed.returncode, 3, completed.stderr)
        self.assertIn(
            "not yet checked: recipe-box/plan.json (pilot-sync did not answer:", completed.stdout
        )
        self.assertEqual(self.plan()["tasks"][2]["status"], "in_progress")

    def test_an_error_status_after_a_write_is_not_yet_checked(self) -> None:
        self.sidecar.status = 500
        self.sidecar.body = "cannot check a file of the tree\n"

        completed = self.write()

        self.assertEqual(completed.returncode, 3, completed.stderr)
        self.assertIn(
            "not yet checked: recipe-box/plan.json (pilot-sync answered 500:"
            " cannot check a file of the tree)",
            completed.stdout,
        )

    def test_a_sidecar_past_the_5_second_cap_is_not_yet_checked(self) -> None:
        self.sidecar.hold = True
        started = time.monotonic()

        completed = self.write()

        elapsed = time.monotonic() - started
        self.assertEqual(completed.returncode, 3, completed.stderr)
        self.assertIn("not yet checked: recipe-box/plan.json", completed.stdout)
        self.assertGreaterEqual(elapsed, 5)
        self.assertLess(elapsed, 7)

    def test_with_no_port_set_the_check_asks_3510(self) -> None:
        try:
            default = StandIn(3510)
        except OSError as error:
            self.skipTest(
                f"127.0.0.1:3510 is taken here, as pilot-sync takes it in the store: {error}"
            )
        threading.Thread(target=default.serve_forever, daemon=True).start()
        self.addCleanup(default.server_close)
        self.addCleanup(default.shutdown)

        completed = self.write(PILOT_SYNC_LOCAL_PORT=None)

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(default.asked, [check_of(str(self.plan_path))])

    def test_check_asks_for_the_file_alone(self) -> None:
        document = self.folder / "items" / "3-old-recipes.md"
        for path in ("items/3-old-recipes.md", str(document)):
            with self.subTest(path=path):
                self.sidecar.asked.clear()
                before = self.files()
                completed = self.pilot("check", path)
                self.assertEqual(completed.returncode, 0, completed.stderr)
                self.assertEqual(
                    completed.stdout, "checked recipe-box/items/3-old-recipes.md: clean\n"
                )
                self.assertEqual(self.sidecar.asked, [check_of(str(document))])
                self.assertEqual(self.files(), before)

    def test_check_exits_by_its_answer(self) -> None:
        for body, code in (
            ("recipe-box/items/3-old-recipes.md:14: block Q1: `to: t9` names no task\n", 1),
            ("recipe-box/plan.json: task `t2` is removed while its notes `n1` are open\n", 0),
            ("not yet checked: recipe-box/items/3-old-recipes.md\n", 3),
        ):
            with self.subTest(body=body):
                self.sidecar.body = body
                completed = self.pilot("check", "items/3-old-recipes.md")
                self.assertEqual(completed.returncode, code, completed.stderr)
                self.assertIn(body, completed.stdout)

    def test_check_refuses_a_path_outside_the_folder_and_a_file_that_is_not_there(self) -> None:
        for path, says in (
            ("../reference.json", "is not in the project's folder"),
            ("/tmp/notes.md", "is not in the project's folder"),
            ("items/9-soup.md", "no file at"),
        ):
            with self.subTest(path=path):
                self.assert_refused("check", path, says=("<path>", says))

    def test_check_refuses_a_path_pilot_sync_refuses(self) -> None:
        for status, body in (
            (400, 'not a file of the tree /work/Projects: "x"\n'),
            (404, "no file at x\n"),
        ):
            with self.subTest(status=status):
                self.sidecar.status = status
                self.sidecar.body = body
                completed = self.pilot("check", "plan.json")
                self.assertEqual(completed.returncode, 2)
                self.assertIn(f"<path>: pilot-sync refused it: {body.strip()}", completed.stderr)


class TestItems(PilotCase):
    def test_list_prints_each_item_of_the_timeline_on_one_line(self) -> None:
        completed = self.pilot("items", "list")

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(completed.stdout, "".join(f"{line}\n" for line in LINES.values()))
        self.assertEqual(self.sidecar.asked, [])

    def test_list_open_and_kind(self) -> None:
        for args, seqs in (
            (("--open",), [3, 4, 5, 6]),
            (("--kind", "decision"), [2]),
            (("--kind", "decision", "--open"), []),
            (("--kind", "question", "--open"), [3]),
        ):
            with self.subTest(args=args):
                completed = self.pilot("items", "list", *args)
                self.assertEqual(completed.returncode, 0, completed.stderr)
                self.assertEqual(
                    completed.stdout, "".join(f"{LINES[seq]}\n" for seq in seqs) or "no items\n"
                )

    def test_list_refuses_a_kind_reference_json_has_not(self) -> None:
        self.assert_refused(
            "items", "list", "--kind", "recipe", says=("--kind: `recipe` is no item kind", "work")
        )

    def test_show_prints_the_item_s_line_and_its_blocks_with_their_answer_lines(self) -> None:
        for named in (
            OLD,
            "items/3-old-recipes.md",
            str(self.folder / "items" / "3-old-recipes.md"),
        ):
            with self.subTest(named=named):
                completed = self.pilot("items", "show", named)
                self.assertEqual(completed.returncode, 0, completed.stderr)
                self.assertEqual(
                    completed.stdout,
                    f"{LINES[3]}\n"
                    "summary: Which old recipes come over\n"
                    "Q1 · question · Years\n"
                    "    answer: deferred\n"
                    "    by: agent\n"
                    "    at: 2026-10-13T08:00:00Z\n"
                    "    to: t2\n"
                    "    note: Asked again once the importer reads the old files.\n"
                    "Q2 · question · Photos\n"
                    "    no answer\n",
                )

    def test_show_reads_the_document_as_it_stands(self) -> None:
        document = self.folder / "inbox" / "6-import-notes.md"
        document.write_text(
            document.read_text().replace(
                "  - Keep the newer\n",
                "  - Keep the newer\nanswer: Merge both\nby: dana\n"
                "note: |\n  Both folders.\n  Old first.\n",
            )
        )

        completed = self.pilot("items", "show", NOTES)

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(
            completed.stdout,
            f"{LINES[6]}\n"
            "summary: Where the old files are\n"
            "D1 · decision\n"
            "    answer: Merge both\n"
            "    by: dana\n"
            "    note: |\n"
            "      Both folders.\n"
            "      Old first.\n",
        )

    def test_show_an_item_with_no_document_prints_its_line(self) -> None:
        completed = self.pilot("items", "show", IMPORTER)

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(completed.stdout, f"{LINES[5]}\n")

    def test_show_refuses_what_no_item_is(self) -> None:
        for named in ("0b0b0b0b-0000-4000-8000-000000000000", "items/9-soup.md", "handbook.md"):
            with self.subTest(named=named):
                self.assert_refused("items", "show", named, says=("<id|path>: no item",))


class TestPlanTask(PilotCase):
    def test_add_puts_a_pending_task_last(self) -> None:
        completed = self.pilot(
            "plan", "task", "add", "--id", "t4", "--title", "  Crème brûlée cards "
        )

        self.assert_written(completed)
        self.assertTrue(
            completed.stdout.startswith("task t4 added, last: Crème brûlée cards (pending)\n")
        )
        expected = self.fixture_plan
        expected["tasks"].append(
            {"id": "t4", "title": "Crème brûlée cards", "status": "pending", "notes": []}
        )
        self.assertEqual(self.plan_path.read_text(), canonical(expected))

    def test_add_places_the_task_before_or_after_another_with_its_status(self) -> None:
        for args, order in (
            (("--before", "t1"), ["t4", "t1", "t2", "t3"]),
            (("--after", "t1"), ["t1", "t4", "t2", "t3"]),
            (("--after", "t3"), ["t1", "t2", "t3", "t4"]),
        ):
            with self.subTest(args=args):
                self.put_plan(self.fixture_plan)
                self.sidecar.asked.clear()
                completed = self.pilot(
                    "plan",
                    "task",
                    "add",
                    "--id",
                    "t4",
                    "--title",
                    "Bake",
                    "--status",
                    "done",
                    *args,
                )
                self.assert_written(completed)
                self.assertEqual([task["id"] for task in self.plan()["tasks"]], order)
                self.assertEqual(self.plan()["tasks"][order.index("t4")]["status"], "done")

    def test_add_is_refused_an_id_the_plan_has_a_blank_title_and_a_task_it_has_not(self) -> None:
        for args, says in (
            (("--id", "t2", "--title", "Bake"), "--id: the plan has a task `t2` already"),
            (("--id", " ", "--title", "Bake"), "--id: blank"),
            (("--id", "t4", "--title", " "), "--title: blank"),
            (
                ("--id", "t4", "--title", "Bake", "--before", "t9"),
                "--before: the plan has no task `t9`",
            ),
            (
                ("--id", "t4", "--title", "Bake", "--after", "t9"),
                "--after: the plan has no task `t9`",
            ),
        ):
            with self.subTest(args=args):
                self.assert_refused("plan", "task", "add", *args, says=(says,))

    def test_set_changes_the_title_and_the_status(self) -> None:
        completed = self.pilot(
            "plan", "task", "set", "t2", "--title", "Import the 2019 recipes", "--status", "done"
        )

        self.assert_written(completed)
        self.assertTrue(completed.stdout.startswith("task t2: Import the 2019 recipes (done)\n"))
        expected = self.fixture_plan
        expected["tasks"][1].update(title="Import the 2019 recipes", status="done")
        self.assertEqual(self.plan_path.read_text(), canonical(expected))

    def test_set_is_refused_nothing_to_set_and_a_task_the_plan_has_not(self) -> None:
        self.assert_refused(
            "plan", "task", "set", "t2", says=("--title, --status: nothing to set",)
        )
        self.assert_refused(
            "plan",
            "task",
            "set",
            "t9",
            "--status",
            "done",
            says=("<id>: the plan has no task `t9`",),
        )

    def test_remove_takes_the_task_out_of_the_plan(self) -> None:
        completed = self.pilot("plan", "task", "remove", "t3")

        self.assert_written(completed)
        expected = self.fixture_plan
        del expected["tasks"][2]
        self.assertEqual(self.plan_path.read_text(), canonical(expected))

    def test_remove_is_refused_while_the_task_has_open_notes_naming_them(self) -> None:
        plan = self.fixture_plan
        plan["tasks"][1]["notes"].append(
            {
                "id": "n7",
                "summary": "Sizes",
                "content": "Check the sizes.",
                "refs": [],
                "created": "2026-10-15T08:00:00Z",
            }
        )
        self.put_plan(plan)

        self.assert_refused(
            "plan", "task", "remove", "t2", says=("task `t2` has the open notes `n1`, `n7`",)
        )
        self.assert_refused(
            "plan", "task", "remove", "t9", says=("<id>: the plan has no task `t9`",)
        )

    def test_list_prints_the_tasks_in_order(self) -> None:
        completed = self.pilot("plan", "task", "list")

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(
            completed.stdout,
            "t1 · done · Pick a storage format\n"
            "t2 · in_progress · Import the old recipes · notes n1\n"
            "t3 · pending · Publish the card view\n",
        )
        self.assertEqual(self.sidecar.asked, [])

    def test_a_writer_leaves_a_plan_canonical_in_the_record_s_order(self) -> None:
        shuffled = {
            "notes": self.fixture_plan["notes"],
            "tasks": [
                {"status": "done", "title": "Pick a storage format", "id": "t1"},
                *self.fixture_plan["tasks"][1:],
            ],
            "repo": "example/recipe-box",
        }
        self.plan_path.write_text(json.dumps(shuffled, indent=4))

        self.assert_written(self.pilot("plan", "task", "set", "t3", "--status", "in_progress"))

        expected = self.fixture_plan
        expected["ticket"] = None
        expected["tasks"][2]["status"] = "in_progress"
        self.assertEqual(self.plan_path.read_text(), canonical(expected))

    def test_a_plan_out_of_the_record_s_shape_is_refused(self) -> None:
        for text, says in (
            ('{\n  "ticket": \n', "plan.json: "),
            (canonical({**self.fixture_plan, "owner": "dana"}), "the plan has the key `owner`"),
            (canonical({**self.fixture_plan, "tasks": {}}), "plan.json: `tasks` is not a list"),
        ):
            with self.subTest(text=text[:40]):
                self.plan_path.write_text(text)
                self.assert_refused(
                    "plan", "task", "add", "--id", "t4", "--title", "Bake", says=(says,)
                )


class TestPlanNote(PilotCase):
    def test_add_puts_the_next_note_on_the_task_with_its_refs(self) -> None:
        started = datetime.now(UTC).replace(microsecond=0)

        completed = self.pilot(
            "plan",
            "note",
            "add",
            "--task",
            "t3",
            "--summary",
            "Photos first",
            "--ref",
            f"{OLD}/Q2",
            "--ref",
            f"{NOTES}/D1",
            "--ref",
            f"{OLD}/Q2",
            "Show the cards with a photo first.",
        )

        self.assert_written(completed)
        self.assertTrue(completed.stdout.startswith("note n3 added on task t3\n"))
        (note,) = self.plan()["tasks"][2]["notes"]
        created = datetime.strptime(note.pop("created"), "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=UTC)
        self.assertLessEqual(started, created)
        self.assertLessEqual(created, datetime.now(UTC))
        self.assertEqual(
            note,
            {
                "id": "n3",
                "summary": "Photos first",
                "content": "Show the cards with a photo first.",
                "refs": [f"{OLD}/Q2", f"{NOTES}/D1"],
            },
        )

    def test_add_without_a_task_puts_the_note_on_the_plan_its_content_from_stdin(self) -> None:
        completed = self.pilot(
            "plan",
            "note",
            "add",
            "--summary",
            "Units",
            "-",
            stdin="Grams, never cups.\n\nAsk dana.\n",
        )

        self.assert_written(completed)
        self.assertTrue(completed.stdout.startswith("note n3 added on the plan\n"))
        notes = self.plan()["notes"]
        self.assertEqual([note["id"] for note in notes], ["n2", "n3"])
        self.assertEqual(notes[1]["content"], "Grams, never cups.\n\nAsk dana.")
        self.assertEqual(notes[1]["refs"], [])

    def test_add_is_refused_a_task_a_ref_and_a_text_the_record_would_not_take(self) -> None:
        for args, says in (
            (("--task", "t9", "--summary", "Units", "Grams."), "--task: the plan has no task `t9`"),
            (
                ("--summary", "Units", "--ref", f"{OLD}/Q9", "Grams."),
                f"--ref: `{OLD}/Q9` names no block",
            ),
            (
                ("--summary", "Units", "--ref", f"{IMPORTER}/W1", "Grams."),
                f"--ref: `{IMPORTER}/W1`",
            ),
            (("--summary", "Units", "--ref", "Q1", "Grams."), "--ref: `Q1`"),
            (("--summary", " ", "Grams."), "--summary: blank"),
            (("--summary", "Units", " "), "<content|->: blank"),
        ):
            with self.subTest(args=args):
                self.assert_refused("plan", "note", "add", *args, says=(says,))

    def test_strike_takes_the_note_out_of_the_plan(self) -> None:
        for note_id, owner in (("n1", ("tasks", 1)), ("n2", ("notes",))):
            with self.subTest(note=note_id):
                self.put_plan(self.fixture_plan)
                self.sidecar.asked.clear()
                completed = self.pilot("plan", "note", "strike", note_id)
                self.assert_written(completed)
                self.assertTrue(completed.stdout.startswith(f"note {note_id} struck\n"))
                expected = json.loads(canonical(self.fixture_plan))
                if owner == ("notes",):
                    expected["notes"] = []
                else:
                    expected["tasks"][1]["notes"] = []
                self.assertEqual(self.plan(), expected)

        self.assert_refused(
            "plan", "note", "strike", "n9", says=("<id>: the plan has no open note `n9`",)
        )

    def test_list_shows_each_note_with_its_refs_blocks_as_they_stand(self) -> None:
        completed = self.pilot("plan", "note", "list")

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(
            completed.stdout,
            "n1 · t2 · Ask which years come over\n"
            "    Once the importer reads the old files, ask again.\n"
            f"    {OLD}/Q1 · Old recipes · answer: deferred → t2 by agent\n"
            "n2 · plan · Card layout after the import\n"
            "    The layout waits for real recipes; Markdown keeps it simple.\n"
            f"    {STORAGE}/D1 · Storage format · answer: Markdown by dana\n",
        )
        self.assertEqual(self.sidecar.asked, [])

    def test_list_makes_a_stale_note_plain(self) -> None:
        document = self.folder / "items" / "3-old-recipes.md"
        document.write_text(
            document.read_text()
            .replace("answer: deferred\nby: agent\n", "answer: Since 2015\nby: dana\nvia: chat\n")
            .replace("to: t2\n", "")
        )
        plan = self.fixture_plan
        plan["tasks"][1]["notes"][0]["refs"].append(f"{KEY}/A9")
        self.put_plan(plan)

        completed = self.pilot("plan", "note", "list", "--task", "t2")

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(
            completed.stdout,
            "n1 · t2 · Ask which years come over\n"
            "    Once the importer reads the old files, ask again.\n"
            f"    {OLD}/Q1 · Old recipes · answer: Since 2015 by dana via chat\n"
            f"    {KEY}/A9 · no block of this project's items\n",
        )

    def test_list_of_a_task_with_no_notes_and_of_a_task_the_plan_has_not(self) -> None:
        completed = self.pilot("plan", "note", "list", "--task", "t1")

        self.assertEqual((completed.returncode, completed.stdout), (0, "no open notes\n"))
        self.assert_refused(
            "plan", "note", "list", "--task", "t9", says=("--task: the plan has no task `t9`",)
        )


class TestPlanSet(PilotCase):
    def test_set_sets_and_clears_the_ticket_and_the_repo(self) -> None:
        for args, ticket, repo in (
            (("--ticket", "RB-40", "--repo", "example/cookbook"), "RB-40", "example/cookbook"),
            (("--no-ticket",), None, "example/cookbook"),
            (("--no-repo", "--ticket", "RB-41"), "RB-41", None),
        ):
            with self.subTest(args=args):
                self.sidecar.asked.clear()
                completed = self.pilot("plan", "set", *args)
                self.assert_written(completed)
                self.assertTrue(
                    completed.stdout.startswith(
                        f"plan: ticket {ticket or 'none'} · repo {repo or 'none'}\n"
                    )
                )
                self.assertEqual((self.plan()["ticket"], self.plan()["repo"]), (ticket, repo))
                self.assertEqual(self.plan()["tasks"], self.fixture_plan["tasks"])

    def test_set_is_refused_nothing_to_set_and_a_blank_value(self) -> None:
        self.assert_refused("plan", "set", says=("nothing to set",))
        self.assert_refused("plan", "set", "--ticket", " ", says=("--ticket: blank",))
        self.assert_refused("plan", "set", "--repo", "", says=("--repo: blank",))


if __name__ == "__main__":
    unittest.main()
