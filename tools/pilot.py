#!/usr/bin/env python3
"""Pilot's editing scripts over one project's folder of the store's tree.

Design 3 §7. One verb per intent, on the folder `$PILOT_PROJECT` names, or
`--project`. A refusal goes to stderr, naming the flag or the rule, exits 2
and writes nothing. Every read-modify-write holds an exclusive flock on the
project folder itself, and every file is replaced whole: written to a
temporary file in its directory, then renamed over it. Every writing verb
ends with pilot-sync's local check of each file it wrote and prints its
answer (PilotApp's docs/sync.md, § The local check).

Exit codes: 0 done, and the check names no file written · 1 a Save Error
names a file written: its save held, or a line reverted · 2 refused, nothing
written · 3 not yet checked.
"""

import argparse
import contextlib
import fcntl
import json
import os
import sys
import tempfile
import urllib.error
import urllib.parse
import urllib.request
from collections.abc import Callable, Iterator
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pilot_dsl as dsl

PROG = "pilot.py"
PLAN = "plan.json"
TIMELINE = "timeline.json"
REFERENCE = "reference.json"
TASK_STATUSES = ("pending", "in_progress", "done")
DRAFT = "project.md"
DOCUMENT_FOLDERS = ("items", "inbox")
OPENING = "opening"
# The answer of an action Pilot has claimed (F21.6, D062).
CLAIM = "Pilot does it"

DONE, HELD, REFUSED, UNCHECKED = 0, 1, 2, 3

# pilot-sync answers `not yet checked` itself once 2 s of waiting for the
# file's ingest have passed; the rest of the cap bounds its call to Pilot.
CHECK_CAP_SECONDS = 5
NOT_YET_CHECKED = "not yet checked: "
# The local notes pilot-sync prints as `<path>: <note>`, in the shape of a
# Save Error without a line (PilotApp's sidecar/internal/sidecar/tree.go).
LOCAL_NOTES = (
    "not a document of the record — files are born through `add_item`",
    "a read-only view; re-projected",
)
HOMELESS_HEADING = "Deferrals without a home (no plan note names these blocks):"

# plan.json's keys in the record's order (PilotApp's docs/projection.md).
_PLAN_KEYS = ("ticket", "repo", "tasks", "notes")
_TASK_KEYS = ("id", "title", "status", "notes")
_NOTE_KEYS = ("id", "summary", "content", "refs", "created")


class Refused(Exception):
    """A refusal, its text naming the flag or the rule; nothing is written."""


@dataclass(frozen=True)
class Project:
    """A project's folder of the store's tree, which is its parent."""

    folder: Path

    @property
    def tree(self) -> Path:
        return self.folder.parent

    def file(self, name: str, what: str) -> Path:
        """`name`, relative to the folder or absolute, as an absolute path
        inside it."""
        path = Path(os.path.normpath(self.folder / name))
        if not path.is_relative_to(self.folder) or path == self.folder:
            raise Refused(f"{what}: {name} is not in the project's folder {self.folder}")
        return path

    def tree_path(self, path: Path) -> str:
        """The path as pilot-sync names it, from the tree's root."""
        return path.relative_to(self.tree).as_posix()


@dataclass(frozen=True)
class Checked:
    """pilot-sync's answer on one file: its HTTP status, none when it did not
    answer, and its text."""

    path: Path
    status: int | None
    answer: str


# -- the frame -----------------------------------------------------------------


def _project(flag: str | None) -> Project:
    named = flag if flag is not None else os.environ.get("PILOT_PROJECT")
    if not named:
        raise Refused("--project: no project folder; pass --project or set $PILOT_PROJECT")
    folder = Path(os.path.abspath(named))
    if not folder.is_dir():
        raise Refused(f"--project: {folder} is no folder")
    return Project(folder)


@contextlib.contextmanager
def _locked(project: Project) -> Iterator[None]:
    """An exclusive flock on the project folder itself, so that two writers
    on one folder never interleave and no lock file lands in the tree."""
    fd = os.open(project.folder, os.O_RDONLY | os.O_DIRECTORY)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX)
        yield
    finally:
        os.close(fd)


def _write(path: Path, text: str) -> None:
    """Replace the file whole, keeping its mode: a reader, pilot-sync's
    watcher among them, never sees half a file."""
    mode = path.stat().st_mode & 0o7777
    fd, temporary = tempfile.mkstemp(dir=path.parent, prefix=f".{path.name}.", suffix=".tmp")
    try:
        with os.fdopen(fd, "wb") as file:
            file.write(text.encode())
            os.fchmod(file.fileno(), mode)
        os.replace(temporary, path)
    except BaseException:
        with contextlib.suppress(FileNotFoundError):
            os.unlink(temporary)
        raise


