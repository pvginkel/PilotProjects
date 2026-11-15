"""The brain's map as its sessions load it — CLAUDE.md, the rule files and the four skills: each
skill named as its folder and its brief last, the handbook read first, the format skill cited by
its name, pilot.py's verbs as its parser has them, the tool calls the hook locks around, every
pilot.py command line it quotes one the parser takes, every path the map cites in place, the chat
skill and the create skill reading a person's message as PilotApp's server sends it, the create
skill naming a draft's ask and its material as pilot-store takes them, the pre-rule skill reading
the briefs of a worker's turn and of its writer's answer as PilotApp's server writes them and
naming its writes — a claim, a research, a question to the writer and a wait among them — routing
the blocks a research's brief gives and its hand-on to the plan, making nothing, a notice, a card
or a fieldnote of the stage session's debrief they carry, an open card on the same change
commented on rather than a card made, a card on it the one exception
rules/stages.md makes to a stage's documents, whose brief says nothing of it, the plan skill naming
each mode by its brief's kind line, reading the brief of an item done, the claimed actions of a
worker's turn and the brief and the follow-up of a wait's run as the server writes them, a claimed
action the run's or the operator's where the server's reading draws the line, an open action of an
item of Pilot's own that a work item does claimed by the routing rule's one section, which
CLAUDE.md, the chat and the plan cite, its done the item's close with no mark, naming its writes,
the finish decision's options and what each calls of pilot-store's `finish`, and copying the draft's
prose into the handbook without its asks, a task's title the task alone and what it waits on a note,
no file of the map refusing a wait, a work item's fields and brief in one rule file the skills
starting work cite, the chat's cancel of an ask of Pilot's own by `cancel_ask`'s arguments, the
chat's alone, and a replaced work item closed through `stop_work`'s `reason`, in that rule file,
which the chat's correction and the plan's jobs cite."""

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
# The plan's end checks the handbook's result first: in a project whose handbook grows the plan a
# step at a time in the chat, the operator is asked for the next step, with no sweep and no finish
# decision (P-204, the operator's note of 2026-11-05).
PLAN_END_RESULT_FIRST = (
    "**The plan's end**: once its last task is done, the handbook's result checked first",
    "Where it is not reached and the handbook adds the plan's steps in the chat, the next"
    " prerequisite is the operator naming the next step, asked as an item, with no sweep and no"
    " finish decision; otherwise The sweep, then The finish decision.",
)
RULING_CARRIED_OUT = (
    "**A ruling or a close you record on an item of Pilot's own**",
    "is carried out in this turn: no job of Pilot's follows what the chat records",
    "what the turn leaves undone waits for Pilot's next job",
    "the finish decision's `Finish` your `finish`, its `Finish and archive` your `finish` with"
    " `archive` `true`, either the turn's last call, after your reply",
)
# Asked about an open block, the chat offers the answer it would record, and it does or offers
# what it can do itself rather than adding an ask item (P-194's chat half).
OFFERED_ANSWER = (
    "**Asked about an open block**, lead with a short answer, then offer the answer you would"
    " record: its option and its note",
    "you do in this turn where the person asked for it, or offer in the reply: never an ask item",
    "Past an offer of either kind, or of calling off an ask you find obsolete yourself"
    " (Recording's An ask the person calls off), the chat asks no closed question of its own",
)
# A small correction the chat makes unasked and says so (P-353, the store's memory note
# small-corrections-unasked; P-194's chat half without it).
SMALL_CORRECTION = (
    "A small correction — to your own wording, a typo, an obvious fix to what you just wrote — you"
    " make in the turn, unasked, and say so in the reply"
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
# The stage session's debrief as BriefService writes it after the turn its loop completed in
# (PilotApp's brief_service.py, `_debriefed`): its line, then its words, after what is attached and
# before the claimed actions, and last in the brief after the writer answered.
DEBRIEF_LINE = "`The stage session's debrief, as given:`"
DEBRIEF_IN_THE_BRIEF = (
    "the files attached on the work item; the stage session's debrief, where it gave one,"
    f" {DEBRIEF_LINE} and its words on the lines after it; the claimed actions given",
    "and last the stage session's debrief, where it gave one, in the lines The debrief reads",
)
# A brief without it, a Pilot's that carries no debrief among them, leaves the pass nothing to do;
# and the debrief is no document, so nothing of it is answered, marked or written.
DEBRIEF_ABSENT = "A brief without that line has none"
DEBRIEF_NO_DOCUMENT = "The debrief is no document: it has no block, and nothing is answered"
# What the pass makes of it (F52.4): nothing; a notice, only where the operator must know or do
# something, ending with its suggestion (D142, D144); a card, none of a finding a stage's document
# holds; or a fieldnote, one already there for the same friction fine.
DEBRIEF_FATES = (
    "- **Nothing**, where it holds nothing the operator must know or do and nothing to change.",
    "- **A notice**, only where the operator must know or do something",
    "and ending with what you suggest",
    "- **A card**, for a change the debrief shows is needed",
    "a close-out's among them, is that document's, its fate the stage's to carry out:"
    " no card of it",
    "- **A fieldnote**, for friction the debrief names in an environment or in tooling",
    "one already there for the same friction, that one is fine",
)
# A card from a debrief is looked for first (slice 043's close-out I1, the operator's Agree,
# 2026-11-15): an open card on the same change in that project takes the debrief's words as a
# comment and no card is made; CLAUDE.md grants that comment, and the summary line names it.
DEBRIEF_OPEN_CARD = (
    "Before you make it, search that project through youtrack for an open card on the same change:"
    " where one is open, add the debrief's words it rests on to that card as a comment, quoted,"
    " and make no card",
    "the comment by its card's id",
)
COMMENT_GRANT = (
    "yours to read with, and to make a card, a comment on an open card, a fleet call or a"
    " Fieldnotes post where a rule says so"
)
# A stage's documents get no card and no fold of the pass's, the stage's continuation carrying out
# their fates; a card on the stage session's debrief is the one exception; and the stage's brief
# says nothing of its debrief or of notices.
STAGE_DOCUMENTS_NO_CARD = "you make no card and fold nothing, or it is done twice"
STAGE_DEBRIEF_CARD = "is no document of the stage's, and a card on it is yours: the one exception"
STAGE_BRIEF_SILENT = "no list of what to register, and nothing on its debrief or on notices"
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
# An open action of an item of Pilot's own that a work item does takes the claim route (PilotApp's
# RecordService.claimable, widened by its D224): named in `claims`, then the claim, and
# its `done` after the work's turn the item's close on its last open block, with no `mark` and no
# undo (RecordService.done_by_its_save), so that the item leaves the operator's queue. The routing
# rule's section is its one home, which the rule's head names and CLAUDE.md, the chat and the plan
# cite; a research stays on a worker's document.
OWN_ACTION_SECTION = "## The claim"
OWN_ACTION_SCOPE = (
    "the claim route also takes an open action of an item of Pilot's own that a work item does"
    " (The claim)"
)
OWN_ACTION_RULE = (
    "An action Pilot may run under the grants that a work item does is claimed: a worker's"
    " document's, as the routes have it, or an open action of an item you added, in `items/`, that"
    " a work item does",
    "The block is named in `claims` on the `add_item` of the work item that does it, added in the"
    ' same turn, then `pilot.py answer` with `--value "Pilot does it"`, the note naming that work'
    " item in words",
    "the job after the work's turn writes its `done`, the paste-back (`/plan`'s An action of"
    " Pilot's done)",
    "where that was the item's last open block, its `done` is the item's close, with no `mark`"
    " after it and no undo, so that the item leaves the operator's queue once the work has done it",
    "a work item that does it unclaimed leaves it open there",
    "an act the run leaves undone is the operator's again",
    "`researches` names a worker's document's blocks alone",
)
# The claim route's row, which points at the section and writes the claim out no more.
OWN_ACTION_ROW = "claimed, unless the row after takes it (The claim). Done at once"
# The rule's head while it routed what a worker registered alone.
OWN_ACTION_SCOPE_RETIRED = "and what each route writes. The route is"
OWN_ACTION_CITED = "as `rules/routing.md`'s The claim has it"
OWN_ACTION_CITING_SKILLS = ("chat", "plan")
OWN_ACTION_IN_CLAUDE = (
    "`rules/routing.md` (where an open block goes, the claim, of a worker's document or of an item"
    " of yours, a block a run holds,",
    "`claims` the actions you claimed that it does, of a worker's document or of an item of yours,",
    "An item of yours closes at the `done` of its last open block, a claimed action's included,"
    " with no undo and no `mark` after it, which the server refuses.",
)
# After the work's turn, the plan writes the `done` and marks a worker's document Done; an item of
# its own takes no `mark`, its `done` its close.
OWN_ACTION_DONE = (
    "Its path is a worker's document's, in `inbox/`, or an item of yours, in `items/`.",
    "Then a worker's document is marked Done where that was its last open block",
    "An item of yours takes no `mark`: the `done` of its last open block is its close, with no"
    " undo, and it leaves the operator's queue",
)
# The plan's every mode and the chat's work claim it on the work item's add_item.
OWN_ACTION_BY_A_JOB = (
    "- **An action of yours a work item does**, an open action of an item you added that you hand"
    " to a work item, one you put to the operator among them, is claimed on that work item's"
    " `add_item`"
)
OWN_ACTION_BY_THE_CHAT = (
    "Work that does an open action of an item of Pilot's own, one the person hands to a worker,"
    " claims it on its `add_item`",
    CLAIM_NAMED.removeprefix("its "),
    "the claim of an action of an item of Pilot's own that a work item does (`pilot.py answer`,"
    " Acting)",
)
# The modes' writes past the setup: a task's status, a note struck, a homeless deferral's note, and
# pilot-store's `finish` on the finish decision's Finish.
PLAN_CALLS = (
    "`pilot.py plan task set <id> --status done`",
    "`pilot.py plan note strike <id>`",
    "`pilot.py plan note add --task <id> --summary <line> --ref <block id> <content>`",
    "the job after its close calls `finish`",
    "`pilot.py done <file> <block id> --note <what was done and what was seen>`",
    "`mark`, `item` the document's id, `mark` `done`, and no `for`",
)
# The finish decision's options by their labels and what each calls: pilot-store's `finish` takes
# `archive` (PilotApp's pilot_mcp/tools.py), whose description names the option by the words
# "Finish and archive on that decision", and without it the server asks the archive question.
FINISH_DECISION = (
    "asking whether to finish, its options `Finish`, `Finish and archive` and `No`, by those"
    " labels",
    "On its `Finish`, the job after its close calls `finish`, last",
    "the archive question after it is the server's",
    "On its `Finish and archive`, the same call with `archive` `true`, on that answer alone",
    "the project is archived with the finish, and no archive question follows",
    "On a No, its reason read and the plan adjusted",
)
FINISH_TOOL = (
    "- `finish`: the project finished, on the operator's `Finish` on the finish decision; with"
    " `archive`, on their `Finish and archive`, archived with it, and no archive question asked."
)
FINISH_YES_RETIRED = ("On its Yes", "the finish decision's Yes", "Yes to the finish decision")
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
# How long a run holds a block, claimed or researched, and a failed run's: one routing section,
# which the plan's An action of Pilot's done and the pass's A researched block cite.
HELD_SECTION = "## A block a run holds"
HELD_RULE = (
    "A claimed action, or a block left open on a research (Due diligence, step 4), stays the run's"
    " until the job after a turn of it that registered no document with a block in it ends (never a"
    " clarification run's turn, which registers nothing), or its work fails or is stopped, or a"
    " person cancels the run: Pilot's server reads that, and nothing Pilot writes hands one over",
    "A run that failed gets no job: its work item waits on a person's Resume, the blocks it holds"
    " standing open",
)
HELD_CITED = "`rules/routing.md`'s A block a run holds"
HELD_CITING = (
    ("plan", "## An action of Pilot's done"),
    ("pre-rule", "## A researched block"),
)
CLAIM_HANDED_BACK = (
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
NOTE_RULE_FILES = ("rules/routing.md",)
# The skills that write a note cite the routing rule's head for it, as the chat does.
NOTE_RULE_CITED = "`rules/routing.md`'s head has"
NOTE_RULE_CITING = ("pre-rule", "plan", "chat")
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
# pilot-store's `cancel_ask` as it takes its arguments (PilotApp's pilot_mcp/tools.py): `item`, the
# ask's id, and `for`, the handle of the person on whose word it is called off. PilotApp's
# RecordService.call_off refuses Pilot as that person, a document a work item's run registered,
# whose page's Cancel ends the run, and a notice (P-233).
CANCEL_ASK = "`cancel_ask`"
CANCEL_TOOL = (
    "- `cancel_ask`: an open ask of Pilot's own, one `add_item` added — a decision, a"
    " confirmation, a question, an action or a document — called off on the word of the person"
    " `for` names, given in the chat: `item` its id, done as cancelled, by them, with no undo and"
    " no job following it. Never on your own word. A document a work item's run registered is"
    " refused: the Cancel on its page, which ends that run, is the one way to call it off."
)
# When the chat cancels for a person, beside the Done, Read and Reviewed it records for them: an
# ask that no longer applies, on their word alone, never in place of an answer.
CANCEL_BESIDE = "- **Done, Read and Reviewed** a person gives go through `mark` with `for` them"
CANCEL_BY_THE_CHAT = (
    "**An ask the person calls off**",
    "`cancel_ask` with `item` the ask's id and `for` their handle",
    "on an open ask of Pilot's own, in `items/`: a decision, a confirmation, a question, an action"
    " or a document",
    "an ask that no longer applies, never for an answer: a confirmation they refuse takes its `No`"
    " through `answer`",
    "Only on their word: an ask you find obsolete yourself you offer to call off in the reply",
    "A worker's document in `inbox/` is refused: the person calls it off themselves, with the"
    " Cancel on its page, which ends its run",
)
CANCEL_EFFECT = '"Cancelled · <title>"'
# No job follows a cancel the chat records, so its turn brings the plan up to date.
CANCEL_CARRIED_OUT = "an ask called off: none of its acts, and the plan adjusted to its going"
# The files that name the call: a job has no person's word, so no skill of a job names it.
CANCEL_FILES = {"CLAUDE.md", ".claude/skills/chat/SKILL.md"}
# A free-form work item's own card closed, Done with a comment, by the job after its last turn,
# once its done-when is met and no document of its run is open (P-281, the operator's note).
OWN_CARD_SECTION = "## Its own card"
OWN_CARD_CLOSED = (
    "A free-form work item's own card, the card it was started to work, is closed by the job after"
    " the work item's last turn, once the card's done-when is met and no document of its run is"
    " open: Done, through youtrack, with a comment"
)
# pilot-store's `stop_work` with `reason` (PilotApp's pilot_mcp/tools.py): the work item closed for
# good in the same act, one stopped earlier included, and a failed one refused (P-201). The rule's
# one home is the work item's rule file, which the chat's correction and the plan's jobs cite.
STOP_TOOL = (
    "- `stop_work`: a work item's session stopped, running, starting or held, for a person to"
    " resume; a job of yours is refused. With `reason`, a line its done line carries, the work"
    " item is closed for good in the same act, for one you replaced with another"
    " (`rules/work-items.md`): stopped where it was not, one stopped earlier included, and done as"
    " cancelled, with no Resume and no undo; one that failed is refused."
)
REPLACED_SECTION = "## A work item replaced"
REPLACED_RULE = (
    "is closed for good in the turn that adds the other: `stop_work` with `item` its id and"
    " `reason`, a line saying what replaced it and why",
    "It is stopped where it was not, one stopped earlier included, and done as cancelled",
    "takes no Resume and no undo",
    '"Closed · <title>"',
    "The documents its run put to a person stay open and theirs",
    'Without `reason`, `stop_work` only stops, "Stopped · <title>"',
    'One that failed is refused, "it has failed, and keeps its Resume"',
)
REPLACED_CITED = "`stop_work` with `reason`, as `rules/work-items.md`'s A work item replaced has it"
REPLACED_BY_THE_CHAT = (
    "A work item the new one replaces is closed for good with it, never left stopped beside it",
    "nothing is said stopped or closed before `stop_work` answered its effect,"
    ' "Stopped · <title>" or "Closed · <title>"',
)
# A work item the person drops in the chat, with nothing in its place, closed for good on their
# word, their words the reason (P-298, the operator's "Agreed", 2026-11-15, widening "Pilot closes
# what it replaces, with its reason" to what a person drops).
DROPPED_BY_THE_CHAT = (
    "A work item the person drops, its work no longer wanted with nothing in its place",
    "is closed for good on their word: `stop_work` with `reason` their words, never left stopped"
    " for them to close",
)
REPLACED_BY_A_JOB = (
    "A work item you replace with another, its task changed by a ruling or its brief outdated, is"
    " closed for good with it, never left stopped beside it"
)
# The map's line while `stop_work` took no reason.
STOP_TOOL_RETIRED = "running, starting or held; a job of yours is refused"
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
# The brief names the application's commit alone, and the procedure takes the deploy repository's
# from the build's pin line, since it exists only once the build has pinned it (P-216).
PROMOTE_DEPLOY_COMMIT = (
    "The deploy commit, from the build: the brief names the application's commit alone, and the"
    " job's `commit` takes the deploy repository's, which exists only once the build has pinned it",
    "PilotApp's `pvginkel/PilotDeploy <sha> pins config/dev/values.yaml, …`",
    "`<n>` the build track_build.py's summary names",
    "never the application's, which the job refuses as not on `main`, and never none, which"
    " promotes the deploy repository's tip, which a later build may have moved past",
    '--data-urlencode "commit=<the deploy commit>"',
)
PROMOTE_BRIEF_COMMIT = (
    "step 2 naming the application, its commit, the application's alone, never the deploy"
    " repository's, which the promotion takes from the build, and what follows it"
)
# A close-out's promotion deferred to the run's own task, never claimed, with what the close-out
# owes after it, so that the close-out closes on its other blocks and the continuation goes on;
# the promotion due once that continuation has ended, so that it takes its fixes (P-183, D2). Its
# one home is the routing rule's section, which the routes, Deferral, the pass and the plan cite.
PROMOTION_SECTION = "## A close-out's promotion"
PROMOTION_ROUTED = (
    "A close-out's promotion Pilot may run under the grants goes with the update that follows it,"
    " the store's after a PilotApp promotion, and every action the close-out owes after the"
    " promotion — a criterion's `Settle <id> after …`",
    "deferred to the running task, never claimed: each through `pilot.py defer`, `--to` the run's"
    " own task, so that the close-out closes once its other blocks are answered and the run's"
    " continuation goes on, and so that the promotion takes the fixes of the run's continuation",
    "the event it waits on is the end of the run's continuation, whose turn a job of Pilot's"
    " follows",
    "They are due once that continuation has ended, the work item that continues the run done after"
    " a turn that registered no document with a block in it; until then their notes stand",
    "One work item then does them all, the promotion first, its brief carrying `rules/promote.md`",
)
PROMOTION_POINTED = (
    "| a close-out's promotion Pilot may run under the grants, with what follows it | deferred to"
    " the running task, never claimed (A close-out's promotion). |",
    "| the run's end: a close-out's promotion and what follows it | a note on the running task, due"
    " once the run's continuation has ended (A close-out's promotion) |",
    "A close-out's promotion is the one exception (A close-out's promotion).",
    "A deferral from a close-out, the task's last document, goes to the next task or to the end, but"
    " for its promotion and what follows it, which go to the running task (A close-out's"
    " promotion).",
)
PROMOTION_CITED = "`rules/routing.md`'s A close-out's promotion"
# The rule's words while a close-out's promotion was claimed and its deferral barred the run.
PROMOTION_ROUTED_RETIRED = ("goes to the next task or to the end, never to the running task",)
PROMOTION_DEFERRED = (
    "A close-out's promotion, the update that follows it and every action the close-out owes after"
    f" it are deferred so, `--to` the run's own task, never claimed ({PROMOTION_CITED})"
)
PROMOTION_DUE = (
    "**A close-out's promotion**, deferred to the run's own task with what follows it, is met only"
    f" once it is due, as {PROMOTION_CITED} has it: until then its notes stand, neither acted on"
    " nor struck",
    "one work item does them all, its `step` the run's task, the promotion first, its brief"
    " carrying `rules/promote.md`",
    "and naming the application's commit read then, its `main` as the continuation left it, never"
    " the commit or the build the close-out's block names, which predate the continuation's fixes",
    "that `main` read on GitHub itself, never through gitblit, a daily mirror that may not hold the"
    " continuation's push yet",
)
# Where a run's turn and what it registered do not say, its reply is read whole, through
# `get_session_response`, never the session log, whose lines are cut (P-291's PilotProjects half).
REPLY_READ = (
    "its turn's reply whole (`get_session_response`), never its session log, `get_session_log`,"
    " which cuts every line at about 80 characters"
)
REPLY_READ_SECTIONS = (
    ("plan", "## An action of Pilot's done"),
    ("pre-rule", "## A researched block"),
)
# A cancelled run's deferred promotion: no continuation comes, so it is never started, and the
# operator gets a notice naming it (P-215, the operator's "Agreed", 2026-11-12, to "The card has
# Pilot send you a notice naming the promotion and start nothing").
PROMOTION_CANCELLED_ROUTED = (
    "A run a person cancels has no continuation: its promotion and what follows it are never"
    " started, and go to the operator as a notice naming the promotion, the notes struck"
)
PROMOTION_CANCELLED_DUE = (
    "**A run a person cancelled**, its documents closed by the Cancel, their `done` `cause`"
    " `cancelled` in `timeline.json`, has no continuation to end: its promotion and what follows it"
    " are never started",
    "The job that meets their notes starts nothing of them, posts the operator a notice naming the"
    " promotion and the cancelled run it was owed after, and strikes the notes.",
)
# A placed worker's model and effort: Opus at xhigh for every work item, and Fable on a person's
# own word for that work alone, asked once more before it is placed, in the placement rule and in
# the work item's field line; a brief's one line on how, the sub-agents, and the draft's rules,
# which name no model.
PLACEMENT = "rules/placement.md"
PLACEMENT_DEFAULTS = (
    "`model` is `opus` and `reasoning_effort` is `xhigh`, for every work item, whatever its size"
    " and its kind",
    "you pick no lower model or effort for one, and a design or an arch design takes no other",
    "Fable is the one other model, and it is never yours to choose",
    "only where a person named Fable for that piece of work in their own words",
    "and you then asked them once, in a question of its own that names the work item and says"
    " whether its sub-agents run on Fable too, and they said yes",
    "not a handbook, a `project.md`, a plan's task or note or a brief, which a session wrote",
    "not the answer to a question about something else whose option named a model",
    "You write no model and no effort into any of them, and you recommend and offer none",
)
WORK_ITEM_DEFAULTS = (
    "`model` and `reasoning_effort` as `rules/placement.md` says, `opus` and `xhigh`, Fable on a"
    " person's own word for that work alone"
)
WORK_ITEM_SUB_AGENTS = (
    "the session hands its reading, its research and whatever else stands apart to sub-agents,"
    " eagerly, each call naming the model and the effort its job needs and never Fable"
)
DRAFT_RULES_NAME_NO_MODEL = (
    "No rule names a model or an effort for work, whatever the opening or a brief says of one,"
    " and no ask's option carries one along: `rules/placement.md`'s The model and the effort"
)
# With auto pilot off, a push the operator approves is an agent's to make, never handed back to
# them, in the grants and in the auto-pilot-off brief's text (P-248's note of 2026-11-14, ruled
# "Agreed" at the GA wrap-up, 2026-11-15).
PUSH_AFTER_APPROVAL = (
    "With auto pilot off, a push the granted column asks for is the operator's approval alone: on"
    " their Yes an agent makes it — the worker that asked, or a work item of Pilot's — and nothing"
    " asks them to push themselves"
)
PUSH_AFTER_APPROVAL_BRIEF = "A push they approve is yours to make, never theirs."
# A design, a design session or an arch design is a work item of Pilot's that presents the design
# as a document, never an action for the operator's hands; a mockup is theirs (P-353, the store's
# memory note design-through-pilot; the operator, 2026-11-14).
DESIGN_SECTION = "## A design"
DESIGN_THROUGH_PILOT = (
    "A design, a design session or an arch design (`/dev:arch-design`) that a task needs is a work"
    " item of yours, placed as any other, and never an action for the operator's hands",
    "its brief has it present the design to the operator as a document",
    "A mockup is the operator's own, which they make themselves: a task that needs one waits on an"
    " action for them.",
)
DESIGN_ROUTED = (
    "a secret no repository's tooling can place, a mockup, which they make themselves | left to the"
    " operator, with no edit. |",
    "an Ansible work item, a design, a design session or an arch design (`rules/placement.md`'s A"
    " design), among them |",
)
# An operator action that needs infrastructure access Pilot's environments lack is an Ansible
# work item, the granted column's, never a new capability; its brief's command, and a secret by
# its path and key, minted on stdin (P-353, the store's memory note infra-through-ansible; the
# operator, 2026-11-03, generalising D121 of 2026-11-02).
INFRA_THROUGH_ANSIBLE = (
    "Infrastructure access Pilot's environments lack — `kubectl exec` or a write on prd, an OpenBao"
    " leaf, a host change — is the same: a work item in `pvginkel/Ansible`, `/work/Ansible`",
    "an operator action Pilot can run itself, the granted column's, and never a new capability for"
    " the app's environments",
    "Its brief gives the exact command and says not to work around a failure",
    "what needs another environment checked, Pilot checks itself",
    "For a secret, the brief names its OpenBao path and key, `kv/eso/<stage>/<app>/<stage>/<leaf>`,"
    " and the agent mints the value and writes it on stdin, `bao kv put -mount=kv <leaf> <key>=-`",
    "is their convention for a person at a terminal: for Pilot's work this ruling stands",
)
INFRA_PLACED = (
    "an operator action that needs infrastructure access Pilot's environments lack in"
    " `pvginkel/Ansible`, its `cwd` `/work/Ansible` (`rules/grants.md`)"
)
# The rule's words while the effort was left unset and the stage could name a model, and while a
# handbook or a task could name another model, or Pilot a lower one.
PLACEMENT_RETIRED = (
    "left unset",
    "the stage",
    "names another model",
    "kept for the design",
    "lower model or effort where",
)


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
        self.assertIn(SMALL_CORRECTION, text)

    def test_the_chat_calls_off_an_ask_of_pilot_s_own_for_the_person_who_says_so(self) -> None:
        _, _, rest = skill_file("chat").read_text().partition("\n## Recording\n")
        recording, _, _ = rest.partition("\n## ")
        _, beside, after = recording.partition(CANCEL_BESIDE)
        self.assertTrue(beside)
        _, _, following = after.partition("\n- ")
        bullet, _, _ = following.partition("\n- ")
        bullet = " ".join(bullet.split())
        for form in CANCEL_BY_THE_CHAT:
            with self.subTest(form):
                self.assertIn(form, bullet)
        recording = " ".join(recording.split())
        for form in (CANCEL_EFFECT, CANCEL_CARRIED_OUT):
            with self.subTest(form):
                self.assertIn(form, recording)
        self.assertIn(CANCEL_TOOL, " ".join(CLAUDE.read_text().split()))

    def test_cancel_ask_is_named_by_the_map_and_the_chat_skill_alone(self) -> None:
        named = {source for source, text in the_map().items() if CANCEL_ASK in text}
        self.assertEqual(named, CANCEL_FILES)


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

    def test_the_plan_s_end_checks_the_handbook_s_result_first(self) -> None:
        _, _, rest = skill_file("plan").read_text().partition("\n## What is next\n")
        mode, _, _ = rest.partition("\n## ")
        text = " ".join(mode.split())
        for form in PLAN_END_RESULT_FIRST:
            with self.subTest(form):
                self.assertIn(form, text)

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

    def test_the_finish_decision_offers_finish_and_archive_which_calls_finish_with_archive(
        self,
    ) -> None:
        _, _, rest = skill_file("plan").read_text().partition("\n## The finish decision\n")
        mode, _, _ = rest.partition("\n## ")
        text = " ".join(mode.split())
        for form in FINISH_DECISION:
            with self.subTest(form):
                self.assertIn(form, text)
        self.assertIn(FINISH_TOOL, " ".join(CLAUDE.read_text().split()))
        for source, page in the_map().items():
            for form in FINISH_YES_RETIRED:
                with self.subTest(source=source, form=form):
                    self.assertNotIn(form, " ".join(page.split()))

    def test_a_task_s_title_names_the_task_alone_and_what_it_waits_on_is_a_note(self) -> None:
        rule = (
            f"A task's title names the task alone, in {pilot_module().TITLE_WORDS} words at most:"
            " what it waits on, what follows it and the actions related to it go into a note on"
            " the task"
        )
        self.assertIn(rule, " ".join(CLAUDE.read_text().split()))
        plan = " ".join(skill_file("plan").read_text().split())
        for form in (
            "a task's title naming the task alone",
            "what a task waits on is a note on it",
        ):
            with self.subTest(form):
                self.assertIn(form, plan)
        for form in ("a task's title naming what it waits on", "a task's title names what it is"):
            with self.subTest(form):
                self.assertNotIn(form, plan)
        chat = " ".join(skill_file("chat").read_text().split())
        self.assertIn("each title naming its task alone (`CLAUDE.md`'s invariants)", chat)

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

    def test_with_auto_pilot_off_an_approved_push_is_an_agent_s(self) -> None:
        text = (ROOT / "rules" / "grants.md").read_text()
        _, _, rest = text.partition("\n## In a worker's brief\n")
        on, off = re.findall(r"^```text\n(.*?)^```$", rest, re.MULTILINE | re.DOTALL)
        self.assertIn(PUSH_AFTER_APPROVAL, " ".join(text.split()))
        self.assertIn(PUSH_AFTER_APPROVAL_BRIEF, " ".join(off.split()))
        self.assertNotIn(PUSH_AFTER_APPROVAL_BRIEF, " ".join(on.split()))

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

    def test_a_free_form_work_item_s_own_card_is_closed_by_the_job_after_its_last_turn(
        self,
    ) -> None:
        _, heading, rest = (ROOT / WORK_ITEMS).read_text().partition(f"\n{OWN_CARD_SECTION}\n")
        self.assertTrue(heading)
        section, _, _ = rest.partition("\n## ")
        self.assertIn(OWN_CARD_CLOSED, " ".join(section.split()))

    def test_a_replaced_work_item_is_closed_through_stop_work_with_its_reason(self) -> None:
        _, heading, rest = (ROOT / WORK_ITEMS).read_text().partition(f"\n{REPLACED_SECTION}\n")
        self.assertTrue(heading)
        section, _, _ = rest.partition("\n## ")
        section = " ".join(section.split())
        for form in REPLACED_RULE:
            with self.subTest(form):
                self.assertIn(form, section)
        claude = " ".join(CLAUDE.read_text().split())
        self.assertIn(STOP_TOOL, claude)
        self.assertNotIn(STOP_TOOL_RETIRED, claude)

    def test_the_chat_s_correction_and_the_plan_s_jobs_close_what_they_replace_by_the_rule(
        self,
    ) -> None:
        _, _, rest = skill_file("chat").read_text().partition("\n## Correcting\n")
        correcting, _, _ = rest.partition("\n## ")
        correcting = " ".join(correcting.split())
        for form in (REPLACED_CITED, *REPLACED_BY_THE_CHAT, *DROPPED_BY_THE_CHAT):
            with self.subTest(skill="chat", form=form):
                self.assertIn(form, correcting)
        _, _, rest = skill_file("plan").read_text().partition("\n## In every mode\n")
        every_mode, _, _ = rest.partition("\n## ")
        every_mode = " ".join(every_mode.split())
        for form in (REPLACED_CITED, REPLACED_BY_A_JOB):
            with self.subTest(skill="plan", form=form):
                self.assertIn(form, every_mode)
        for name in WORK_ITEM_SKILLS:
            with self.subTest(name):
                self.assertNotIn(
                    "a line saying what replaced it", " ".join(skill_file(name).read_text().split())
                )


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

    def test_the_brief_names_the_application_s_commit_and_the_build_the_deploy_commit(
        self,
    ) -> None:
        _, _, section = (ROOT / PROMOTE).read_text().partition(f"\n{PROMOTE_SECTION}\n")
        (block,) = re.findall(r"^```text\n(.*?)^```$", section, re.MULTILINE | re.DOTALL)
        block = " ".join(block.split())
        for form in PROMOTE_DEPLOY_COMMIT:
            with self.subTest(form):
                self.assertIn(form, block)
        work_items = " ".join((ROOT / WORK_ITEMS).read_text().split())
        self.assertIn(PROMOTE_BRIEF_COMMIT, work_items)
        self.assertNotIn("the commit to promote", work_items)


class DeferredPromotionTest(unittest.TestCase):
    def test_routing_defers_a_close_out_s_promotion_to_the_running_task(self) -> None:
        text = (ROOT / "rules" / "routing.md").read_text()
        self.assertEqual(text.splitlines().count(PROMOTION_SECTION), 1)
        _, _, rest = text.partition(f"\n{PROMOTION_SECTION}\n")
        section, _, _ = rest.partition("\n## ")
        section = " ".join(section.split())
        for form in (*PROMOTION_ROUTED, PROMOTION_CANCELLED_ROUTED):
            with self.subTest(form):
                self.assertIn(form, section)
        text = " ".join(text.split())
        for form in PROMOTION_POINTED:
            with self.subTest(form):
                self.assertIn(form, text)
        for form in PROMOTION_ROUTED_RETIRED:
            with self.subTest(form):
                self.assertNotIn(form, text)

    def test_the_pass_defers_it_and_claims_it_not(self) -> None:
        text = " ".join(skill_file("pre-rule").read_text().split())
        self.assertIn(PROMOTION_DEFERRED, text)
        self.assertNotIn("a close-out's promotion aside", text)

    def test_what_is_next_starts_it_once_the_run_s_continuation_has_ended(self) -> None:
        _, _, rest = skill_file("plan").read_text().partition("\n## What is next\n")
        mode, _, _ = rest.partition("\n## ")
        text = " ".join(mode.split())
        for form in PROMOTION_DUE:
            with self.subTest(form):
                self.assertIn(form, text)

    def test_a_cancelled_run_s_promotion_is_started_never_and_goes_to_the_operator(self) -> None:
        _, _, rest = skill_file("plan").read_text().partition("\n## What is next\n")
        mode, _, _ = rest.partition("\n## ")
        text = " ".join(mode.split())
        for form in PROMOTION_CANCELLED_DUE:
            with self.subTest(form):
                self.assertIn(form, text)


class ReplyReadTest(unittest.TestCase):
    def test_the_fallback_reads_the_reply_whole_through_get_session_response(self) -> None:
        for name, heading in REPLY_READ_SECTIONS:
            _, found, rest = skill_file(name).read_text().partition(f"\n{heading}\n")
            section, _, _ = rest.partition("\n## ")
            with self.subTest(name):
                self.assertTrue(found)
                self.assertIn(REPLY_READ, " ".join(first_step(section).split()))


class PlacementRuleTest(unittest.TestCase):
    def test_a_placed_worker_runs_on_opus_at_xhigh_and_on_fable_on_a_person_s_word_alone(
        self,
    ) -> None:
        text = " ".join((ROOT / PLACEMENT).read_text().split())
        for form in PLACEMENT_DEFAULTS:
            with self.subTest(form):
                self.assertIn(form, text)
        for form in PLACEMENT_RETIRED:
            with self.subTest(form):
                self.assertNotIn(form, text)

    def test_a_design_is_a_work_item_of_pilot_s_and_a_mockup_the_operator_s(self) -> None:
        _, heading, rest = (ROOT / PLACEMENT).read_text().partition(f"\n{DESIGN_SECTION}\n")
        self.assertTrue(heading)
        section, _, _ = rest.partition("\n## ")
        section = " ".join(section.split())
        for form in DESIGN_THROUGH_PILOT:
            with self.subTest(form):
                self.assertIn(form, section)
        routing = " ".join((ROOT / "rules" / "routing.md").read_text().split())
        for form in DESIGN_ROUTED:
            with self.subTest(form):
                self.assertIn(form, routing)

    def test_infrastructure_access_is_an_ansible_work_item_never_a_new_capability(self) -> None:
        grants = " ".join((ROOT / "rules" / "grants.md").read_text().split())
        for form in INFRA_THROUGH_ANSIBLE:
            with self.subTest(form):
                self.assertIn(form, grants)
        self.assertIn(INFRA_PLACED, " ".join((ROOT / PLACEMENT).read_text().split()))

    def test_the_work_item_s_field_line_carries_the_defaults(self) -> None:
        text = " ".join((ROOT / WORK_ITEMS).read_text().split())
        self.assertIn(WORK_ITEM_DEFAULTS, text)
        self.assertNotIn("names another", text)

    def test_a_brief_hands_work_to_sub_agents_that_name_their_model(self) -> None:
        text = " ".join((ROOT / WORK_ITEMS).read_text().split())
        self.assertIn(WORK_ITEM_SUB_AGENTS, text)

    def test_a_draft_s_rules_name_no_model(self) -> None:
        text = " ".join(skill_file("create").read_text().split())
        self.assertIn(DRAFT_RULES_NAME_NO_MODEL, text)


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

    def test_the_pass_reads_the_debrief_as_the_server_writes_it_or_finds_none(self) -> None:
        lines = skill_file("pre-rule").read_text().splitlines()
        self.assertEqual(lines.count("## The debrief"), 1)
        for form in (*DEBRIEF_IN_THE_BRIEF, DEBRIEF_ABSENT, DEBRIEF_NO_DOCUMENT):
            with self.subTest(form):
                self.assertIn(form, self.text)

    def test_the_pass_makes_nothing_a_notice_a_card_or_a_fieldnote_of_the_debrief(self) -> None:
        for form in DEBRIEF_FATES:
            with self.subTest(form):
                self.assertIn(form, self.text)

    def test_a_card_from_the_debrief_comments_on_an_open_card_on_the_same_change(self) -> None:
        for form in DEBRIEF_OPEN_CARD:
            with self.subTest(form):
                self.assertIn(form, self.text)
        self.assertIn(COMMENT_GRANT, " ".join(CLAUDE.read_text().split()))


class StagesRuleTest(unittest.TestCase):
    def setUp(self) -> None:
        self.text = " ".join((ROOT / "rules" / "stages.md").read_text().split())

    def test_a_card_on_the_debrief_is_the_one_exception_to_a_stage_s_documents(self) -> None:
        for form in (STAGE_DOCUMENTS_NO_CARD, STAGE_DEBRIEF_CARD):
            with self.subTest(form):
                self.assertIn(form, self.text)

    def test_the_stage_s_brief_says_nothing_of_its_debrief_or_of_notices(self) -> None:
        self.assertIn(STAGE_BRIEF_SILENT, self.text)


class OperatorReadsTest(unittest.TestCase):
    def test_a_note_is_the_choice_and_its_reason_and_the_findings_go_to_the_session_log(
        self,
    ) -> None:
        for source in NOTE_RULE_FILES:
            text = " ".join((ROOT / source).read_text().split())
            for form in (NOTE_RULE, FINDINGS_LOGGED):
                with self.subTest(source=source, form=form):
                    self.assertIn(form, text)
        for name in NOTE_RULE_CITING:
            text = " ".join(skill_file(name).read_text().split())
            with self.subTest(skill=name):
                self.assertIn(NOTE_RULE_CITED, text)
                self.assertNotIn(NOTE_RULE, text)
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


class OwnActionClaimTest(unittest.TestCase):
    def test_routing_claims_an_open_action_of_an_item_of_pilot_s_own_that_a_work_item_does(
        self,
    ) -> None:
        text = (ROOT / "rules" / "routing.md").read_text()
        self.assertEqual(text.splitlines().count(OWN_ACTION_SECTION), 1)
        _, _, rest = text.partition(f"\n{OWN_ACTION_SECTION}\n")
        section, _, _ = rest.partition("\n## ")
        section = " ".join(section.split())
        for form in OWN_ACTION_RULE:
            with self.subTest(form):
                self.assertIn(form, section)
        text = " ".join(text.split())
        self.assertIn(OWN_ACTION_SCOPE, text)
        self.assertIn(OWN_ACTION_ROW, text)
        self.assertNotIn(OWN_ACTION_SCOPE_RETIRED, text)

    def test_routing_says_how_long_a_run_holds_a_block_and_the_skills_cite_it(self) -> None:
        text = (ROOT / "rules" / "routing.md").read_text()
        self.assertEqual(text.splitlines().count(HELD_SECTION), 1)
        _, _, rest = text.partition(f"\n{HELD_SECTION}\n")
        section, _, _ = rest.partition("\n## ")
        section = " ".join(section.split())
        for form in HELD_RULE:
            with self.subTest(form):
                self.assertIn(form, section)
        for name, heading in HELD_CITING:
            _, found, rest = skill_file(name).read_text().partition(f"\n{heading}\n")
            cited, _, _ = rest.partition("\n## ")
            with self.subTest(name):
                self.assertTrue(found)
                self.assertIn(HELD_CITED, " ".join(cited.split()))
                self.assertNotIn(HELD_RULE[0], " ".join(cited.split()))

    def test_claude_md_names_it_among_the_claims_and_its_done_as_the_item_s_close(self) -> None:
        text = " ".join(CLAUDE.read_text().split())
        for form in OWN_ACTION_IN_CLAUDE:
            with self.subTest(form):
                self.assertIn(form, text)

    def test_the_chat_and_the_plan_claim_it_by_the_rule(self) -> None:
        for name in OWN_ACTION_CITING_SKILLS:
            with self.subTest(name):
                self.assertIn(OWN_ACTION_CITED, " ".join(skill_file(name).read_text().split()))
        _, _, rest = skill_file("plan").read_text().partition("\n## In every mode\n")
        every_mode, _, _ = rest.partition("\n## ")
        self.assertIn(OWN_ACTION_BY_A_JOB, " ".join(every_mode.split()))
        chat = " ".join(skill_file("chat").read_text().split())
        for form in OWN_ACTION_BY_THE_CHAT:
            with self.subTest(form):
                self.assertIn(form, chat)

    def test_an_action_of_pilot_s_done_closes_an_item_of_its_own_with_no_mark(self) -> None:
        _, _, rest = skill_file("plan").read_text().partition("\n## An action of Pilot's done\n")
        mode, _, _ = rest.partition("\n## ")
        text = " ".join(mode.split())
        for form in OWN_ACTION_DONE:
            with self.subTest(form):
                self.assertIn(form, text)


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
        for path in (
            skill_file("pre-rule"),
            skill_file("plan"),
            skill_file("chat"),
            ROOT / "rules" / "routing.md",
        ):
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
