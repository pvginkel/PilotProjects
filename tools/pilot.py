#!/usr/bin/env python3
"""Pilot's editing scripts over one project's folder of the store's tree.

Design 3 §7. One verb per intent, on the folder `$PILOT_PROJECT` names, or
`--project`. A refusal goes to stderr, naming the flag or the rule, exits 2
and writes nothing. Every read-modify-write holds an exclusive flock on the
project folder itself, and every file is replaced whole: written to a
temporary file in its directory, then renamed over it. It calls neither
pilot-sync nor Pilot: the store's hooks hold the tree's write lock around
the Bash call that runs it, and report what the record made of its writes
after that call (.claude/hooks/pilot-sync-lock.py).

Exit codes: 0 done · 2 refused, nothing written.
"""

import argparse
import contextlib
import fcntl
import json
import os
import sys
import tempfile
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
# `timeline.json`'s `project.state` while the project is a draft.
DRAFT_STATE = "draft"
DOCUMENT_FOLDERS = ("items", "inbox")
OPENING = "opening"
# A work item's run as its row in `timeline.json` names it, a job's included, in the row's order
# (PilotApp's engine/views.py, `_run`): a row of any other kind has none of these keys, and neither
# has one rendered before PilotApp put them on a work item's row.
RUN_KEYS = ("repo", "environment", "model", "reasoning_effort", "session")
# What a person's request is called on each kind of wait (PilotApp's F27.3).
REQUESTS = {"card_wait": "Check now", "timed_wait": "Skip wait"}
# The answer of an action Pilot has claimed (F21.6, D062), pilot-dsl's.
CLAIM = dsl.CLAIM
# What `done` takes, as its description and its refusal say it.
DONE_TAKES = (
    f"an action Pilot claimed (`answer: {CLAIM}`, `by: agent`), one Pilot deferred"
    " (`answer: deferred`, `by: agent`) or one with no answer"
)

DONE, REFUSED = 0, 2

# The most words a task's title holds, counted as whitespace separates them: PilotApp's engine
# holds a save of plan.json with a title over it (`TITLE_WORDS`, backend/app/engine/plan.py),
# and its fault states the rule below.
TITLE_WORDS = 25
TITLE_RULE = (
    "a task's title names the task alone; what it waits on, what follows it and the actions"
    " related to it go into a note on the task"
)

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


def _words(value: str, flag: str, stdin: bool) -> str:
    """The words of a note or its content: read from stdin where the verb
    takes `-` for it, then as the record keeps them."""
    return _text(_stdin_or(value) if stdin else value, flag)


# -- the timeline and the documents -------------------------------------------


def _reference(project: Project) -> dict[str, Any]:
    """reference.json at the tree's root, which holds the record's closed lists."""
    reference: dict[str, Any] = _read_json(project.tree / REFERENCE, REFERENCE)
    return reference


def _timeline(project: Project) -> dict[str, Any]:
    timeline: dict[str, Any] = _read_json(project.folder / TIMELINE, "the timeline")
    return timeline


def _parsed(project: Project, item: dict[str, Any]) -> tuple[str, dsl.ParsedDocument] | None:
    """The item's document as it stands on disk, its text and what parses of
    it; none without one."""
    if item["path"] is None:
        return None
    try:
        text = (project.folder / item["path"]).read_text(errors="replace")
    except FileNotFoundError:
        return None
    return text, dsl.parse(text)


def _item(
    project: Project,
    items: list[dict[str, Any]],
    named: str | int,
    what: str,
    *,
    arms: tuple[str, ...] = ("seq", "id", "path"),
    tail: str = "",
) -> dict[str, Any]:
    """The item `named` names, by the arms given: its seq, as decimal digits
    alone (an int is one), else its id, else its document's path. No id or
    path is a bare integer: a seq is the number `items list` prints first.
    Refused naming `what`, the arms the lookup tried and `tail`."""
    found = None
    if "seq" in arms and (isinstance(named, int) or named.isdecimal()):
        said = "the seq"
        found = next((item for item in items if item["seq"] == int(named)), None)
    else:
        said = "the " + " or the ".join(arm for arm in arms if arm != "seq")
        if "id" in arms:
            found = next((item for item in items if item["id"] == named), None)
        if found is None and "path" in arms:
            path = project.file(str(named), what).relative_to(project.folder).as_posix()
            found = next((item for item in items if item["path"] == path), None)
    if found is None:
        raise Refused(f"{what}: no item of {TIMELINE} has {said} {named}{tail}")
    return found