def _ask(path: Path) -> Checked:
    """pilot-sync's local check of the file: `GET /check?path=` on
    127.0.0.1, at the port `$PILOT_SYNC_LOCAL_PORT` names, 3510 when unset."""
    port = os.environ.get("PILOT_SYNC_LOCAL_PORT", "3510")
    query = urllib.parse.urlencode({"path": str(path)})
    try:
        with urllib.request.urlopen(
            f"http://127.0.0.1:{port}/check?{query}", timeout=CHECK_CAP_SECONDS
        ) as response:
            return Checked(path, response.status, response.read().decode())
    except urllib.error.HTTPError as error:
        return Checked(path, error.code, error.read().decode())
    except OSError as error:
        return Checked(path, None, f"pilot-sync did not answer: {error}")


def _names(line: str, tree_path: str) -> bool:
    """Whether the answer's line is a Save Error of the file: `<path>:<line>:
    <message>`, or `<path>: <message>` that is no local note."""
    if not line.startswith(tree_path):
        return False
    rest = line.removeprefix(tree_path)
    if rest.startswith(": "):
        return rest.removeprefix(": ") not in LOCAL_NOTES
    number, colon, _ = rest.removeprefix(":").partition(": ")
    return rest.startswith(":") and bool(colon) and number.isdigit()


def _verdict(project: Project, checked: Checked) -> int:
    tree_path = project.tree_path(checked.path)
    if checked.status != 200 or checked.answer.startswith(NOT_YET_CHECKED):
        return UNCHECKED
    for line in checked.answer.splitlines():
        if line == HOMELESS_HEADING:
            break
        if _names(line, tree_path):
            return HELD
    return DONE


def _report(project: Project, checked: Checked) -> int:
    """Print the check's answer on the file, and return its exit code."""
    tree_path = project.tree_path(checked.path)
    verdict = _verdict(project, checked)
    answer = checked.answer.rstrip("\n")
    if verdict == UNCHECKED:
        if not answer.startswith(NOT_YET_CHECKED):
            status = "" if checked.status is None else f"pilot-sync answered {checked.status}: "
            answer = f"{NOT_YET_CHECKED}{tree_path} ({status}{answer})"
        relative = checked.path.relative_to(project.folder).as_posix()
        print(f"{answer}\nthe next check shows it: `{PROG} check {relative}`")
    elif verdict == HELD:
        print(f"checked {tree_path}: a Save Error names it\n{answer}")
    elif answer:
        print(f"checked {tree_path}: no Save Error names it; the check says\n{answer}")
    else:
        print(f"checked {tree_path}: clean")
    return verdict


def _check_written(project: Project, paths: list[Path]) -> int:
    """The check of every file a verb wrote, one call each: 1 when a Save
    Error names one, else 3 when one is not yet checked, else 0."""
    verdicts = [_report(project, _ask(path)) for path in paths]
    return HELD if HELD in verdicts else max(verdicts)


def _read_json(path: Path, what: str) -> Any:
    try:
        return json.loads(path.read_text())
    except FileNotFoundError:
        raise Refused(f"{what}: no {path.name} at {path.parent}") from None
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise Refused(f"{what}: {path} is not JSON: {error}") from None


def _utc(moment: datetime) -> str:
    """A time as the files write it: UTC, to the second."""
    return moment.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def _text(value: str, flag: str) -> str:
    """A value as the record keeps it: trimmed, and never blank."""
    trimmed = value.strip()
    if not trimmed:
        raise Refused(f"{flag}: blank")
    return trimmed


def _stdin_or(value: str) -> str:
    return sys.stdin.read() if value == "-" else value


# -- the timeline and the documents -------------------------------------------


def _timeline(project: Project) -> dict[str, Any]:
    timeline: dict[str, Any] = _read_json(project.folder / TIMELINE, "the timeline")
    return timeline


def _parsed(project: Project, item: dict[str, Any]) -> dsl.ParsedDocument | None:
    """The item's document as it stands on disk; none without one."""
    if item["path"] is None:
        return None
    try:
        text = (project.folder / item["path"]).read_text(errors="replace")
    except FileNotFoundError:
        return None
    return dsl.parse(text)


def _block_of(
    project: Project, ref: str
) -> tuple[dict[str, Any], dsl.ParsedDocument, dsl.Block] | None:
    """The item, document and block a ref names, `<item id>/<local id>`, as
    the folder holds them; none where it names no block of an item's."""
    item_id, _, local_id = ref.partition("/")
    item = next((item for item in _timeline(project)["items"] if item["id"] == item_id), None)
    document = None if item is None else _parsed(project, item)
    if document is None:
        return None
    block = next((block for block in document.blocks if block.local_id == local_id), None)
    return None if block is None else (item, document, block)


def _answer_line(block: dsl.Block) -> str:
    """The block's answer as it stands: `answer: v4 by ada`, `answer:
    deferred → t5 by agent`, `done: <at> by ada`, or `no answer`."""
    parts = []
    if block.answer is not None:
        parts.append(f"answer: {block.answer}" + ("" if block.to is None else f" → {block.to}"))
    if block.done is not None:
        parts.append(f"done: {_utc(block.done)}")
    if not parts:
        return "no answer"
    line = " · ".join(parts)
    if block.by is not None:
        line += f" by {block.by}"
    if block.via is not None and block.via != dsl.AnswerChannel.APP:
        line += f" via {block.via}"
    return line


