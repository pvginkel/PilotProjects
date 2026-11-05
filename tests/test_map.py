"""The brain's map as its sessions load it — CLAUDE.md, the rule files and the four skills: each
skill named as its folder and its brief last, the handbook read first, the format skill cited by
its name, pilot.py's verbs as its parser has them, the tool calls the hook locks around, every
pilot.py command line it quotes one the parser takes, every path the map cites in place, the chat
skill and the create skill reading a person's message as PilotApp's server sends it, the create
skill naming a draft's ask and its material as pilot-store takes them, the pre-rule skill reading
the briefs of a worker's turn and of its writer's answer as PilotApp's server writes them and
naming its writes — a claim, a research, a question to the writer and a wait among them — routing
the blocks a research's brief gives and its hand-on to the plan, the plan skill naming each mode by
its brief's kind line, reading the brief of an item done, the claimed actions of a worker's turn
and the brief and the follow-up of a wait's run as the server writes them, a claimed action the
run's or the operator's where the server's reading draws the line, naming its writes and copying
the draft's prose into the handbook without its asks, no file of the map refusing a wait, and a
work item's fields and brief in one rule file the skills starting work cite."""

import importlib.util
import itertools
import json
import os
import re
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / ".claude" / "skills"
CLAUDE = ROOT / "CLAUDE.md"
SKILL_NAMES = {"create", "chat", "pre-rule", "plan"}
FORMAT_SKILL = "/dev:document-format"
BRIEF = "## The brief\n\n$ARGUMENTS"
# A project's folder in the store's tree (PilotApp's docs/projection.md), with chat.md, and the
# tree root's reference.json: the map cites them relative to the folder, never this repo.
TREE_FILES = {
    "project.md",
    "handbook.md",
    "plan.json",
    "timeline.json",
    "chat.md",
    "reference.json",
}
TREE_FOLDERS = ("items/", "inbox/", "attachments/")
PATH_LIKE = re.compile(r"[^\s/]*(/[^\s/]*)*(\.(md|py|json|yaml|toml)|/)")
NOT_IN_REPO = {".git", ".venv", "__pycache__", ".ruff_cache"}
# A fenced block, its fences included: no code span, and its backticks would shift the pairing.
FENCED = re.compile(r"^[ \t]*```.*?^[ \t]*```[^\n]*$", re.MULTILINE | re.DOTALL)
# A person's message as PilotApp's server sends it to the chat (its ChatService and BriefService):
# the line naming its author, a quote's three tags, and the paths a quote by path names.
NAMING_LINE = '"The message, from <handle> (member|not a member):"'
QUOTE_TAGS = (
    '`<quoted_item id="<item id>">…</quoted_item id="<item id>">`',
    '`<quoted_block id="<item id>/<local id>">…</quoted_block id="<item id>/<local id>">`',
    '`<quoted_path path="<path>">…</quoted_path path="<path>">`',
)
QUOTED_PATHS = ("`handbook.md`", "`project.md`", "`attachments/<batch>/<filename>`")
# The server names a message's author only when the message before was another person's, so the
# chat skill takes a message without the line, and a ruling's `for`, from the latest such line.
LATEST_NAMING = (
    "A message without that line is from the person the latest such line named, the brief's"
    " included.",
    f"`for` their handle, as the latest line {NAMING_LINE} names them",
)
# "Is it still going?" answered from the tree, as design 3 §6.3 and §11 and D054 have it: the
# item's line and its session log pointed to, and neither its session's log nor its status read,
# in How work goes and in Grounding alike (P-186).
HOW_WORK_GOES = (
    "say what the tree holds of the work item, open, or done, when and how",
    "point the person to its line and its session log on the timeline",
    "no read of its session's log or its session's status to tell how far it got",
)
LOG_NOT_FOR_HOW_WORK_GOES = "A session's log is never read to tell how work goes"
# What `/plan`'s An item done takes on a person's ruling, which the chat carries out in its own
# turn on a ruling or a close it records on an item of Pilot's own: PilotApp's RecordService
# places no item_done job for a close through the chat (item 173).
RULING_ACTS = (
    "its act, every act it covered — a work item, or your own hands where it is a tool call: a"
    " card, a fleet call",
    "its reason read and the plan adjusted",
    "the plan's next step on it — a task started, changed, added or removed as it rules",
)
# The job after a close ran What is next once it had acted on the close: the chat that carries the
# close out takes it whole, so the task an action item unblocks is started and the plan's end is
# reached with no job after the close.
RULING_THEN_NEXT = (
    "then What is next whole, the task's status set and every task whose inputs are now done"
    " started, up to the plan's end"
)
ITEM_DONE_THEN_NEXT = "Act on the close, then What is next:"
WHAT_IS_NEXT_STEPS = (
    "1. **The task's status**",
    "**Every task whose inputs are done, started**",
    "**The plan's end**",
)
RULING_CARRIED_OUT = (
    "**A ruling or a close you record on an item of Pilot's own**",
    "is carried out in this turn: no job of Pilot's follows what the chat records",
    "what the turn leaves undone waits for Pilot's next job",
    "the finish decision's Yes your `finish`, the turn's last call, after your reply",
)
# Asked about an open block, the chat offers the answer it would record, and it does or offers
# what it can do itself rather than adding an ask item (P-194's chat half).
OFFERED_ANSWER = (
    "**Asked about an open block**, lead with a short answer, then offer the answer you would"
    " record: its option and its note",
    "you do in this turn where the person asked for it, or offer in the reply: never an ask item",
    "Past an offer of either kind, the chat asks no closed question of its own",
)
OFFERED_ANSWER_RETIRED = "you added it. The chat asks no closed question"
# In a draft's definition chat the server's quotes are of the draft alone — an ask of it by
# `project.md/<local id>`, the id pilot-store's `answer` takes for it, or a file by its path — and
# its brief names the person who started the draft, the first message's author unless the line
# names another.
DRAFT_QUOTE_TAGS = (
    '`<quoted_block id="project.md/<local id>">…</quoted_block id="project.md/<local id>">`',
    '`<quoted_path path="<path>">…</quoted_path path="<path>">`',
)
DRAFT_QUOTED_PATHS = ("`project.md`", "`attachments/<batch>/<filename>`")
DRAFT_LATEST_NAMING = (
    "A message without that line is from the person the latest such line named, the brief's"
    " included, and with none so far from the person who started the draft.",
    "`for` their handle, as step 4 names them",
)
# pilot-store's `answer` on a draft's ask and `attach_file` hung on nothing (PilotApp's
# pilot_mcp/tools.py), and the one link the Draft tab opens, relative to the draft's folder.
DRAFT_CALLS = (
    "`answer` with `block` `project.md/<local id>`",
    "`attach_file`: `source` `<environment>:<path>`",
    "and no `to`, so that it hangs on nothing until Create project hangs it on the opening",
    "`[words](attachments/<batch>/<filename>)`, relative to the draft's folder",
)
# What the create skill never does: Create project is the operator's.
CREATE_IS_THE_OPERATORS = (
    "**Create project is the operator's**: never ask for it, and never say the draft is"
    ' "ready".'
)
# The draft's sections the create skill writes and the plan skill's setup reads.
DRAFT_SECTIONS = ("`## The plan`", "`## Rules`", "`## Context`")
SETUP_KIND = "`Pilot's brief · the setup · …`"
# The brief of the job after a worker's turn as PilotApp's BriefService writes it: its kind line, a
# registered document's line in each read state, and a run that registered nothing.
PASS_KIND = "`Pilot's brief · a worker's turn ended · …`"
PASS_DOCUMENT_LINES = (
    "`- <path> (<item id>) — published`",
    "`- <path> (<item id>) — read failed: <reason>`",
    "`Registered nothing this run.`",
)
# The brief of the job after a clarification run's turn, as BriefService writes it: its kind line,
# the run's line, a document asked about, and its last words.
WRITER_ANSWERED_KIND = "`Pilot's brief · the writer answered · …`"
WRITER_ANSWERED_LINES = (
    '`The clarification run: "<title>" (<id>), of the work item "<title>" (<id>)…`',
    "`Asked <stamp> on <path> (<item id>):`",
    "`This pass asks nothing: …`",
)
# pilot-store's ask_writer as it takes its arguments (PilotApp's pilot_mcp/tools.py): the block's
# id names its document.
ASK_WRITER = "`ask_writer` with `block`, `<item id>/<local id>`, and `question`"
# The claim: the block named on the add_item of the work item that does it, then pilot.py's answer
# with the claim's value, pilot.py's CLAIM.
CLAIM_NAMED = "its `claims` the block's id, `<item id>/<local id>`"
# The research: the block left open on a fact named on the add_item of the work item that finds it
# (PilotApp's pilot_mcp/api.py, `researches`), in CLAUDE.md, the routing rule and the pass.
RESEARCH_NAMED = {
    "CLAUDE.md": "`researches` the blocks you left open on a fact it finds",
    "rules/routing.md": "the block named in `researches` on its `add_item`",
    ".claude/skills/pre-rule/SKILL.md": "its `researches` the block's id, `<item id>/<local id>`",
}
# How BriefService ends a claimed or researched block's line once the server's reading handed it
# back to the person (PilotApp's brief_service.py, HANDED_BACK): theirs, never done or routed.
HANDED_BACK = "handed back to the operator: leave it to them"
# The pass's writes and its hand-on: an answer, a deferral with its plan note, an action's Done and
# a claim through pilot.py, a question to the writer and Pilot's own Done through pilot-store, then
# the plan.
PASS_CALLS = (
    "`pilot.py answer <file> <block id>",
    "`pilot.py defer <file> <block id>",
    "`pilot.py done <file> <block id>",
    CLAIM_NAMED,
    ASK_WRITER,
    "`mark`, `item` the document's id, `mark` `done`, and no `for`",
    "run `/plan`, its mode What is next, in this session",
)
# The brief of the job after a person's close of an item of Pilot's own as PilotApp's BriefService
# writes it: its kind line and the item's line.
ITEM_DONE_KIND = "`Pilot's brief · an item of yours is done · …`"
ITEM_DONE_LINE = '`The item: <path> (<item id>), <kind> "<title>"[, task <id>] — <close>.`'
# The plan skill's modes, each a section of its own.
PLAN_MODES = (
    "## The setup",
    "## What is next",
    "## An action of Pilot's done",
    "## An item done",
    "## A wait's firings",
    "## The sweep",
    "## The finish decision",
)
# Pilot's `done` on the last open block of an item of its own is the item's close (PilotApp's
# RecordService.done_by_its_save), with no `mark` after it; an answer of its own closes nothing,
# and a registered document, a worker's, still closes by Pilot's own `mark`.
OWN_ITEM_CLOSED = (
    "an action of an item you added that is done, by a work item's run or your own hands, takes"
    " its `done`",
    "Where that was the item's last open block, every other one answered, deferred or done, that"
    " `done` is the item's close, yours: no `mark` follows it, and the server refuses one",
    "An answer of yours closes nothing",
    "A registered document is a worker's, not yours: its last `done` still takes your own `mark`"
    " with no `for`",
)
# The modes' writes past the setup: a task's status, a note struck, a homeless deferral's note, and
# pilot-store's `finish` on the finish decision's Yes.
PLAN_CALLS = (
    "`pilot.py plan task set <id> --status done`",
    "`pilot.py plan note strike <id>`",
    "`pilot.py plan note add --task <id> --summary <line> --ref <block id> <content>`",
    "the job after its close calls `finish`",
    "`pilot.py done <file> <block id> --note <what was done and what was seen>`",
    "`mark`, `item` the document's id, `mark` `done`, and no `for`",
)
# The claimed actions the brief of a worker's turn names, as BriefService writes them, each open or
# as its close reads.
CLAIMED_ACTIONS = (
    '"The claimed actions given to this work item, as they stand:"',
    (
        "`- <path> (<item id>) <local id>` followed by `open, claimed`, by"
        f" `open, claimed, {HANDED_BACK}`, by `open, its claim gone`, or by its close as it reads"
    ),
)
# A claimed action its run left, refused or not reached, in a turn that registered a document with
# a block in it: the run goes on as a work item titled as it, whose brief names the run's claimed
# actions (PilotApp's D100), so nothing carries them in a note, and nothing retries or hands over an
# act the run still holds.
CLAIM_CARRIED = (
    "After the turn of the work item that continues its run, the brief names the run's claimed"
    " actions as well",
    "**Still the run's**, its act refused or never reached in a turn that registered a document"
    " with a block in it",
    "nothing is written, no note, retry or hand-over",
    "its run waiting on its documents — gets no second",
)
# Where the server's reading hands a claimed action back (PilotApp's working_on.py): left after a
# turn that registered no document with a block in it, it is the person's once the job after that
# turn ends, which retries it or sends the notice; one the brief gives as handed back is theirs, and
# nothing is written of it.
CLAIM_HANDED_BACK = (
    "stays the run's until the job after a turn of it that registered no document with a block in"
    " it ends (never a clarification run's turn, which registers nothing), or its work fails or is"
    " stopped, or a person cancels the run",
    "**Left undone**, its act refused or never reached in a turn that registered no document with"
    " a block in it: the claim stays and the block open, the operator's once this job ends",
    "the operator gets it with the reason: a notice of yours",
    f"**Handed back to the operator** — its line ending `{HANDED_BACK}`",
    "nothing is written, no Done, retry or notice",
)
# The line the plan skill drew before the server read when a run is done with a block.
CLAIM_LINE_RETIRED = (
    "never reached in a turn that registered documents",
    "never reached in a turn that registered nothing",
)
# The blocks the brief of a worker's turn names as researched, as BriefService writes them, and the
# pass's route for each: on the fact found, still the run's while it asks a person first, routed
# without the fact otherwise, and left to the person once handed back.
RESEARCHED_BLOCKS = (
    '"The blocks this work item researched, as they stand:"',
    "`- <path> (<item id>) <local id>` followed by `open`, by"
    f" `open, {HANDED_BACK}`, by `open, claimed`, or by its answer as it reads",
    "the blocks it researched, which are the pass's",
    "After the turn of the work item that continues its run, the brief names the run's researched"
    " blocks as well",
)
RESEARCH_ROUTED = (
    "**Routed**, each `open` one whose fact the run found",
    "**Still the run's**, an `open` one whose fact was not found in a turn that registered a"
    " document with a block in it",
    "**Not found**, an `open` one whose fact was not found in a turn that registered no document"
    " with a block in it",
    f"**Handed back to the operator** — its line ending `{HANDED_BACK}`",
    "**Claimed since, or answered**: settled; leave it.",
)
# The note that carried them before the brief named them.
CLAIM_NOTE = "A note carries them to that turn"
# The words and the sections by which the map refused a wait while pilot-store took none.
WAIT_REFUSALS = ("Pilot takes no waits yet", "refused for now", "## Not yet the", "No wait")
# A wait's two kinds as pilot-store's add_item takes them (PilotApp's pilot_mcp/tools.py), named by
# each skill that adds one, armed as the routing rule arms it: on a fresh read of the card, with a
# backstop where it outlives the plan's horizon.
WAIT_KINDS = ("`card_wait`", "`timed_wait`")
WAIT_ADDING_SKILLS = ("pre-rule", "chat")
WAIT_ARMED = (
    "armed as `rules/routing.md` has it, on a fresh read through youtrack of the card it watches"
)
# A backstop's title, by which a card wait's backstop is told from a timed wait a person asked
# for on the same task.
BACKSTOP_TITLE = "its title `Backstop: <the card wait's title>`"
ROUTING_WAIT = (
    "a wait through `add_item`, armed on a fresh read of the card it watches",
    "a timed wait beside it as a backstop where it outlives the plan's horizon, its `step` the same"
    f" task and {BACKSTOP_TITLE}",
)
# The brief of a wait's run as PilotApp's BriefService writes it: its kind line, the wait's line of
# either kind, its pending firings and each firing's line; then the resumed run's one turn, which
# opens with no slash command and which CLAUDE.md routes.
WAIT_FIRED_KIND = "`Pilot's brief · a wait fired · …`"
WAIT_FIRED_LINES = (
    '`The wait: "<title>" (<id>), a card wait on <cards> for <states>; waiting since <stamp>;'
    " task <id>.`",
    "`a timed wait due <stamp>`",
    "`Firings pending, oldest first:`",
    "`- <stamp> · <card>: <from> → <to>, by <login>`",
    "`- <stamp> · due <stamp> — fired at its due time`",
    "`- <stamp> · the operator's request (Check now), by <handle>`",
    "`(Skip wait)`",
)
WAIT_FOLLOW_UP = '`Another firing of "<title>" since your last run:`'
WAIT_FOLLOW_UP_ROUTED = "`/plan`'s A wait's firings again"
# Design 3 §6.5's wait's firings: each judged, the card read again before any act, the wait closed
# through `mark` with its note or left open, and the backstop; a card wait and its backstop, paired
# by their task and told from a person's timed wait by the backstop's title, closed together
# whichever fired, and a backstop spent at its due time counted for none (P-176).
WAIT_FIRINGS = (
    "**Its pair**, a card wait and its backstop, found by the task they share",
    "A card wait's backstop is the open timed wait on its task titled as one,"
    " `Backstop: <the card wait's title>`",
    "A timed wait a person asked for on the same task is titled otherwise: it is no backstop",
    "**Each firing judged** against what the wait waits for",
    "but a backstop's, a read on demand of its card wait's card",
    "the operator's request is a read on demand",
    "**The card read again** through youtrack before any act",
    "**Over**, its event come: the action after it started",
    "`mark`, `item` the wait's id, `mark` `done`, no `for`, and `note` what was read and when and"
    " the action started",
    "A card wait and its backstop close together, whichever fired",
    "**Not over**: the wait left open",
    "its backstop closed with it",
    "a card wait that outlives the plan's horizon takes a timed wait beside it, its `step` the same"
    f" task and {BACKSTOP_TITLE}, where it has none open that has not fired at its due time",
    "A backstop that fired at its due time on an event not come is spent",
)
# The words by which the backstop counted an open timed wait that had fired as the card wait's.
WAIT_FIRINGS_RETIRED = ("where it has none open (",)
# What the operator reads first (the operator's "In full" on session review 2's change 5,
# 2026-11-04): an answer's note, where the due diligence's findings go, a notice, an item's lead.
NOTE_RULE = (
    'at most two sentences, the choice and its one reason, with no "Checked:" and no bare ids'
)
NOTE_RULE_FILES = (
    ".claude/skills/pre-rule/SKILL.md",
    ".claude/skills/plan/SKILL.md",
    "rules/routing.md",
)
FINDINGS_LOGGED = "goes to the session log"
NOTICE_RULE = "A notice is posted only for what the operator must know or do"
ITEM_LEAD = "An item's heading and first paragraph carry its ruling in about 60 words"
NOTICE_SKILLS = ("pre-rule", "plan")
# A notice the pass posts on a block left to the operator (P-194's pre-rule half).
NOTICE_SUGGESTS = "ending with the answer you suggest and the note for it"
# The operator's rule of 2026-11-01, that the note named what was checked and found.
FINDINGS_IN_NOTE = (
    "names what was checked and what was found",
    "the note saying what was checked",
    "the note naming what was found",
    "the note saying the fact stayed unread",
    "the note saying so",
)
# The setup's handbook: the draft's prose without its asks' blocks, a ruled ask's outcome a rule
# line, and the report after the write read for what it says of the handbook.
SETUP_HANDBOOK = (
    "the prose of the draft's `## Rules` and `## Context`, copied, and never an ask's block",
    "an ask fenced there stays in `project.md`",
    "a ruled ask's outcome as a plain rule line",
    "that the write landed is not enough",
)
# A work item's add_item fields and its brief, at home in one rule file that the skills starting
# work cite and none copies.
WORK_ITEMS = "rules/work-items.md"
WORK_ITEM_FIELDS = (
    "`kind` `work`",
    "`title`",
    "`repo`",
    "`cwd`",
    "`model`",
    "`reasoning_effort`",
    "`step`",
    "`attachments`",
    "`brief`",
)
WORK_ITEM_BRIEF = (
    "The task in a line.",
    "copied verbatim from `rules/grants.md`'s \"In a worker's brief\"",
    "never paste the handbook",
)
WORK_ITEM_SKILLS = ("chat", "plan", "pre-rule")
# A promotion's procedure, at home in one rule file whose text a promotion's brief carries, as it
# carries the grants, since the worker runs outside the store (P-184): the job and its parameter,
# the wait on the build, production read through `cexec iac`, and what else is running, Pilot's.
PROMOTE = "rules/promote.md"
PROMOTE_SECTION = "## In a promotion's brief"
PROMOTE_TEXT = (
    "`<App>/Promote-PRD`, in its Jenkins folder beside its build job, `<App>/Build-Main`",
    "`Jenkinsfile.promote` in the application's deploy repository, whose header names the job on"
    " its `Job:` line and says what each parameter takes",
    "PilotApp's is `PilotApp/Promote-PRD`, in PilotDeploy, with one parameter, `commit`",
    "`timeout 1800 track_build.py <App>/Build-Main --hash <the application's commit> --diagnose`",
    "`timeout 1800 track_build.py <App>/Promote-PRD --buildnr <n> --diagnose`",
    "kubectl runs in the `iac` tool container, `cexec iac kubectl …`",
    "that check is Pilot's, never yours: a session you see running holds nothing",
)
PROMOTE_BRIEF = (
    "For a promotion to production, the text of `rules/promote.md`'s \"In a promotion's brief\","
    " copied verbatim"
)
# A close-out's promotion deferred to the run's own task, never claimed, with what the close-out
# owes after it, so that the close-out closes on its other blocks and the continuation goes on;
# the promotion due once that continuation has ended, so that it takes its fixes (P-183, D2).
PROMOTION_ROUTED = (
    "| a close-out's promotion Pilot may run under the grants, with the update that follows it",
    "every action the close-out owes after the promotion — a criterion's `Settle <id> after …`",
    "deferred to the running task, never claimed: each through `pilot.py defer`, `--to` the run's"
    " own task, so that the close-out closes once its other blocks are answered and the run's"
    " continuation goes on",
    "| the run's end: a close-out's promotion and what follows it | a note on the running task, due"
    " once the run's continuation has ended |",
    "A close-out's promotion is the one exception (below): the event it waits on is the end of the"
    " run's continuation, whose turn a job of Pilot's follows",
    "A deferral from a close-out, the task's last document, goes to the next task or to the end, but"
    " for its promotion: the promotion, the update that follows it and every action the close-out"
    " owes after it go to the running task, so that the promotion takes the fixes of the run's"
    " continuation",
    "They are due once that continuation has ended, the work item that continues the run done after"
    " a turn that registered no document with a block in it; until then their notes stand",
)
# The rule's words while a close-out's promotion was claimed and its deferral barred the run.
PROMOTION_ROUTED_RETIRED = ("goes to the next task or to the end, never to the running task",)
PROMOTION_DEFERRED = (
    "a close-out's promotion aside, which is deferred",
    "A close-out's promotion, the update that follows it and every action the close-out owes after"
    " it are deferred so, `--to` the run's own task, never claimed",
)
PROMOTION_DUE = (
    "**A close-out's promotion**, deferred to the run's own task with the update that follows it"
    " and every action the close-out owes after it",
    "is met only once the run's continuation has ended, the work item that continues the run done"
    " after a turn that registered no document with a block in it: until then its notes stand,"
    " neither acted on nor struck",
    "one work item does them all, its `step` the run's task, the promotion first, its brief"
    " carrying `rules/promote.md`",
    "and naming the application's commit read then, its `main` as the continuation left it, never"
    " the commit or the build the close-out's block names, which predate the continuation's fixes",
)
# A placed worker's model and effort: Opus at xhigh unless the handbook or the task names another,
# in the placement rule and in the work item's field line.
PLACEMENT = "rules/placement.md"
PLACEMENT_DEFAULTS = (
    "`model` is `opus` and `reasoning_effort` is `xhigh`",
    "unless the handbook or the task names another model or level",
)
WORK_ITEM_DEFAULTS = (
    "`model` and `reasoning_effort` as `rules/placement.md` says, `opus` and `xhigh` unless the"
    " handbook or the task names another"
)
# The rule's words while the effort was left unset and the stage could name a model.
PLACEMENT_RETIRED = ("left unset", "the stage")