def _block_of(
    project: Project, items: list[dict[str, Any]], ref: str
) -> tuple[dict[str, Any], dsl.ParsedDocument, dsl.Block] | None:
    """The item, document and block a ref names, `<item id>/<block id>`, as
    the folder holds them; none where it names no block of an item's."""
    item_id, _, local_id = ref.partition("/")
    item = next((item for item in items if item["id"] == item_id), None)
    parsed = None if item is None else _parsed(project, item)
    if parsed is None:
        return None
    document = parsed[1]
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


def _is_wait(item: dict[str, Any]) -> bool:
    """A wait is the one item `timeline.json` gives its firings."""
    return "firings" in item


def _wait_parts(item: dict[str, Any]) -> list[str]:
    """A wait's part of its line: what it watches or when it is due, its
    firings counted, and those no run has taken yet among them while it is
    open."""
    if "due_at" in item:
        parts = [f"due {item['due_at']}"]
    else:
        parts = [f"on {', '.join(item['cards'])} for {', '.join(item['states'])}"]
    firings = item["firings"]
    count = f"{len(firings)} firing{'' if len(firings) == 1 else 's'}" if firings else "no firings"
    pending = sum(firing["job"] is None for firing in firings)
    if item["done"] is None and pending:
        count += f", {pending} pending"
    parts.append(count)
    return parts


def _note(item: dict[str, Any]) -> str | None:
    """The words a done item's close holds: a wait's, its `mark`'s, and a
    work item's, Pilot's reason for closing it for good; None on any other."""
    return None if item["done"] is None else item["done"].get("note")


def _firing_line(item: dict[str, Any], firing: dict[str, Any]) -> str:
    """A firing as the wait's run is briefed with it, then the run that took
    it: `firing 1 · <fired at> · RB-12: In Review → Done at <at>, by ada ·
    run <id>`."""
    if firing["cause"] == "transition":
        transition = firing["transition"]
        card = transition["card"]
        moved = card if transition["from"] is None else f"{card}: {transition['from']}"
        what = f"{moved} → {transition['to']} at {transition['at']}"
        if transition["by"] is not None:
            what += f", by {transition['by']}"
    elif firing["cause"] == "requested":
        what = f"the operator's request ({REQUESTS[item['kind']]}), by {firing['requested_by']}"
    else:
        what = f"due {item['due_at']} — fired at its due time"
    if firing["job"] is not None:
        run = f"run {firing['job']}"
    else:
        run = "pending" if item["done"] is None else "no run"
    return f"firing {firing['seq']} · {firing['fired_at']} · {what} · {run}"


def _one_line(text: str) -> str:
    """The words of a note on one line."""
    return " ".join(text.split())


def _field(label: str, text: str, indent: str) -> Iterator[str]:
    """`label: text` on one line, or the label and the text's lines under
    it, indented, where it has more than one."""
    lines = text.splitlines()
    if len(lines) == 1:
        yield f"{indent}{label}: {text}"
        return
    yield f"{indent}{label}:"
    for line in lines:
        yield f"{indent}    {line}"


def _pilots_note(note: dict[str, Any], head: str, indent: str) -> Iterator[str]:
    """A note of Pilot's as `timeline.json` holds it: its head and time,
    then its text and each suggestion and offer it holds, indented under it."""
    yield f"{indent}{head} · {note['at']}"
    inner = indent + "    "
    if note["text"] is not None:
        for line in note["text"].splitlines():
            yield f"{inner}{line}"
    if note["suggested_answer"] is not None:
        yield from _field("suggested answer", note["suggested_answer"], inner)
    if note["suggested_note"] is not None:
        yield from _field("suggested note", note["suggested_note"], inner)
    if note["offer"] is not None:
        label = "offer, taken" if note["offer_taken"] else "offer"
        yield from _field(label, note["offer"], inner)