def _item_line(item: dict[str, Any]) -> str:
    parts = [str(item["seq"]), item["kind"], item["title"] or "(no title)"]
    done = item["done"]
    if done is None:
        parts.append("open")
    else:
        by = "" if done["by"] is None else f" by {done['by']}"
        parts.append(f"done {done['at']} ({done['cause']}{by})")
    if item["for"] is not None:
        parts.append(f"for {item['for']}")
    if item["step"] is not None:
        parts.append(f"step {item['step']}")
    if item["urgent"]:
        parts.append("urgent")
    parts.append(item["path"] or "no document")
    parts.append(item["id"])
    return " · ".join(parts)


def _items_list(project: Project, args: argparse.Namespace) -> int:
    items = _timeline(project)["items"]
    if args.kind is not None:
        reference = _read_json(project.tree / REFERENCE, "--kind")
        codes = [kind["code"] for kind in reference["item_kinds"]]
        if args.kind not in codes:
            raise Refused(
                f"--kind: `{args.kind}` is no item kind; {REFERENCE} has {', '.join(codes)}"
            )
        items = [item for item in items if item["kind"] == args.kind]
    if args.open:
        items = [item for item in items if item["done"] is None]
    for item in items:
        print(_item_line(item))
    if not items:
        print("no items")
    return DONE


def _items_show(project: Project, args: argparse.Namespace) -> int:
    items = _timeline(project)["items"]
    item = next((item for item in items if item["id"] == args.item), None)
    if item is None:
        path = project.file(args.item, "<id|path>").relative_to(project.folder).as_posix()
        item = next((item for item in items if item["path"] == path), None)
    if item is None:
        raise Refused(f"<id|path>: no item of {TIMELINE} has the id or the path {args.item}")
    print(_item_line(item))
    if item["summary"] is not None:
        print(f"summary: {item['summary']}")
    document = _parsed(project, item)
    if item["path"] is not None and document is None:
        print(f"its document {item['path']} is not on disk")
    if document is None:
        return DONE
    lines = (project.folder / item["path"]).read_text(errors="replace").splitlines()
    for block in document.blocks:
        heading = "" if block.section is None else f" · {block.section.heading}"
        print(f"{block.local_id} · {block.kind}{heading}")
        spans = sorted(
            (span for key, span in block.lines.items() if key in dsl.ANSWER_KEYS),
            key=lambda span: span.first,
        )
        for span in spans:
            for line in lines[span.first - 1 : span.last]:
                print(f"    {line}")
        if not spans:
            print("    no answer")
    return DONE


def _check(project: Project, args: argparse.Namespace) -> int:
    path = project.file(args.path, "<path>")
    if not path.is_file():
        raise Refused(f"<path>: no file at {path}")
    checked = _ask(path)
    if checked.status in (400, 404):
        raise Refused(f"<path>: pilot-sync refused it: {checked.answer.strip()}")
    return _report(project, checked)


# -- plan.json -----------------------------------------------------------------


def _read_plan(project: Project) -> dict[str, Any]:
    """plan.json, in the record's order; one out of the record's shape is
    refused."""
    data = _read_json(project.folder / PLAN, PLAN)

    def shaped(value: Any, keys: tuple[str, ...], what: str) -> dict[str, Any]:
        if not isinstance(value, dict):
            raise Refused(f"{PLAN}: {what} is not an object")
        stray = [key for key in value if key not in keys]
        if stray:
            raise Refused(f"{PLAN}: {what} has the key `{stray[0]}`, which the record's has not")
        read = {key: value.get(key) for key in keys}
        for key, held in read.items():
            if key not in ("tasks", "notes", "refs") and not isinstance(held, str | None):
                raise Refused(f"{PLAN}: `{key}` of {what} is not a string")
        return read

    def listed(value: Any, what: str) -> list[Any]:
        if value is None:
            return []
        if not isinstance(value, list):
            raise Refused(f"{PLAN}: {what} is not a list")
        return value

    def notes(value: Any, owner: str) -> list[dict[str, Any]]:
        read = []
        for note in listed(value, f"`notes` of {owner}"):
            note = shaped(note, _NOTE_KEYS, f"a note of {owner}")
            note["refs"] = listed(note["refs"], f"`refs` of note `{note['id']}`")
            for ref in note["refs"]:
                if not isinstance(ref, str):
                    raise Refused(
                        f"{PLAN}: `refs` of note `{note['id']}` holds {json.dumps(ref)},"
                        " not a block id"
                    )
            read.append(note)
        return read

    plan = shaped(data, _PLAN_KEYS, "the plan")
    tasks = []
    for task in listed(plan["tasks"], "`tasks`"):
        task = shaped(task, _TASK_KEYS, "a task")
        task["notes"] = notes(task["notes"], f"task `{task['id']}`")
        tasks.append(task)
    plan["tasks"] = tasks
    plan["notes"] = notes(plan["notes"], "the plan")
    return plan