def skill_file(name: str) -> Path:
    return SKILLS / name / "SKILL.md"


def the_map() -> dict[str, str]:
    files = [CLAUDE, *sorted((ROOT / "rules").glob("*.md"))]
    files += [skill_file(name) for name in sorted(SKILL_NAMES)]
    return {str(path.relative_to(ROOT)): path.read_text() for path in files}


def front_matter(text: str) -> tuple[dict, str]:
    head, separator, body = text.removeprefix("---\n").partition("\n---\n")
    if not text.startswith("---\n") or not separator:
        raise AssertionError("no front matter")
    return yaml.safe_load(head), body


def code_spans(text: str) -> list[str]:
    return re.findall(r"`([^`]+)`", FENCED.sub("", text))


def cited_paths(text: str) -> list[str]:
    """Every path-like word of the text's code spans, outside its fenced blocks: a file name
    with an extension, or a folder ending in a slash."""
    words = (word for span in code_spans(text) for word in span.split())
    return [word for word in words if PATH_LIKE.fullmatch(word)]


def quoted_commands(text: str) -> list[str]:
    """Every code span of the text, outside its fenced blocks, that is a pilot.py command line."""
    return [span for span in code_spans(text) if span.startswith("pilot.py ")]


def repo_names() -> set[str]:
    names: set[str] = set()
    for _, folders, files in os.walk(ROOT):
        folders[:] = [folder for folder in folders if folder not in NOT_IN_REPO]
        names.update(files)
    return names