def _title_of(item: dict[str, Any], document: dsl.ParsedDocument | None = None) -> str:
    """The item's title, else its document's, else `(no title)`."""
    return item["title"] or (None if document is None else document.title) or "(no title)"


def _item_line(item: dict[str, Any]) -> str:
    parts = [str(item["seq"]), item["kind"], _title_of(item)]
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
    if _is_wait(item):
        parts.extend(_wait_parts(item))
    note = _note(item)
    if note is not None:
        parts.append(f"note: {_one_line(note)}")
    parts.append(item["path"] or "no document")
    parts.append(item["id"])
    return " · ".join(parts)


def _run_line(item: dict[str, Any]) -> str | None:
    """A work item's run, each fact named and `none` where the record holds
    none: `run · repo ada/tide · environment ada-tide-1d6b01 · model opus ·
    reasoning_effort xhigh · session claude-1`; None for a row without them."""
    if not all(key in item for key in RUN_KEYS):
        return None
    facts = (f"{key} {'none' if item[key] is None else item[key]}" for key in RUN_KEYS)
    return " · ".join(("run", *facts))


def _items_list(project: Project, args: argparse.Namespace) -> int:
    items = _timeline(project)["items"]
    if args.kind is not None:
        codes = [kind["code"] for kind in _reference(project)["item_kinds"]]
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
    return _show(project, _item(project, items, args.item, "<id|path|seq>"))


def _show(project: Project, item: dict[str, Any]) -> int:
    print(_item_line(item))
    run = _run_line(item)
    if run is not None:
        print(run)
    if item["summary"] is not None:
        print(f"summary: {item['summary']}")
    if _is_wait(item):
        for firing in item["firings"]:
            print(_firing_line(item, firing))
    note = _note(item)
    if note is not None and note != _one_line(note):
        print("note:")
        for line in note.splitlines():
            print(f"    {line}")
    # Only a prose item's row carries `notes` and `alert` (F74.2).
    notes = {standing["block"]: standing for standing in item.get("notes", [])}
    if None in notes:
        for line in _pilots_note(notes.pop(None), "Pilot's note on the item", ""):
            print(line)
    alert = item.get("alert")
    if alert is not None:
        print(f"Pilot's alert · {alert['at']} · awaits {alert['awaits']}")
        for line in alert["text"].splitlines():
            print(f"    {line}")
    parsed = _parsed(project, item)
    if item["path"] is not None and parsed is None:
        print(f"its document {item['path']} is not on disk")
    blocks = [] if parsed is None else parsed[1].blocks
    lines = [] if parsed is None else parsed[0].splitlines()
    for block in blocks:
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
        if block.local_id in notes:
            for line in _pilots_note(notes.pop(block.local_id), "Pilot's note", "    "):
                print(line)
    # The notes on blocks the file on disk does not hold, all of them where it is not on disk.
    for local_id, standing in notes.items():
        for line in _pilots_note(standing, f"Pilot's note on {local_id}", ""):
            print(line)
    return DONE


def _items_get(project: Project, args: argparse.Namespace) -> int:
    items = _timeline(project)["items"]
    item = _item(project, items, args.seq, "<seq>", arms=("seq",))
    print(json.dumps(item, indent=2, ensure_ascii=False))
    return DONE


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


def _task(plan: dict[str, Any], task_id: str, flag: str, said: str | None = None) -> dict[str, Any]:
    """The plan's task, refused as `said` where the verb words it itself."""
    task = next((task for task in plan["tasks"] if task["id"] == task_id), None)
    if task is None:
        raise Refused(said or f"{flag}: the plan has no task `{task_id}`")
    return task


def _home(
    plan: dict[str, Any], task_id: str | None, flag: str, said: str | None = None
) -> tuple[list[dict[str, Any]], str]:
    """Where a note lives, the plan's own notes where no task is named and
    else that task's, with the words that say so."""
    if task_id is None:
        return plan["notes"], "the plan"
    return _task(plan, task_id, flag, said)["notes"], f"task {task_id}"