def _render_plan(plan: dict[str, Any]) -> str:
    """plan.json as the record renders it: two-space indent, non-ASCII as it
    is, a final newline."""
    return json.dumps(plan, indent=2, ensure_ascii=False) + "\n"


def _task(plan: dict[str, Any], task_id: str, flag: str) -> dict[str, Any]:
    task = next((task for task in plan["tasks"] if task["id"] == task_id), None)
    if task is None:
        raise Refused(f"{flag}: the plan has no task `{task_id}`")
    return task


def _all_notes(plan: dict[str, Any]) -> Iterator[tuple[dict[str, Any] | None, dict[str, Any]]]:
    """Every open note with its task, none for the plan's own."""
    for task in plan["tasks"]:
        for note in task["notes"]:
            yield task, note
    for note in plan["notes"]:
        yield None, note


def _edit_plan(project: Project, edit: Callable[[dict[str, Any]], str]) -> int:
    """Read plan.json, apply `edit`, which refuses or says what it did,
    write the plan back canonical, and check it."""
    path = project.folder / PLAN
    with _locked(project):
        plan = _read_plan(project)
        done = edit(plan)
        _write(path, _render_plan(plan))
    print(done)
    return _check_written(project, [path])


def _task_add(project: Project, args: argparse.Namespace) -> int:
    def edit(plan: dict[str, Any]) -> str:
        task_id = _text(args.id, "--id")
        if any(task["id"] == task_id for task in plan["tasks"]):
            raise Refused(f"--id: the plan has a task `{task_id}` already")
        title = _text(args.title, "--title")
        task = {"id": task_id, "title": title, "status": args.status, "notes": []}
        tasks = plan["tasks"]
        if args.before is not None:
            index = tasks.index(_task(plan, args.before, "--before"))
            where = f"before {args.before}"
        elif args.after is not None:
            index = tasks.index(_task(plan, args.after, "--after")) + 1
            where = f"after {args.after}"
        else:
            index, where = len(tasks), "last"
        tasks.insert(index, task)
        return f"task {task_id} added, {where}: {task['title']} ({task['status']})"

    return _edit_plan(project, edit)


def _task_set(project: Project, args: argparse.Namespace) -> int:
    def edit(plan: dict[str, Any]) -> str:
        if args.title is None and args.status is None:
            raise Refused("--title, --status: nothing to set; give one or both")
        task = _task(plan, args.id, "<id>")
        if args.title is not None:
            task["title"] = _text(args.title, "--title")
        if args.status is not None:
            task["status"] = args.status
        return f"task {task['id']}: {task['title']} ({task['status']})"

    return _edit_plan(project, edit)


def _task_remove(project: Project, args: argparse.Namespace) -> int:
    def edit(plan: dict[str, Any]) -> str:
        task = _task(plan, args.id, "<id>")
        if task["notes"]:
            notes = ", ".join(f"`{note['id']}`" for note in task["notes"])
            raise Refused(
                f"<id>: task `{task['id']}` has the open notes {notes}: strike them first"
                f" (`{PROG} plan note strike <id>`), or move them to another task in {PLAN}"
            )
        plan["tasks"].remove(task)
        return f"task {task['id']} removed"

    return _edit_plan(project, edit)


def _task_list(project: Project, args: argparse.Namespace) -> int:
    plan = _read_plan(project)
    for task in plan["tasks"]:
        line = f"{task['id']} · {task['status']} · {task['title']}"
        if task["notes"]:
            line += " · notes " + ", ".join(note["id"] for note in task["notes"])
        print(line)
    if not plan["tasks"]:
        print("the plan has no tasks")
    return DONE


def _note_add(project: Project, args: argparse.Namespace) -> int:
    content = _text(_stdin_or(args.content), "<content|->")

    def edit(plan: dict[str, Any]) -> str:
        owner = plan["notes"] if args.task is None else _task(plan, args.task, "--task")["notes"]
        refs = list(dict.fromkeys(ref.strip() for ref in args.ref))
        for ref in refs:
            if _block_of(project, ref) is None:
                raise Refused(
                    f"--ref: `{ref}` names no block of this project's items"
                    f" (`<item id>/<local id>`, the item's id from {TIMELINE})"
                )
        summary = _text(args.summary, "--summary")
        note_id = _new_note(plan, owner, summary, content, refs, datetime.now(UTC))
        on = "the plan" if args.task is None else f"task {args.task}"
        return f"note {note_id} added on {on}"

    return _edit_plan(project, edit)