def is_there(path: str, names: set[str]) -> bool:
    """A cited path is a file or a folder of a project's folder, absolute and so outside this
    repo, a file name this repo holds somewhere, or a path from its root, `<…>` any one name."""
    if path.startswith("/") or path in TREE_FILES or path.startswith(TREE_FOLDERS):
        return True
    if "/" not in path.rstrip("/"):
        return path in names or (ROOT / path).is_dir()
    return any(ROOT.glob(re.sub(r"<[^>]*>", "*", path.rstrip("/"))))


def first_step(body: str) -> str:
    match = re.search(r"^1\. (.+?)(?=\n\S|\n\n|\Z)", body, re.MULTILINE | re.DOTALL)
    if match is None:
        raise AssertionError("no numbered step")
    return match.group(1)


def pilot_module():
    spec = importlib.util.spec_from_file_location("pilot", ROOT / "tools" / "pilot.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def pilot_verbs() -> dict[str, str]:
    module = pilot_module()
    return {leaf.prog: leaf.description for leaf in module._leaves(module.build_parser())}


def pilot_options() -> dict[str, set[str]]:
    """The options each verb's parser takes, by its prog, and the script's own, `pilot.py`'s."""
    module = pilot_module()
    root = module.build_parser()
    parsers = [root, *module._leaves(root)]
    return {parser.prog: set(parser._option_string_actions) for parser in parsers}


def command_fault(command: str, options: dict[str, set[str]]) -> str | None:
    """Why a quoted pilot.py command line is not one its parser takes — a word after the
    script's name that is no verb of it, or an option its verb does not have; None for one it
    takes. A word after the verb is an option, `--…`, or a placeholder, `<…>`."""
    words = command.split()
    verb = max((prog for prog in options if words[: len(prog.split())] == prog.split()), key=len)
    rest = words[len(verb.split()) :]
    named = list(itertools.takewhile(lambda word: not word.startswith(("-", "<")), rest))
    if named:
        return f"`{verb}` has no verb `{' '.join(named)}`"
    unknown = [word for word in rest if word.startswith("--") and word not in options[verb]]
    return f"`{verb}` takes no {', '.join(unknown)}" if unknown else None


class SkillsTest(unittest.TestCase):
    def test_the_four_skills_are_there_and_no_other(self) -> None:
        self.assertEqual({path.parent.name for path in SKILLS.glob("*/SKILL.md")}, SKILL_NAMES)

    def test_each_skill_is_named_as_its_folder_and_says_when_it_runs(self) -> None:
        for name in SKILL_NAMES:
            with self.subTest(name):
                meta, _ = front_matter(skill_file(name).read_text())
                self.assertEqual(meta["name"], name)
                self.assertIn(f"/{name}", meta["description"])

    def test_the_brief_is_last_under_its_heading(self) -> None:
        for name in SKILL_NAMES:
            with self.subTest(name):
                text = skill_file(name).read_text()
                self.assertTrue(text.endswith(BRIEF + "\n"))
                self.assertEqual(text.count("## The brief"), 1)
                self.assertEqual(text.count("$ARGUMENTS"), 1)

    def test_every_skill_but_create_reads_the_handbook_first(self) -> None:
        for name in SKILL_NAMES - {"create"}:
            with self.subTest(name):
                _, body = front_matter(skill_file(name).read_text())
                self.assertIn("`handbook.md`", first_step(body))

    def test_claude_md_names_every_skill_by_its_command(self) -> None:
        text = CLAUDE.read_text()
        for name in SKILL_NAMES:
            with self.subTest(name):
                self.assertIn(f"`/{name}`", text)


class ChatSkillTest(unittest.TestCase):
    def test_the_chat_skill_reads_the_naming_line_and_every_quote_tag(self) -> None:
        text = " ".join(skill_file("chat").read_text().split())
        for form in (NAMING_LINE, *QUOTE_TAGS, *QUOTED_PATHS):
            with self.subTest(form):
                self.assertIn(form, text)

    def test_the_chat_skill_takes_for_from_the_latest_naming_line(self) -> None:
        text = " ".join(skill_file("chat").read_text().split())
        for rule in LATEST_NAMING:
            with self.subTest(rule):
                self.assertIn(rule, text)

    def test_how_work_goes_is_answered_from_the_tree_and_grounding_agrees(self) -> None:
        text = skill_file("chat").read_text()
        _, _, rest = text.partition("- **How work goes**")
        passage, _, _ = rest.partition("\n## ")
        passage = " ".join(passage.split())
        for form in HOW_WORK_GOES:
            with self.subTest(form):
                self.assertIn(form, passage)
        _, _, rest = text.partition("\n## Grounding\n")
        grounding, _, _ = rest.partition("\n## ")
        self.assertIn(LOG_NOT_FOR_HOW_WORK_GOES, " ".join(grounding.split()))

    def test_a_ruling_on_an_item_of_pilot_s_own_is_carried_out_as_an_item_done_has_it(
        self,
    ) -> None:
        chat = " ".join(skill_file("chat").read_text().split())
        _, _, rest = skill_file("plan").read_text().partition("\n## An item done\n")
        mode, _, _ = rest.partition("\n## ")
        item_done = " ".join(mode.split())
        for form in RULING_ACTS:
            with self.subTest(form):
                self.assertIn(form, chat)
                self.assertIn(form, item_done)
        for form in RULING_CARRIED_OUT:
            with self.subTest(form):
                self.assertIn(form, chat)

    def test_a_close_through_the_chat_goes_on_to_what_is_next(self) -> None:
        chat = skill_file("chat").read_text()
        _, _, rest = chat.partition("- **A ruling or a close you record on an item of Pilot's own**")
        bullet, _, _ = rest.partition("\n## ")
        self.assertIn(RULING_THEN_NEXT, " ".join(bullet.split()))
        plan = skill_file("plan").read_text()
        _, _, rest = plan.partition("\n## An item done\n")
        item_done, _, _ = rest.partition("\n## ")
        self.assertIn(ITEM_DONE_THEN_NEXT, " ".join(item_done.split()))
        _, _, rest = plan.partition("\n## What is next\n")
        what_is_next, _, _ = rest.partition("\n## ")
        for step in WHAT_IS_NEXT_STEPS:
            with self.subTest(step):
                self.assertIn(step, what_is_next)

    def test_the_chat_offers_its_answer_and_what_it_can_do_itself(self) -> None:
        text = " ".join(skill_file("chat").read_text().split())
        for form in OFFERED_ANSWER:
            with self.subTest(form):
                self.assertIn(form, text)
        self.assertNotIn(OFFERED_ANSWER_RETIRED, text)


class CreateSkillTest(unittest.TestCase):
    def setUp(self) -> None:
        self.text = " ".join(skill_file("create").read_text().split())

    def test_the_create_skill_reads_the_naming_line_and_the_draft_s_quote_tags(self) -> None:
        for form in (NAMING_LINE, *DRAFT_QUOTE_TAGS, *DRAFT_QUOTED_PATHS):
            with self.subTest(form):
                self.assertIn(form, self.text)

    def test_the_create_skill_takes_for_from_the_latest_naming_line_or_the_starter(self) -> None:
        for rule in DRAFT_LATEST_NAMING:
            with self.subTest(rule):
                self.assertIn(rule, self.text)

    def test_the_create_skill_answers_and_attaches_as_pilot_store_takes_a_draft_s(self) -> None:
        for call in DRAFT_CALLS:
            with self.subTest(call):
                self.assertIn(call, self.text)

    def test_the_create_skill_leaves_create_project_to_the_operator(self) -> None:
        self.assertIn(CREATE_IS_THE_OPERATORS, self.text)


class PlanSkillTest(unittest.TestCase):
    def test_the_plan_skill_names_the_setup_by_its_kind_line(self) -> None:
        text = " ".join(skill_file("plan").read_text().split())
        self.assertIn(SETUP_KIND, text)
        self.assertIn("## The setup", text)

    def test_the_setup_reads_the_sections_the_create_skill_writes(self) -> None:
        for name in ("create", "plan"):
            text = skill_file(name).read_text()
            for section in DRAFT_SECTIONS:
                with self.subTest(skill=name, section=section):
                    self.assertIn(section, text)

    def test_the_setup_copies_the_draft_s_prose_and_none_of_its_asks(self) -> None:
        text = " ".join(skill_file("plan").read_text().split())
        for rule in SETUP_HANDBOOK:
            with self.subTest(rule):
                self.assertIn(rule, text)

    def test_the_plan_skill_names_each_mode_by_its_kind_line(self) -> None:
        text = " ".join(skill_file("plan").read_text().split())
        for form in (
            SETUP_KIND,
            PASS_KIND,
            WRITER_ANSWERED_KIND,
            ITEM_DONE_KIND,
            WAIT_FIRED_KIND,
            "entered from `/pre-rule`",
        ):
            with self.subTest(form):
                self.assertIn(form, text)

    def test_each_mode_is_a_section_of_its_own(self) -> None:
        lines = skill_file("plan").read_text().splitlines()
        for heading in PLAN_MODES:
            with self.subTest(heading):
                self.assertEqual(lines.count(heading), 1)

    def test_an_item_done_reads_the_item_s_line_as_the_server_writes_it(self) -> None:
        self.assertIn(ITEM_DONE_LINE, " ".join(skill_file("plan").read_text().split()))

    def test_an_action_of_pilot_s_done_reads_the_claimed_actions_as_the_server_writes_them(
        self,
    ) -> None:
        text = " ".join(skill_file("plan").read_text().split())
        for form in CLAIMED_ACTIONS:
            with self.subTest(form):
                self.assertIn(form, text)

    def test_a_claimed_action_its_run_still_holds_is_carried_to_the_run_s_next_turn(
        self,
    ) -> None:
        text = " ".join(skill_file("plan").read_text().split())
        for form in CLAIM_CARRIED:
            with self.subTest(form):
                self.assertIn(form, text)
        self.assertNotIn(CLAIM_NOTE, text)

    def test_a_claimed_action_is_the_operator_s_where_the_server_s_reading_hands_it_back(
        self,
    ) -> None:
        text = " ".join(skill_file("plan").read_text().split())
        for form in CLAIM_HANDED_BACK:
            with self.subTest(form):
                self.assertIn(form, text)
        for form in CLAIM_LINE_RETIRED:
            with self.subTest(form):
                self.assertNotIn(form, text)

    def test_the_plan_skill_applies_every_rule_file(self) -> None:
        text = skill_file("plan").read_text()
        for path in sorted((ROOT / "rules").glob("*.md")):
            with self.subTest(path.name):
                self.assertIn(f"`{path.relative_to(ROOT)}`", text)

    def test_the_modes_write_through_pilot_py_and_finish_through_pilot_store(self) -> None:
        text = " ".join(skill_file("plan").read_text().split())
        for call in PLAN_CALLS:
            with self.subTest(call):
                self.assertIn(call, text)

    def test_pilot_s_done_on_the_last_open_block_of_an_item_of_its_own_is_its_close(self) -> None:
        _, _, rest = skill_file("plan").read_text().partition("\n## In every mode\n")
        mode, _, _ = rest.partition("\n## ")
        text = " ".join(mode.split())
        for form in OWN_ITEM_CLOSED:
            with self.subTest(form):
                self.assertIn(form, text)


class WorkItemRuleTest(unittest.TestCase):
    def test_the_rule_file_holds_the_fields_and_the_brief(self) -> None:
        text = " ".join((ROOT / WORK_ITEMS).read_text().split())
        for form in (*WORK_ITEM_FIELDS, *WORK_ITEM_BRIEF):
            with self.subTest(form):
                self.assertIn(form, text)

    def test_the_brief_s_grants_text_is_a_section_of_the_grants(self) -> None:
        lines = (ROOT / "rules" / "grants.md").read_text().splitlines()
        self.assertIn("## In a worker's brief", lines)

    def test_the_skills_that_start_work_cite_it_and_carry_no_copy(self) -> None:
        for name in WORK_ITEM_SKILLS:
            text = " ".join(skill_file(name).read_text().split())
            with self.subTest(name):
                self.assertIn(f"`{WORK_ITEMS}`", text)
                for form in (
                    "`reasoning_effort`",
                    "In a worker's brief",
                    "In a promotion's brief",
                    "paste the handbook",
                ):
                    self.assertNotIn(form, text)


class PromoteRuleTest(unittest.TestCase):
    def test_the_rule_file_holds_what_every_promotion_needs_in_the_text_its_brief_carries(
        self,
    ) -> None:
        text = (ROOT / PROMOTE).read_text()
        self.assertEqual(text.splitlines().count(PROMOTE_SECTION), 1)
        _, _, section = text.partition(f"\n{PROMOTE_SECTION}\n")
        (block,) = re.findall(r"^```text\n(.*?)^```$", section, re.MULTILINE | re.DOTALL)
        block = " ".join(block.split())
        for form in PROMOTE_TEXT:
            with self.subTest(form):
                self.assertIn(form, block)

    def test_a_promotion_s_brief_carries_the_text_as_it_carries_the_grants(self) -> None:
        self.assertIn(PROMOTE_BRIEF, " ".join((ROOT / WORK_ITEMS).read_text().split()))


class DeferredPromotionTest(unittest.TestCase):
    def test_routing_defers_a_close_out_s_promotion_to_the_running_task(self) -> None:
        text = " ".join((ROOT / "rules" / "routing.md").read_text().split())
        for form in PROMOTION_ROUTED:
            with self.subTest(form):
                self.assertIn(form, text)
        for form in PROMOTION_ROUTED_RETIRED:
            with self.subTest(form):
                self.assertNotIn(form, text)

    def test_the_pass_defers_it_and_claims_it_not(self) -> None:
        text = " ".join(skill_file("pre-rule").read_text().split())
        for form in PROMOTION_DEFERRED:
            with self.subTest(form):
                self.assertIn(form, text)

    def test_what_is_next_starts_it_once_the_run_s_continuation_has_ended(self) -> None:
        _, _, rest = skill_file("plan").read_text().partition("\n## What is next\n")
        mode, _, _ = rest.partition("\n## ")
        text = " ".join(mode.split())
        for form in PROMOTION_DUE:
            with self.subTest(form):
                self.assertIn(form, text)


class PlacementRuleTest(unittest.TestCase):
    def test_a_placed_worker_runs_on_opus_at_xhigh_unless_the_work_names_another(self) -> None:
        text = " ".join((ROOT / PLACEMENT).read_text().split())
        for form in PLACEMENT_DEFAULTS:
            with self.subTest(form):
                self.assertIn(form, text)
        for form in PLACEMENT_RETIRED:
            with self.subTest(form):
                self.assertNotIn(form, text)

    def test_the_work_item_s_field_line_carries_the_defaults(self) -> None:
        text = " ".join((ROOT / WORK_ITEMS).read_text().split())
        self.assertIn(WORK_ITEM_DEFAULTS, text)


class PreRuleSkillTest(unittest.TestCase):
    def setUp(self) -> None:
        self.text = " ".join(skill_file("pre-rule").read_text().split())

    def test_the_pass_reads_the_brief_as_the_server_writes_it(self) -> None:
        for form in (PASS_KIND, *PASS_DOCUMENT_LINES):
            with self.subTest(form):
                self.assertIn(form, self.text)

    def test_the_pass_routes_by_the_rule_files(self) -> None:
        for rule in ("`rules/routing.md`", "`rules/grants.md`"):
            with self.subTest(rule):
                self.assertIn(rule, self.text)

    def test_the_pass_writes_through_pilot_py_marks_through_pilot_store_and_hands_on(self) -> None:
        for call in PASS_CALLS:
            with self.subTest(call):
                self.assertIn(call, self.text)

    def test_the_pass_reads_the_writer_answered_brief_as_the_server_writes_it(self) -> None:
        for form in (WRITER_ANSWERED_KIND, *WRITER_ANSWERED_LINES):
            with self.subTest(form):
                self.assertIn(form, self.text)

    def test_the_pass_waits_on_an_event_as_its_own_route_and_holds_none_back(self) -> None:
        self.assertIn("- **Waited on**, an owed action waiting on an event", self.text)
        self.assertNotIn("## Not yet the pass's", self.text)

    def test_the_pass_routes_the_researched_blocks_as_the_server_writes_them(self) -> None:
        lines = skill_file("pre-rule").read_text().splitlines()
        self.assertEqual(lines.count("## A researched block"), 1)
        for form in (*RESEARCHED_BLOCKS, *RESEARCH_ROUTED):
            with self.subTest(form):
                self.assertIn(form, self.text)


class OperatorReadsTest(unittest.TestCase):
    def test_a_note_is_the_choice_and_its_reason_and_the_findings_go_to_the_session_log(
        self,
    ) -> None:
        for source in NOTE_RULE_FILES:
            text = " ".join((ROOT / source).read_text().split())
            for form in (NOTE_RULE, FINDINGS_LOGGED):
                with self.subTest(source=source, form=form):
                    self.assertIn(form, text)
        for source, text in the_map().items():
            text = " ".join(text.split())
            for form in FINDINGS_IN_NOTE:
                with self.subTest(source=source, form=form):
                    self.assertNotIn(form, text)

    def test_a_notice_is_for_what_the_operator_must_know_or_do_and_an_item_leads_with_its_ruling(
        self,
    ) -> None:
        for name in NOTICE_SKILLS:
            text = " ".join(skill_file(name).read_text().split())
            for form in (NOTICE_RULE, ITEM_LEAD):
                with self.subTest(skill=name, form=form):
                    self.assertIn(form, text)

    def test_a_notice_on_a_block_left_to_the_operator_ends_with_the_answer_pilot_suggests(
        self,
    ) -> None:
        self.assertIn(NOTICE_SUGGESTS, " ".join(skill_file("pre-rule").read_text().split()))


class ResearchTest(unittest.TestCase):
    def test_the_map_names_a_researched_block_in_researches_on_add_item(self) -> None:
        for source, form in RESEARCH_NAMED.items():
            with self.subTest(source):
                self.assertIn(form, " ".join((ROOT / source).read_text().split()))


class WaitTest(unittest.TestCase):
    def test_no_file_of_the_map_refuses_a_wait(self) -> None:
        for source, text in the_map().items():
            for words in WAIT_REFUSALS:
                with self.subTest(source=source, words=words):
                    self.assertNotIn(words, text)

    def test_the_skills_that_add_a_wait_name_its_kinds_and_arm_it_as_routing_does(self) -> None:
        for name in WAIT_ADDING_SKILLS:
            text = " ".join(skill_file(name).read_text().split())
            for form in (*WAIT_KINDS, WAIT_ARMED):
                with self.subTest(skill=name, form=form):
                    self.assertIn(form, text)
        routing = " ".join((ROOT / "rules" / "routing.md").read_text().split())
        for form in ROUTING_WAIT:
            with self.subTest(form):
                self.assertIn(form, routing)

    def test_claude_md_names_both_kinds_and_routes_a_resumed_run_to_the_plan_skill(self) -> None:
        text = " ".join(CLAUDE.read_text().split())
        for form in (*WAIT_KINDS, WAIT_FOLLOW_UP, WAIT_FOLLOW_UP_ROUTED):
            with self.subTest(form):
                self.assertIn(form, text)

    def test_a_wait_s_firings_read_the_brief_and_the_follow_up_as_the_server_writes_them(
        self,
    ) -> None:
        text = " ".join(skill_file("plan").read_text().split())
        for form in (WAIT_FIRED_KIND, *WAIT_FIRED_LINES, WAIT_FOLLOW_UP):
            with self.subTest(form):
                self.assertIn(form, text)

    def test_a_wait_s_firings_are_judged_read_again_and_closed_with_a_note_or_left_open(
        self,
    ) -> None:
        _, _, rest = skill_file("plan").read_text().partition("\n## A wait's firings\n")
        mode, _, _ = rest.partition("\n## ")
        text = " ".join(mode.split())
        for form in WAIT_FIRINGS:
            with self.subTest(form):
                self.assertIn(form, text)
        for form in WAIT_FIRINGS_RETIRED:
            with self.subTest(form):
                self.assertNotIn(form, text)


class CitationsTest(unittest.TestCase):
    def test_claude_md_and_every_skill_cite_the_format_skill_by_its_name(self) -> None:
        for path in [CLAUDE, *(skill_file(name) for name in SKILL_NAMES)]:
            with self.subTest(path.relative_to(ROOT)):
                text = path.read_text()
                self.assertIn(f"`{FORMAT_SKILL}`", text)
                self.assertEqual(set(re.findall(r"/[\w:-]*format\b", text)), {FORMAT_SKILL})

    def test_every_path_the_map_cites_is_there(self) -> None:
        names = repo_names()
        for source, text in the_map().items():
            for path in cited_paths(text):
                with self.subTest(source=source, path=path):
                    self.assertTrue(is_there(path, names))

    def test_claude_md_gives_every_verb_of_pilot_py_its_one_line(self) -> None:
        text = " ".join(CLAUDE.read_text().split())
        verbs = pilot_verbs()
        for verb, description in verbs.items():
            with self.subTest(verb):
                self.assertIn(f"`{verb}`: {description}", text)
        named = set(re.findall(r"`(pilot\.py [a-z ]+)`:", text))
        self.assertEqual(named, set(verbs))

    def test_claude_md_names_every_tool_call_the_hook_locks_around(self) -> None:
        settings = json.loads((ROOT / ".claude" / "settings.json").read_text())
        (entry,) = settings["hooks"]["PreToolUse"]
        text = CLAUDE.read_text()
        for tool in entry["matcher"].split("|"):
            with self.subTest(tool):
                self.assertIn(f"`{tool}`", text)

    def test_every_pilot_py_command_the_map_quotes_is_one_its_parser_takes(self) -> None:
        options = pilot_options()
        for source, text in the_map().items():
            for command in quoted_commands(text):
                with self.subTest(source=source, command=command):
                    self.assertIsNone(command_fault(command, options))

    def test_the_claim_is_quoted_with_the_value_pilot_py_reads_as_one(self) -> None:
        value = f'--value "{pilot_module().CLAIM}"'
        for path in (skill_file("pre-rule"), skill_file("plan"), ROOT / "rules" / "routing.md"):
            with self.subTest(path.relative_to(ROOT)):
                self.assertIn(value, " ".join(path.read_text().split()))

    def test_ask_writer_is_named_by_the_arguments_pilot_store_takes(self) -> None:
        for path in (skill_file("pre-rule"), ROOT / "rules" / "routing.md"):
            with self.subTest(path.relative_to(ROOT)):
                self.assertIn(ASK_WRITER, " ".join(path.read_text().split()))

    def test_the_grants_name_every_confirmation_reason_by_its_code(self) -> None:
        reference = json.loads(
            (ROOT / "tests" / "fixtures" / "tree" / "reference.json").read_text()
        )
        grants = (ROOT / "rules" / "grants.md").read_text()
        for reason in reference["confirmation_reasons"]:
            with self.subTest(reason["code"]):
                self.assertIn(f"`{reason['code']}`", grants)


class PathCheckTest(unittest.TestCase):
    """The citation check itself: what it takes for a path, and what it refuses."""

    def test_a_path_is_a_file_name_or_a_folder(self) -> None:
        self.assertEqual(
            cited_paths(
                "`rules/grants.md`, `cexec python uv run tools/pilot.py <verb> …`, `items/`,"
                " `owner/Name`, `--project`, `$PILOT_PROJECT`, `<environment>:<path>`"
            ),
            ["rules/grants.md", "tools/pilot.py", "items/"],
        )

    def test_a_fenced_block_is_taken_out_before_the_code_spans(self) -> None:
        self.assertEqual(
            cited_paths(
                "```text\ncexec python uv run tools/pilot.py answer <file> <block>\n```\n\n"
                "Read `rules/nothere.md`, then `rules/grants.md`.\n"
            ),
            ["rules/nothere.md", "rules/grants.md"],
        )

    def test_a_path_is_there_in_the_repo_or_the_project_folder(self) -> None:
        names = repo_names()
        for path in (
            "rules/grants.md",
            ".claude/skills/<name>/SKILL.md",
            "tools/",
            "pilot.py",
            "handbook.md",
            "items/<seq>-<slug>.md",
            "/work/Projects/reference.json",
        ):
            with self.subTest(path):
                self.assertTrue(is_there(path, names))

    def test_a_path_missing_from_both_is_not(self) -> None:
        names = repo_names()
        for path in ("rule/grants.md", ".claude/skill/<name>/SKILL.md", "handbok.md", "tool/"):
            with self.subTest(path):
                self.assertFalse(is_there(path, names))


class CommandCheckTest(unittest.TestCase):
    """The command check itself: what it takes for a pilot.py command line, and what it refuses."""

    def test_a_command_is_a_code_span_that_opens_with_the_script(self) -> None:
        self.assertEqual(
            quoted_commands(
                "```text\npilot.py plan note strike n1\n```\n\n"
                "Run `pilot.py plan note strike <id>`, not `cexec python uv run tools/pilot.py"
                " <verb> …` or `pilot.py`."
            ),
            ["pilot.py plan note strike <id>"],
        )

    def test_a_verb_with_its_own_options_and_placeholders_is_taken(self) -> None:
        options = pilot_options()
        for command in (
            "pilot.py plan note add --task <id> --summary <line> --ref <block id> <content>",
            "pilot.py answer <file> <block id> --value <option> --note <their words>",
            "pilot.py items show <id>",
            "pilot.py --help",
        ):
            with self.subTest(command):
                self.assertIsNone(command_fault(command, options))

    def test_a_word_that_is_no_verb_or_an_option_of_another_verb_is_refused(self) -> None:
        options = pilot_options()
        self.assertEqual(
            command_fault("pilot.py plan note remove <id>", options),
            "`pilot.py` has no verb `plan note remove`",
        )
        self.assertEqual(
            command_fault("pilot.py answer <file> <block id> --to plan", options),
            "`pilot.py answer` takes no --to",
        )