def _all_notes(plan: dict[str, Any]) -> Iterator[tuple[dict[str, Any] | None, dict[str, Any]]]:
    """Every open note with its task, none for the plan's own."""
    for task in plan["tasks"]:
        for note in task["notes"]:
            yield task, note
    for note in plan["notes"]:
        yield None, note


def _edit_plan(project: Project, edit: Callable[[dict[str, Any]], str]) -> int:
    """Read plan.json, apply `edit`, which refuses or says what it did,
    write the plan back canonical, and say what it did."""
    path = project.folder / PLAN
    with _locked(project):
        plan = _read_plan(project)
        done = edit(plan)
        _write(path, _render_plan(plan))
    print(done)
    return DONE


def _title(value: str) -> str:
    """A task's title as the record keeps it, refused over its words as the
    engine holds the save."""
    title = _text(value, "--title")
    if len(words := title.split()) > TITLE_WORDS:
        raise Refused(
            f"--title: {len(words)} words, over {TITLE_WORDS}: {TITLE_RULE}"
            f" (`{PROG} plan note add --task <task id>`)"
        )
    return title


def _task_add(project: Project, args: argparse.Namespace) -> int:
    def edit(plan: dict[str, Any]) -> str:
        task_id = _text(args.id, "--id")
        if any(task["id"] == task_id for task in plan["tasks"]):
            raise Refused(f"--id: the plan has a task `{task_id}` already")
        title = _title(args.title)
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


def _task_move(project: Project, args: argparse.Namespace) -> int:
    def edit(plan: dict[str, Any]) -> str:
        task = _task(plan, args.id, "<task id>")
        flag, other_id = ("--before", args.before) if args.before is not None else (
            "--after",
            args.after,
        )
        other = _task(plan, other_id, flag)
        if other is task:
            raise Refused(f"{flag}: a task is not placed {flag[2:]} itself, `{task['id']}`")
        tasks = plan["tasks"]
        tasks.remove(task)
        index = tasks.index(other) + (flag == "--after")
        tasks.insert(index, task)
        return f"task {task['id']} moved, {flag[2:]} {other_id}: {task['title']} ({task['status']})"

    return _edit_plan(project, edit)


def _task_set(project: Project, args: argparse.Namespace) -> int:
    def edit(plan: dict[str, Any]) -> str:
        if args.title is None and args.status is None:
            raise Refused("--title, --status: nothing to set; give one or both")
        task = _task(plan, args.id, "<task id>")
        if args.title is not None:
            task["title"] = _title(args.title)
        if args.status is not None:
            task["status"] = args.status
        return f"task {task['id']}: {task['title']} ({task['status']})"

    return _edit_plan(project, edit)