def _new_note(
    plan: dict[str, Any],
    owner: list[dict[str, Any]],
    summary: str,
    content: str,
    refs: list[str],
    created: datetime,
) -> str:
    """A note appended to `owner`, a task's notes or the plan's, its id the
    next `n<number>` among the plan's open notes; its id."""
    numbers = [
        int(note["id"][1:])
        for _, note in _all_notes(plan)
        if isinstance(note["id"], str) and note["id"][:1] == "n" and note["id"][1:].isdigit()
    ]
    note_id = f"n{max(numbers, default=0) + 1}"
    owner.append(
        {
            "id": note_id,
            "summary": summary,
            "content": content,
            "refs": refs,
            "created": _utc(created),
        }
    )
    return note_id


def _note_strike(project: Project, args: argparse.Namespace) -> int:
    def edit(plan: dict[str, Any]) -> str:
        found = next(((task, n) for task, n in _all_notes(plan) if n["id"] == args.id), None)
        if found is None:
            raise Refused(f"<id>: the plan has no open note `{args.id}`")
        task, note = found
        (plan["notes"] if task is None else task["notes"]).remove(note)
        return f"note {note['id']} struck"

    return _edit_plan(project, edit)


def _note_list(project: Project, args: argparse.Namespace) -> int:
    plan = _read_plan(project)
    if args.task is not None:
        _task(plan, args.task, "--task")
    notes = [
        (task, note)
        for task, note in _all_notes(plan)
        if args.task is None or (task is not None and task["id"] == args.task)
    ]
    for task, note in notes:
        print(f"{note['id']} · {'plan' if task is None else task['id']} · {note['summary']}")
        for line in (note["content"] or "").splitlines():
            print(f"    {line}")
        for ref in note["refs"]:
            found = _block_of(project, ref)
            if found is None:
                print(f"    {ref} · no block of this project's items")
                continue
            item, document, block = found
            title = item["title"] or document.title or "(no title)"
            print(f"    {ref} · {title} · {_answer_line(block)}")
    if not notes:
        print("no open notes")
    return DONE


def _plan_set(project: Project, args: argparse.Namespace) -> int:
    def edit(plan: dict[str, Any]) -> str:
        if args.ticket is None and not args.no_ticket and args.repo is None and not args.no_repo:
            raise Refused(
                "--ticket, --no-ticket, --repo, --no-repo: nothing to set;"
                " give --ticket or --no-ticket, --repo or --no-repo, or one of each"
            )
        if args.ticket is not None or args.no_ticket:
            plan["ticket"] = None if args.no_ticket else _text(args.ticket, "--ticket")
        if args.repo is not None or args.no_repo:
            plan["repo"] = None if args.no_repo else _text(args.repo, "--repo")
        return f"plan: ticket {plan['ticket'] or 'none'} · repo {plan['repo'] or 'none'}"

    return _edit_plan(project, edit)


# -- a document's blocks -------------------------------------------------------


@dataclass(frozen=True)
class _Document:
    """A document a block verb writes, as it stands on disk: the item whose
    it is, none for the draft."""

    path: Path
    relative: str
    item: dict[str, Any] | None
    text: str
    parsed: dsl.ParsedDocument

    @property
    def kind(self) -> dsl.DocumentKind:
        """What the engine ingests the file as (PilotApp's engine/ingest.py)."""
        if self.item is None:
            return dsl.DocumentKind.DRAFT
        if self.item["kind"] == OPENING:
            return dsl.DocumentKind.OPENING
        if self.relative.startswith("inbox/"):
            return dsl.DocumentKind.REGISTERED_ITEM
        return dsl.DocumentKind.OWN_ITEM

    def block(self, local_id: str) -> dsl.Block:
        return next(block for block in self.parsed.blocks if block.local_id == local_id)


def _document(project: Project, name: str) -> _Document:
    """The document `<file>` names, read whole: the draft, or an item's
    document under `items/` or `inbox/`, which `timeline.json` names."""
    path = project.file(name, "<file>")
    relative = path.relative_to(project.folder).as_posix()
    folder, _, rest = relative.partition("/")
    if relative != DRAFT and (folder not in DOCUMENT_FOLDERS or not rest or "/" in rest):
        raise Refused(
            f"<file>: {relative} is no document a block is written in:"
            f" items/<file>, inbox/<file> or {DRAFT}"
        )
    if not path.is_file():
        raise Refused(f"<file>: no file at {path}")
    item = None
    if relative != DRAFT:
        items = _timeline(project)["items"]
        item = next((item for item in items if item["path"] == relative), None)
        if item is None:
            raise Refused(
                f"<file>: no item of {TIMELINE} has the path {relative};"
                " an item's file is born through `add_item`"
            )
    try:
        text: str | None = path.read_bytes().decode()
    except UnicodeDecodeError:
        text = None
    if text is None or "\x00" in text:
        raise Refused(
            f"<file>: {relative} is not UTF-8 text, or holds a NUL: the engine would hold the write"
        )
    return _Document(path, relative, item, text, dsl.parse(text))


def _spliced(document: _Document, splice: Callable[[str], str]) -> str:
    """The document's text with the block's lines spliced in by pilot-dsl's
    writer, as the record splices its own."""
    try:
        return splice(document.text)
    except dsl.WriteRefused as refusal:
        raise Refused(f"<block id>: {refusal}") from None


def _not_a_persons(block: dsl.Block) -> None:
    """A block a person answered or did is the record's whole (F32.7)."""
    if block.by is not None and block.by != dsl.AGENT:
        did = "done" if block.done is not None else "answered"
        raise Refused(
            f"<block id>: block {block.local_id} is {did} by {block.by}:"
            " a change of meaning is a new block or a new item (F32.7)"
        )


def _validated(project: Project, document: _Document, text: str) -> None:
    """`validate()` on the text to write, with the facts the tree carries:
    the confirmation reasons, the plan's live tasks, the `to`s the file has.
    It carries no handle and no removed task, so the rules resting on them
    are left to the check after the write."""
    reference = _read_json(project.tree / REFERENCE, "the confirmation reasons")
    facts = dsl.Facts(
        document=document.kind,
        handles=None,
        plan_task_ids={task["id"] for task in _read_plan(project)["tasks"]},
        removed_task_ids=None,
        confirmation_reasons=[reason["code"] for reason in reference["confirmation_reasons"]],
        taken_slugs=frozenset(),
        published_to={
            block.local_id: block.to for block in document.parsed.blocks if block.to is not None
        },
    )
    faults = dsl.validate(dsl.parse(text), facts)
    if faults:
        tree_path = project.tree_path(document.path)
        lines = "\n".join(
            f"{tree_path}: {fault.message}"
            if fault.line is None
            else f"{tree_path}:{fault.line}: {fault.message}"
            for fault in faults
        )
        raise Refused(f"<file>: the engine would hold the write:\n{lines}")


def _note_text(value: str | None, flag: str) -> str | None:
    return None if value is None else _text(_stdin_or(value), flag)


def _answer(project: Project, args: argparse.Namespace) -> int:
    value = _text(args.value, "--value")
    if value == dsl.DEFERRED:
        raise Refused(f"--value: `{dsl.DEFERRED}` is `{PROG} defer`'s, which writes its plan note")
    note = _note_text(args.note, "--note")
    with _locked(project):
        document = _document(project, args.file)
        text = _spliced(
            document,
            lambda text: dsl.write_answer(
                text,
                args.block,
                answer=value,
                by=dsl.AGENT,
                at=datetime.now(UTC),
                via=dsl.AnswerChannel.APP,
                note=note,
            ),
        )
        _not_a_persons(document.block(args.block))
        _validated(project, document, text)
        _write(document.path, text)
    print(f"block {args.block} of {document.relative} answered: {value}")
    return _check_written(project, [document.path])


def _done(project: Project, args: argparse.Namespace) -> int:
    note = _note_text(args.note, "--note")
    with _locked(project):
        document = _document(project, args.file)
        at = datetime.now(UTC)
        text = _spliced(
            document,
            lambda text: dsl.write_done(text, args.block, by=dsl.AGENT, at=at, note=note),
        )
        block = document.block(args.block)
        _not_a_persons(block)
        if block.kind is not dsl.BlockKind.ACTION:
            raise Refused(f"<block id>: block {block.local_id} is a {block.kind}, not an action")
        claimed = block.answer == CLAIM and block.by == dsl.AGENT and block.done is None
        if block.answered and not claimed:
            raise Refused(
                f"<block id>: action {block.local_id} holds {_answer_line(block)}: `done` takes"
                f" an action Pilot claimed (`answer: {CLAIM}`, `by: agent`) or one with no answer"
            )
        if block.options and not claimed:
            raise Refused(
                f"<block id>: action {block.local_id} has options:"
                f" it is answered with one of them (`{PROG} answer`)"
            )
        _validated(project, document, text)
        _write(document.path, text)
    print(f"action {block.local_id} of {document.relative} done at {_utc(at)}")
    return _check_written(project, [document.path])


def _defer(project: Project, args: argparse.Namespace) -> int:
    to = _text(args.to, "--to")
    summary = _text(args.summary, "--summary")
    content = summary if args.content is None else _text(_stdin_or(args.content), "--content")
    note = None if args.note is None else _text(args.note, "--note")
    plan_path = project.folder / PLAN
    with _locked(project):
        document = _document(project, args.file)
        if document.item is None:
            raise Refused(
                f"<file>: {DRAFT} is the draft, whose blocks no plan note may name (D001)"
            )
        plan = _read_plan(project)
        task = None if to == dsl.PLAN else next((t for t in plan["tasks"] if t["id"] == to), None)
        if to != dsl.PLAN and task is None:
            raise Refused(f"--to: `{to}` names neither `{dsl.PLAN}` nor a task in the plan")
        at = datetime.now(UTC)
        text = _spliced(
            document,
            lambda text: dsl.write_answer(
                text,
                args.block,
                answer=dsl.DEFERRED,
                by=dsl.AGENT,
                at=at,
                via=dsl.AnswerChannel.APP,
                note=note,
                to=to,
            ),
        )
        _not_a_persons(document.block(args.block))
        _validated(project, document, text)
        ref = f"{document.item['id']}/{args.block}"
        owner = plan["notes"] if task is None else task["notes"]
        note_id = _new_note(plan, owner, summary, content, [ref], at)
        # The note first, so that a failure between the two writes never
        # leaves a deferral without its note.
        _write(plan_path, _render_plan(plan))
        _write(document.path, text)
    on = "the plan" if to == dsl.PLAN else f"task {to}"
    print(f"note {note_id} added on {on}, refs {ref}")
    print(f"block {args.block} of {document.relative} deferred to {to}")
    return _check_written(project, [plan_path, document.path])