def _task_remove(project: Project, args: argparse.Namespace) -> int:
    def edit(plan: dict[str, Any]) -> str:
        task = _task(plan, args.id, "<task id>")
        if task["notes"]:
            notes = ", ".join(f"`{note['id']}`" for note in task["notes"])
            raise Refused(
                f"<task id>: task `{task['id']}` has the open notes {notes}: strike them first"
                f" (`{PROG} plan note strike <note id>`), or move them to another task in {PLAN}"
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
    content = _words(args.content, "<text>|-", True)

    def edit(plan: dict[str, Any]) -> str:
        owner, on = _home(plan, args.task, "--task")
        refs = list(dict.fromkeys(ref.strip() for ref in args.ref))
        items = _timeline(project)["items"] if refs else []
        for ref in refs:
            if _block_of(project, items, ref) is None:
                raise Refused(
                    f"--ref: `{ref}` names no block of this project's items"
                    f" (`<item id>/<block id>`, the item's id from {TIMELINE})"
                )
        summary = _text(args.summary, "--summary")
        note_id = _new_note(plan, owner, summary, content, refs, datetime.now(UTC))
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
            raise Refused(f"<note id>: the plan has no open note `{args.id}`")
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
    items = _timeline(project)["items"] if any(note["refs"] for _, note in notes) else []
    for task, note in notes:
        print(f"{note['id']} · {'plan' if task is None else task['id']} · {note['summary']}")
        for line in (note["content"] or "").splitlines():
            print(f"    {line}")
        for ref in note["refs"]:
            found = _block_of(project, items, ref)
            if found is None:
                print(f"    {ref} · no block of this project's items")
                continue
            item, document, block = found
            print(f"    {ref} · {_title_of(item, document)} · {_answer_line(block)}")
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
    it is, none for `project.md`, and whether its project is a draft."""

    path: Path
    relative: str
    item: dict[str, Any] | None
    draft: bool
    text: str
    parsed: dsl.ParsedDocument

    @property
    def kind(self) -> dsl.DocumentKind:
        """What the engine ingests the file as (PilotApp's engine/ingest.py):
        `project.md` the draft while its project is one, and past Create
        project the handbook's kind, which reads no `slug`."""
        if self.item is None:
            return dsl.DocumentKind.DRAFT if self.draft else dsl.DocumentKind.HANDBOOK
        if self.item["kind"] == OPENING:
            return dsl.DocumentKind.OPENING
        if self.relative.startswith("inbox/"):
            return dsl.DocumentKind.REGISTERED_ITEM
        return dsl.DocumentKind.OWN_ITEM

    def block(self, local_id: str) -> dsl.Block:
        return next(block for block in self.parsed.blocks if block.local_id == local_id)


def _document(project: Project, name: str) -> _Document:
    """The document `<file>` names, read whole: `project.md`, or an item's
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
    timeline = _timeline(project)
    item = None
    if relative != DRAFT:
        item = _item(
            project,
            timeline["items"],
            relative,
            "<file>",
            arms=("path",),
            tail="; an item's file is born through `add_item`",
        )
    try:
        text: str | None = path.read_bytes().decode()
    except UnicodeDecodeError:
        text = None
    if text is None or "\x00" in text:
        raise Refused(
            f"<file>: {relative} is not UTF-8 text, or holds a NUL: the engine would hold the write"
        )
    draft = timeline["project"]["state"] == DRAFT_STATE
    return _Document(path, relative, item, draft, text, dsl.parse(text))


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


def _validated(project: Project, document: _Document, text: str, plan: dict[str, Any]) -> None:
    """`validate()` on the text to write, with the facts the tree carries:
    the confirmation reasons, the plan's live tasks, the `to`s the file has.
    It carries no handle and no removed task, so the rules resting on them
    are left to the check after the Bash call that runs the verb."""
    reasons = _reference(project)["confirmation_reasons"]
    facts = dsl.Facts(
        document=document.kind,
        handles=None,
        plan_task_ids={task["id"] for task in plan["tasks"]},
        removed_task_ids=None,
        confirmation_reasons=[reason["code"] for reason in reasons],
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


def _opened(
    document: _Document, block_id: str, splice: Callable[[str], str]
) -> tuple[str, dsl.Block]:
    """The text to write, the block's lines spliced in, and the block as it
    stands, refused where a person's."""
    text = _spliced(document, splice)
    block = document.block(block_id)
    _not_a_persons(block)
    return text, block


def _agent_answer(
    block_id: str, answer: str, at: datetime, note: str | None, to: str | None = None
) -> Callable[[str], str]:
    """The splice of Pilot's own answer to a block, `by: agent`."""
    return lambda text: dsl.write_answer(
        text,
        block_id,
        answer=answer,
        by=dsl.AGENT,
        at=at,
        via=dsl.AnswerChannel.APP,
        note=note,
        to=to,
    )


def _answer(project: Project, args: argparse.Namespace) -> int:
    value = _text(args.value, "--value")
    if value == dsl.DEFERRED:
        raise Refused(f"--value: `{dsl.DEFERRED}` is `{PROG} defer`'s, which writes its plan note")
    note = None if args.note is None else _words(args.note, "--note", True)
    with _locked(project):
        document = _document(project, args.file)
        text, _ = _opened(
            document, args.block, _agent_answer(args.block, value, datetime.now(UTC), note)
        )
        _validated(project, document, text, _read_plan(project))
        _write(document.path, text)
    print(f"block {args.block} of {document.relative} answered: {value}")
    return DONE


def _done(project: Project, args: argparse.Namespace) -> int:
    note = None if args.note is None else _words(args.note, "--note", True)
    with _locked(project):
        document = _document(project, args.file)
        at = datetime.now(UTC)
        text, block = _opened(
            document,
            args.block,
            lambda text: dsl.write_done(text, args.block, by=dsl.AGENT, at=at, note=note),
        )
        if block.kind is not dsl.BlockKind.ACTION:
            raise Refused(f"<block id>: block {block.local_id} is a {block.kind}, not an action")
        # An action Pilot claimed, or deferred itself (`by: agent`, the record's to the
        # work that did it), takes the work's done; its deferral's plan note stays.
        taken = block.claimed or (block.answer == dsl.DEFERRED and block.by == dsl.AGENT)
        if block.answered and not taken:
            raise Refused(
                f"<block id>: action {block.local_id} holds {_answer_line(block)}:"
                f" `done` takes {DONE_TAKES}"
            )
        if block.options and not taken:
            raise Refused(
                f"<block id>: action {block.local_id} has options:"
                f" it is answered with one of them (`{PROG} answer`)"
            )
        _validated(project, document, text, _read_plan(project))
        _write(document.path, text)
    print(f"action {block.local_id} of {document.relative} done at {_utc(at)}")
    return DONE


def _defer(project: Project, args: argparse.Namespace) -> int:
    to = _text(args.to, "--to")
    summary = _text(args.summary, "--summary")
    content = summary if args.content is None else _words(args.content, "--content", True)
    note = None if args.note is None else _words(args.note, "--note", False)
    plan_path = project.folder / PLAN
    with _locked(project):
        document = _document(project, args.file)
        if document.item is None:
            what = "the draft" if document.draft else "the project document"
            raise Refused(f"<file>: {DRAFT} is {what}, whose blocks no plan note may name (D001)")
        plan = _read_plan(project)
        owner, on = _home(
            plan,
            None if to == dsl.PLAN else to,
            "--to",
            f"--to: `{to}` names neither `{dsl.PLAN}` nor a task in the plan",
        )
        at = datetime.now(UTC)
        text, _ = _opened(
            document, args.block, _agent_answer(args.block, dsl.DEFERRED, at, note, to)
        )
        _validated(project, document, text, plan)
        ref = f"{document.item['id']}/{args.block}"
        note_id = _new_note(plan, owner, summary, content, [ref], at)
        # The note first, so that a failure between the two writes never
        # leaves a deferral without its note.
        _write(plan_path, _render_plan(plan))
        _write(document.path, text)
    print(f"note {note_id} added on {on}, refs {ref}")
    print(f"block {args.block} of {document.relative} deferred to {to}")
    return DONE


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
    mutually exclusive pair as `[a|b]`, or `a|b` where one is required."""
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
            pair = "|".join(_shape(a).strip("[]") for a in group._group_actions)
            tokens.append(pair if group.required else f"[{pair}]")
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
        "    exit: 0 done · 2 refused, nothing written",
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
        help=f"the answer: an option's label, Agree, Yes, No or free words; `{CLAIM}` is the claim of"
        " an action Pilot does",
    )
    answer.add_argument(
        "--note", metavar="<text>|-", help="why it was given, - to read it from stdin"
    )
    done = verb(
        verbs,
        "done",
        _done,
        f"an action's Done by Pilot, which takes {DONE_TAKES}",
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
        "the item's line; a work item's run on a line under it, its repo, environment id, model,"
        " reasoning_effort and controller session, none where timeline.json holds none; its"
        " summary, its file's blocks with their answer lines and Pilot's notes under them, Pilot's"
        " note on the item and its alert, a wait's firings, a done item's note",
    )
    show.add_argument(
        "item",
        metavar="<id|path|seq>",
        help="the item's id, its document's path or its seq, as `items list` prints them",
    )
    get = verb(
        items,
        "get",
        _items_get,
        f"the item's fields as {TIMELINE} has them, by its number on the timeline, its seq",
    )
    get.add_argument(
        "seq", type=int, metavar="<seq>", help=f"the item's number on the timeline, from {TIMELINE}"
    )

    plan = verbs.add_parser("plan", help=f"the plan, {PLAN}").add_subparsers(
        dest="plan_verb", required=True, metavar="<verb>"
    )
    task = plan.add_parser("task", help="the plan's tasks").add_subparsers(
        dest="task_verb", required=True, metavar="<verb>"
    )
    add = verb(task, "add", _task_add, "add a task to the plan, last unless placed")
    add.add_argument(
        "--id", required=True, metavar="<task id>", help="the task's id, new to the plan"
    )
    add.add_argument(
        "--title",
        required=True,
        metavar="<text>",
        help=f"the task's title, the task alone in {TITLE_WORDS} words at most: what it waits on,"
        " what follows it and the actions related to it go into a note on it, `plan note add`",
    )
    add.add_argument(
        "--status", choices=TASK_STATUSES, default="pending", help="pending when not given"
    )
    place = add.add_mutually_exclusive_group()
    place.add_argument("--before", metavar="<task id>", help="placed before this task")
    place.add_argument("--after", metavar="<task id>", help="placed after this task")
    sets = verb(task, "set", _task_set, "change a task's title, status or both")
    sets.add_argument("id", metavar="<task id>", help="the task")
    sets.add_argument(
        "--title",
        metavar="<text>",
        help=f"its new title, the task alone in {TITLE_WORDS} words at most, as `plan task add`"
        " has it",
    )
    sets.add_argument("--status", choices=TASK_STATUSES, help="its new status")
    remove = verb(
        task, "remove", _task_remove, "remove a task from the plan, refused while it has open notes"
    )
    remove.add_argument("id", metavar="<task id>", help="the task")
    move = verb(task, "move", _task_move, "move a task before or after another")
    move.add_argument("id", metavar="<task id>", help="the task to move")
    to = move.add_mutually_exclusive_group(required=True)
    to.add_argument("--before", metavar="<task id>", help="placed before this task")
    to.add_argument("--after", metavar="<task id>", help="placed after this task")
    verb(task, "list", _task_list, "the plan's tasks in order, with their open notes' ids")

    note = plan.add_parser("note", help="the plan's notes").add_subparsers(
        dest="note_verb", required=True, metavar="<verb>"
    )
    note_add = verb(
        note, "add", _note_add, "add a note on a task or on the plan; its id is the next n<number>"
    )
    note_add.add_argument(
        "--task", metavar="<task id>", help="the task the note is on; the plan's own when not given"
    )
    note_add.add_argument("--summary", required=True, metavar="<line>", help="the note's summary")
    note_add.add_argument(
        "--ref",
        action="append",
        default=[],
        metavar="<item id>/<block id>",
        help=f"a block the note is about, the item's id from {TIMELINE} and the block's id",
    )
    note_add.add_argument(
        "content", metavar="<text>|-", help="the note's content, - to read it from stdin"
    )
    strike = verb(note, "strike", _note_strike, "strike an open note")
    strike.add_argument("id", metavar="<note id>", help="the note")
    note_list = verb(
        note, "list", _note_list, "the open notes, each with its refs' blocks as they stand"
    )
    note_list.add_argument("--task", metavar="<task id>", help="only the notes on this task")

    plan_set = verb(plan, "set", _plan_set, "set or clear the plan's ticket and repo")
    ticket = plan_set.add_mutually_exclusive_group()
    ticket.add_argument("--ticket", metavar="<ticket>", help="the ticket the work is tracked on")
    ticket.add_argument("--no-ticket", action="store_true", help="no ticket")
    repo = plan_set.add_mutually_exclusive_group()
    repo.add_argument("--repo", metavar="<owner/Name>", help="the repository the work is in")
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