# -- the parser ----------------------------------------------------------------


def _shape(action: argparse.Action) -> str:
    """An argument as the usage writes it, from its definition."""
    if not action.option_strings:
        return str(action.metavar)
    flag = action.option_strings[-1]
    if action.nargs == 0:
        token = flag
    else:
        metavar = action.metavar or "|".join(str(choice) for choice in action.choices or ())
        token = f"{flag} {metavar}"
    if isinstance(action, argparse._AppendAction):
        return f"[{token}]..."
    return token if action.required else f"[{token}]"


def _usage(parser: argparse.ArgumentParser) -> str:
    """The verb's usage line in its arguments' order of definition, a
    mutually exclusive pair as `[a|b]`."""
    tokens: list[str] = []
    grouped: set[argparse._MutuallyExclusiveGroup] = set()
    for action in parser._actions:
        if isinstance(action, argparse._HelpAction):
            continue
        group = next(
            (g for g in parser._mutually_exclusive_groups if action in g._group_actions),
            None,
        )
        if group is None:
            tokens.append(_shape(action))
        elif group not in grouped:
            grouped.add(group)
            tokens.append("[" + "|".join(_shape(a).strip("[]") for a in group._group_actions) + "]")
    return " ".join([parser.prog, *tokens])


def _leaves(parser: argparse.ArgumentParser) -> Iterator[argparse.ArgumentParser]:
    subparsers = [a for a in parser._actions if isinstance(a, argparse._SubParsersAction)]
    if not subparsers:
        yield parser
        return
    for child in subparsers[0].choices.values():
        yield from _leaves(child)


def usage_text() -> str:
    """Every verb's usage line, each argument's help under it: the block the
    skills quote, rendered from the one parser."""
    parser = build_parser()
    project = next(action for action in parser._actions if action.dest == "project")
    lines = [
        f"{PROG} [--project <folder>] <verb> …",
        f"    --project <folder>: {project.help}",
        (
            "    exit: 0 done, the check names no file written · 1 a Save Error names a file"
            " written · 2 refused, nothing written · 3 not yet checked"
        ),
    ]
    for leaf in _leaves(parser):
        lines.append(leaf.usage or _usage(leaf))
        lines.append(f"    {leaf.description}")
        for action in leaf._actions:
            if action.help and not isinstance(action, argparse._HelpAction):
                name = ", ".join(action.option_strings) or action.metavar
                lines.append(f"    {name}: {action.help}")
    return "\n".join(lines)


class _Parser(argparse.ArgumentParser):
    def format_help(self) -> str:
        if self.prog == PROG:
            return usage_text() + "\n"
        return super().format_help()


def build_parser() -> argparse.ArgumentParser:
    parser = _Parser(prog=PROG, description=__doc__.splitlines()[0])
    parser.add_argument(
        "--project", metavar="<folder>", help="the project's folder; $PILOT_PROJECT when not given"
    )
    verbs = parser.add_subparsers(
        dest="verb", required=True, metavar="<verb>", parser_class=_Parser
    )

    def verb(
        group: Any, name: str, run: Callable[[Project, argparse.Namespace], int], about: str
    ) -> argparse.ArgumentParser:
        sub: argparse.ArgumentParser = group.add_parser(name, description=about, help=about)
        sub.set_defaults(run=run)
        return sub

    file = (
        "file",
        "<file>",
        "the document, items/…, inbox/… or project.md, relative to the folder or absolute",
    )
    block = ("block", "<block id>", "the block's id, as its fence gives it")

    answer = verb(
        verbs, "answer", _answer, "Pilot's answer to a block, `by: agent`, in place of its own"
    )
    for dest, metavar, about in (file, block):
        answer.add_argument(dest, metavar=metavar, help=about)
    answer.add_argument(
        "--value",
        required=True,
        metavar="<text>",
        help="the answer: an option's label, Agree, Yes, No or free words",
    )
    answer.add_argument(
        "--note", metavar="<text>|-", help="why it was given, - to read it from stdin"
    )
    done = verb(
        verbs,
        "done",
        _done,
        f"an action's Done by Pilot, one it claimed (`answer: {CLAIM}`) or one with no answer",
    )
    for dest, metavar, about in (file, block):
        done.add_argument(dest, metavar=metavar, help=about)
    done.add_argument(
        "--note",
        metavar="<text>|-",
        help="the paste-back, what was done and what was seen, - to read it from stdin",
    )
    defer = verb(
        verbs,
        "defer",
        _defer,
        "defer a block to a task or the plan, with its plan note, written first",
    )
    for dest, metavar, about in (file, block):
        defer.add_argument(dest, metavar=metavar, help=about)
    defer.add_argument(
        "--to",
        required=True,
        metavar="<task id|plan>",
        help="a task of the plan, or plan for the project's end",
    )
    defer.add_argument("--summary", required=True, metavar="<line>", help="the plan note's summary")
    defer.add_argument(
        "--content",
        metavar="<text>|-",
        help="the plan note's content, - to read it from stdin; its summary when not given",
    )
    defer.add_argument("--note", metavar="<text>", help="the block's note, why it is deferred")

    check = verb(verbs, "check", _check, "the check alone, for a file written by hand")
    check.add_argument(
        "path", metavar="<path>", help="the file, relative to the project's folder or absolute"
    )

    items = verbs.add_parser("items", help="the timeline's items").add_subparsers(
        dest="items_verb", required=True, metavar="<verb>"
    )
    listing = verb(
        items, "list", _items_list, f"the timeline's items, one line each, from {TIMELINE}"
    )
    listing.add_argument("--open", action="store_true", help="only the items not done")
    listing.add_argument(
        "--kind", metavar="<code>", help=f"only the items of this kind, a code of {REFERENCE}"
    )
    show = verb(
        items,
        "show",
        _items_show,
        "the item's line and, for a document, its blocks with their answer lines",
    )
    show.add_argument(
        "item", metavar="<id|path>", help=f"the item's id, or its document's path, from {TIMELINE}"
    )

    plan = verbs.add_parser("plan", help=f"the plan, {PLAN}").add_subparsers(
        dest="plan_verb", required=True, metavar="<verb>"
    )
    task = plan.add_parser("task", help="the plan's tasks").add_subparsers(
        dest="task_verb", required=True, metavar="<verb>"
    )
    add = verb(task, "add", _task_add, "add a task to the plan, last unless placed")
    add.add_argument("--id", required=True, metavar="<id>", help="the task's id, new to the plan")
    add.add_argument("--title", required=True, metavar="<text>", help="the task's title")
    add.add_argument(
        "--status", choices=TASK_STATUSES, default="pending", help="pending when not given"
    )
    place = add.add_mutually_exclusive_group()
    place.add_argument("--before", metavar="<id>", help="placed before this task")
    place.add_argument("--after", metavar="<id>", help="placed after this task")
    sets = verb(task, "set", _task_set, "change a task's title, status or both")
    sets.add_argument("id", metavar="<id>", help="the task")
    sets.add_argument("--title", metavar="<text>", help="its new title")
    sets.add_argument("--status", choices=TASK_STATUSES, help="its new status")
    remove = verb(
        task, "remove", _task_remove, "remove a task from the plan, refused while it has open notes"
    )
    remove.add_argument("id", metavar="<id>", help="the task")
    verb(task, "list", _task_list, "the plan's tasks in order, with their open notes' ids")

    note = plan.add_parser("note", help="the plan's notes").add_subparsers(
        dest="note_verb", required=True, metavar="<verb>"
    )
    note_add = verb(
        note, "add", _note_add, "add a note on a task or on the plan; its id is the next n<number>"
    )
    note_add.add_argument(
        "--task", metavar="<id>", help="the task the note is on; the plan's own when not given"
    )
    note_add.add_argument("--summary", required=True, metavar="<line>", help="the note's summary")
    note_add.add_argument(
        "--ref",
        action="append",
        default=[],
        metavar="<block id>",
        help=f"a block the note is about, `<item id>/<local id>`, the item's id from {TIMELINE}",
    )
    note_add.add_argument(
        "content", metavar="<content|->", help="the note's content, - to read it from stdin"
    )
    strike = verb(note, "strike", _note_strike, "strike an open note")
    strike.add_argument("id", metavar="<id>", help="the note")
    note_list = verb(
        note, "list", _note_list, "the open notes, each with its refs' blocks as they stand"
    )
    note_list.add_argument("--task", metavar="<id>", help="only the notes on this task")

    plan_set = verb(plan, "set", _plan_set, "set or clear the plan's ticket and repo")
    ticket = plan_set.add_mutually_exclusive_group()
    ticket.add_argument("--ticket", metavar="<id>", help="the ticket the work is tracked on")
    ticket.add_argument("--no-ticket", action="store_true", help="no ticket")
    repo = plan_set.add_mutually_exclusive_group()
    repo.add_argument("--repo", metavar="owner/Name", help="the repository the work is in")
    repo.add_argument("--no-repo", action="store_true", help="no repository")

    for leaf in _leaves(parser):
        leaf.usage = _usage(leaf)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return int(args.run(_project(args.project), args))
    except Refused as refusal:
        print(f"{PROG}: refused: {refusal}", file=sys.stderr)
        return REFUSED


if __name__ == "__main__":
    sys.exit(main())
