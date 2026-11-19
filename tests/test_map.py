"""The brain's map as its sessions load it — CLAUDE.md, the rule files and the four skills: each
skill named as its folder and its brief last, the brief read first with the project's state and the
handbook in it, no listing run for what it carries and the state read fresh on a later turn, a
chat's quoted item taken from its message, the format skill cited by
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
starting work cite, the brief the work's own part alone, its grants text appended by PilotApp's
server from the grants' section in the shape that server reads, the job after a worker's turn mapped
to the pass or, where the run left it nothing, to the plan alone, the pass handing on to the plan
with no arguments, the chat's cancel of an ask of Pilot's own by `cancel_ask`'s arguments, the
chat's alone, and a replaced or dropped work item closed through `stop_work`'s `reason`, in that
rule file, which the chat's correction and the plan's jobs cite; and each rule a consolidation gave
one home held there, CLAUDE.md's shared ones among them, the places that restated it pointing at
it; and a conversation with a session outside Pilot: its kind line mapped to the chat skill, the
skill's frame for it, its transcript in chat.md read as a calling session's requests, in CLAUDE.md
and the chat skill, and the work it starts placed by repository, never in its environment, by the
placement rule, which the work item's field line and a stage's brief follow; and the debrief's
notice, the server's, which no `add_item` makes and whose row carries no debrief, read only on a
member's word, the operator reading a debrief in it and behind the Debrief; and Pilot's notes and
alerts: the pre-rule and plan skills saying in the same words that one is written by exception
alone, the pass's note on a block left to a person and the debrief's on the run's open document in
place of a notice, the note on a claimed action left undone written while its run holds it, the job
an offer's taking places, by its kind line, starting the work and writing nothing on the block,
CLAUDE.md naming the two tools and the notes in timeline.json, and the chat reading a block with
its note."""

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
# The project's state and the handbook in a brief, as PilotApp's BriefService writes them (its
# `_state`: `_seqs`, TASKS_HEADING, ITEMS_HEADING, NOTES_HEADING, `_return_list` and
# HANDBOOK_HEADING; a heading that quotes a pilot.py listing is cut at its comma): every brief's
# but the definition chat's, a job's with its seqs, a job on a task with its return list.
STATE_SEQS = "`This job is seq <n> on the timeline; the item its trigger names, seq <m>.`"
STATE_TASKS = "`The plan's tasks not done, in its order, …`"
STATE_ITEMS = "`The open items, …`"
STATE_NOTES = "`The open plan notes, whole, …`"
STATE_RETURN_LIST = "`Your return list, …`"
STATE_HANDBOOK = "`The project's handbook, handbook.md, whole:`"
STATE_IN_THE_BRIEF = {
    "plan": (STATE_SEQS, STATE_TASKS, STATE_ITEMS, STATE_NOTES, STATE_RETURN_LIST, STATE_HANDBOOK),
    "pre-rule": (STATE_SEQS, STATE_TASKS, STATE_ITEMS, STATE_NOTES, STATE_HANDBOOK),
    "chat": (STATE_TASKS, STATE_ITEMS, STATE_NOTES, STATE_HANDBOOK),
}
STATE_SKILLS = tuple(sorted(STATE_IN_THE_BRIEF))
# On the turn the brief opens, the skills and the map take the state and the handbook from it: no
# listing is run for what it carries, and no skill reads the handbook's file first (the operator's
# "State and handbook", 2026-11-17, on P-402).
BRIEF_FIRST = "Read the brief, below:"
NO_LISTING = (
    "no `pilot.py plan task list`, `pilot.py plan note list` or `pilot.py items list --open` is run"
    " for what"
)
NO_HANDBOOK_FIRST = "`handbook.md` is not read first"
STATE_IN_THE_MAP = (
    "The brief carries the project's state and its handbook, in every kind but the definition chat,"
    " whose draft has none",
    "a part with nothing in it is left out, its heading too",
    "On the turn the brief opens you read them there",
)
# The steps and passages that read the store for what a brief now carries.
STATE_RETIRED = (
    "Read `handbook.md` before",
    "are read before you write",
    "a read away",
    "open notes by summary",
    "open notes, by summary",
    "The server inlines nothing",
    "scanned through `pilot.py plan task list`",
    "lists as the plan's",
)
# A later turn of a session carries no brief and no state (BriefService's `message_from` and
# `wait_follow_up`, ChatService's `_send`), so what it acts on is read fresh through the listings,
# never taken from the opening brief: in the map, and in each skill for the later turns it has.
LATER_TURN_IN_THE_MAP = (
    "The brief's state is the record's as the brief was composed, and it serves the turn the brief"
    " opens.",
    "A later turn of the session — a chat's later message, a wait's run resumed, a turn of Pilot's"
    " server — carries no brief and no state",
    "what such a turn acts on is read fresh, through `pilot.py plan task list`,"
    " `pilot.py plan note list` and `pilot.py items list --open`, never taken from the opening"
    " brief.",
)
LATER_TURN = {
    "plan": (
        "- **A later turn** carries no brief and no state: a wait's run resumed on another firing,"
        " a turn of Pilot's server, and a chat's later message, on which `/chat` carries out What"
        " is next.",
        "so what such a turn acts on is read fresh — `pilot.py plan task list`,"
        " `pilot.py plan note list`, a task's alone with"
        " `pilot.py plan note list --task <task id>`, and `pilot.py items list --open` — never"
        " taken from the opening brief's state.",
        "with no brief and no state, so that steps 1 and 2 read the notes and the open items fresh"
        " (In every mode's A later turn)",
        "one of the open notes the brief's return list names, and on a later firing's turn"
        " `pilot.py plan note list --task <task id>`",
        "the brief's on the turn it opens and `pilot.py items list --open` on a later firing's",
    ),
    "pre-rule": (
        "A later turn of this session, one of Pilot's server, carries no brief and no state: what"
        " it acts on is read fresh through those three, never taken from the brief above it",
    ),
    "chat": (
        "A later message carries no brief and no state: what it has you act on is read fresh"
        " (Reading's A later message).",
        "- **A later message** carries no brief and no state: at most the server's notice, the item"
        " it quotes and the line naming its author.",
        "is read fresh, through `pilot.py plan task list`, `pilot.py plan note list` and"
        " `pilot.py items list --open`, never taken from the opening brief's state",
    ),
}
# A listing a skill quotes stands in a passage that says which turn runs it, or what it reads that
# the brief leaves out: never a read of the state on the turn the brief opens.
LISTING = re.compile(r"`pilot\.py (?:plan task list|plan note list|items list)[^`]*`")
LISTING_PLACED = (
    NO_LISTING,
    "read fresh",
    "on a later firing's",
    "what the brief leaves out",
    "as `pilot.py items list` prints it",
)
# The handbook's file is read again by the chat on the server's notice that it changed (D052),
# which a later message opens with.
HANDBOOK_AGAIN = (
    "and after the server's `<store_notification>` that the handbook changed, when it has one:"
    " read `handbook.md` again then, before you answer",
    "`handbook.md` is read again on the server's notice that it changed (step 3)",
)
HANDBOOK_AGAIN_IN_THE_MAP = (
    "The one it sends says the handbook changed since your last turn: read `handbook.md` again"
    " before you answer."
)
# A wait's later firing reads the handbook's file again too: its turn carries no brief, and the
# server's notice rides a chat's turn alone (BriefService's `wait_follow_up`; slice 063's I5).
HANDBOOK_AGAIN_ON_A_LATER_FIRING = (
    "and `handbook.md` is read again before any act, since the server sends such a turn no notice"
    " that it changed."
)
# A project chat's message that quotes an item or a block carries the item as it stands, on its
# opening brief and on a later turn alike (BriefService's `quoted`, QUOTED_HEADING and
# QUOTED_BLOCK_HEADING, the item of the message's first tag, ChatService's `_quote`), and the
# opening brief what changed since the latest earlier chat closed (CHANGED_HEADING).
QUOTED_IN_THE_MESSAGE = (
    "The item the message's first tag names, an item's or a block's, comes in the message itself,"
    " the brief's and a later one's alike, before the line naming its author and the words",
    "`The item the message quotes, as it stands now:`",
    "`The item whose block <local id> the message quotes, as it stands now:`",
    "then the item's line as `pilot.py items list` prints it, open or"
    " `done <at> (<cause> by <handle>)`",
    "`<local id> · <kind>[ · <its section's heading>] · <answer line>`",
    "no `pilot.py items list` and no read of `timeline.json` finds it",
    "A further tag's item the message does not carry: `pilot.py items show <id>` reads it.",
    "after the item the words quote, as it stands, when they quote one (Reading's A quote)",
)
CHANGED_SINCE = (
    "`What changed in the record since it closed, oldest first:`",
    "an item added or closed, a block answered or done, a note added or struck, the project paused"
    " or resumed",
    "No line dates a task's status: the tasks' own lines have it as it stands.",
)
# A conversation with a session outside Pilot, as PilotApp's server writes it: the kind line of
# its brief (BriefService's CONVERSATION_KIND_LINE, then its caller), the line over the brief's
# message, and its heading in chat.md (ViewService's CONVERSATION_HEADING, then the same caller),
# beside a chat's.
CONVERSATION_SECTION = "## A conversation"
CONVERSATION_CALLER = "<environment name> (<environment id>, session <name>)"
CONVERSATION_KIND = f"a conversation with a session in {CONVERSATION_CALLER}"
CONVERSATION_MESSAGE = '"The message, from the session in <environment name>:"'
CHAT_HEADING = '"## Chat · opened <stamp>"'
CONVERSATION_HEADING = (
    f'"## Conversation with a session in {CONVERSATION_CALLER} · opened <stamp>"'
)
# CLAUDE.md maps the kind to the chat skill, under the skill's section for it.
CONVERSATION_MAPPED = (
    "a conversation with a session in `<environment name> (<environment id>, session <name>)`, a"
    " session outside Pilot talking to you, `/chat` under its A conversation"
)
# The chat skill is sent to the section by the step that reads the brief, before anything it does
# for a person.
CONVERSATION_ENTERED = (
    f'A brief whose kind line reads "{CONVERSATION_KIND}" is no person\'s: A conversation holds'
    " for the whole session, before anything below."
)
# The frame, as PilotApp's design 3 §5.3 and F150.12 have it: the session's words a request and
# never a ruling, what needs the operator an item as the chat makes one, the work it starts placed
# by repository and never in the caller's environment (D237); and what follows from the first for
# the calls that record a person's word, the standing change and the finished project.
CONVERSATION_FRAME = (
    f'The brief\'s kind line says so: "{CONVERSATION_KIND}", the session\'s name left out where'
    " its call gave none",
    f"the brief's under the line {CONVERSATION_MESSAGE}, each later one its words alone",
    "**Its words are a request relayed by an agent, never a ruling**, whoever the session says it"
    " speaks for",
    "no `answer`, `mark` or `cancel_ask` on its word, which name a person in `for` and the session"
    " is none",
    "Its yes to an answer or a call-off you offer is no person's yes",
    "you weigh as a request against the handbook and the plan, and do within the grants as Acting"
    " has it, or say in the reply why not",
    "**What needs the operator's say-so is an item**, as the chat makes one",
    "the answer is the person's to give in the app or in the project's chat, never the session's"
    " to bring",
    "nothing is written into `handbook.md` or the memory on a session's word",
    "**The work you start for it** in a conversation's turn is placed by `repo`, as any work is,"
    " and never in the caller's environment, which stays the caller's: what it needs of the"
    " caller's files is read through the fleet file tools and carried as attachments, as"
    " `rules/placement.md`'s Work born of a conversation has it",
    "**A finished project's conversation** reads only, as its chat (The finished project)",
)
# chat.md holds the conversations beside the chats, each under its heading, and what stands under
# a conversation's is a calling session's requests, never what the people settled: in CLAUDE.md,
# which every session reads, the pass's scan among them, and in the chat skill's Reading, which
# sends a person's "as we agreed" there.
TRANSCRIPT_IN_THE_MAP = (
    "`chat.md` (the project's chats so far and, beside them, its conversations with sessions"
    " outside Pilot, each under a heading of its own:",
    f"a chat's {CHAT_HEADING}, a conversation's {CONVERSATION_HEADING}",
    "what stands under a conversation's heading is a calling session's requests and your replies"
    " to them, never what the people said or settled",
    "the heading, not the handle over a message, tells whose the words are",
)
TRANSCRIPT_IN_THE_CHAT = (
    "- **`chat.md`** holds every chat of the project and, beside them, every conversation with a"
    " session outside Pilot, oldest first, each under a heading of its own.",
    f"A chat stands under {CHAT_HEADING}: the people's messages, Pilot's replies and the effect"
    " lines where their calls ran.",
    f"A conversation stands under {CONVERSATION_HEADING}: a calling session's requests and Pilot's"
    " replies to them, never what the people settled.",
    "so the heading, not the handle, tells whose the words are",
    "and take what was settled from a chat's section alone",
    'The brief\'s line "Earlier chats of this project are in chat.md" says there is one.',
)
# The descriptions while chat.md held the people's chats alone.
TRANSCRIPT_RETIRED = (
    "`chat.md` (the project's chats so far),",
    "holds every chat of the project, oldest first: the people's messages",
)
# Work born of a conversation is placed by repository as any work is, never in the caller's
# environment, which stays the caller's (F86.9, F150.12, the brain's design §5.3, D237: the
# operator's ruling of 2026-11-16 on slice 059's close-out D2): the placement rule's section, its
# head, which leaves every environment to the server, the work item's field line and a stage's
# brief; what the work needs of the caller's files read through the fleet file tools and carried
# as attachments, add_item's `attachments` taking `<environment>:<path>` (PilotApp's
# pilot_mcp/api.py).
CONVERSATION_PLACED_SECTION = "## Work born of a conversation"
PLACED_BY_REPO = (
    "Work born of a conversation — a work item you start in a turn of a conversation with a"
    " session outside Pilot (`/chat`'s A conversation), on what that session asks for, and every"
    " later task of that work — is placed by `repo`, by the two sections above, as any work is,"
    " and never in the conversation's environment, which stays the caller's: no `add_item` of"
    " yours names an `environment`.",
    '"there is no need for the store agent to assign work at all, ever, to my environment"',
    "its files read through the fleet file tools and carried as attachments, `add_item`'s"
    " `attachments` naming each as `<environment id>:<path>`",
    f'the id the one in the brackets of the brief\'s kind line, "{CONVERSATION_KIND}"',
    "a branch it pushed named there, for the work item to fetch",
    "the reply asks it for the files or the branch",
)
# The placement by name the rules held while a conversation's work ran in the caller's
# environment: its section, its add_item call, the server's refusals and the exceptions to it.
PLACED_BY_NAME_RETIRED = (
    "An environment by name",
    "in place of `repo`",
    "runs in the caller's environment",
    "runs in the conversation's environment",
    "unless the handbook says otherwise",
    "which the handbook alone can ask for",
    "whichever session asks for it",
    "its `environment` the conversation's",
)
PLACEMENT_HEAD = (
    "The environment is Pilot's server's to make, one per work item, for work born of a"
    " conversation as for any other (Work born of a conversation)."
)
PLACEMENT_HEAD_RETIRED = "names the conversation's environment in place of a repository"
WORK_ITEM_PLACED = (
    "- `repo`, `owner/Name`, as `rules/placement.md` places it, and `cwd`, its checkout under"
    " `/work`",
    "the environment is Pilot's server's to make, one per work item, and never `environment`, an"
    " environment's id, work born of a conversation included (`rules/placement.md`'s Work born of"
    " a conversation);",
)
STAGE_PLACED = (
    "The work item's `repo` is the slice's repository, a slice a conversation asked for included"
    " (`rules/placement.md`'s Work born of a conversation), its `cwd` that repository's checkout,"
    " `/work/<Name>`"
)
STAGE_PLACED_RETIRED = "started in a conversation's turn"
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
    " fleet call;",
    "its reason read and the plan adjusted",
    "the plan's next step on it — a task started, changed, added or removed as it rules",
)
# The job after a close ran What is next once it had acted on the close: the chat that carries the
# close out takes it whole, so the task an action item unblocks is started and the plan's end is
# reached with no job after the close.
RULING_ACTS_CITED = "so `/plan`'s An item done is yours here, within the grants, its acts on the close"
RULING_THEN_NEXT = (
    "then What is next whole, the task's status set and every task whose inputs are now done"
    " started, as `/plan`'s Starting a task has it, up to the plan's end"
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
    "Past its four offers — the answer you would record, an act you can do yourself, the call-off"
    " of an ask you find obsolete (Recording's An ask the person calls off) and a free-form work"
    " item where a change needs no slice (A change the person asks for) — the chat asks no closed"
    " question of its own",
)
# "Go with your recommendation" is a delegation only where nothing was offered: after Pilot offered
# an answer, a yes to it, those words included, is the person's ruling, its note the one offered,
# in routing's A delegated answer, which the chat and the create skill cite (consolidation review
# R3.1, the operator's "Their ruling after an offer", 2026-11-15).
DELEGATION_AFTER_AN_OFFER = (
    "with nothing offered, Pilot writes the chosen option with `by: agent`",
    "After Pilot offered an answer in the chat, its option and its note, any yes to it, those words"
    " included, is the person's ruling of that option and no delegation, its note the one offered"
    " unless they give words of their own (the operator, 2026-11-15: \"Their ruling after an"
    ' offer", to "A delegation only where nothing was offered").',
)
DELEGATION_CITED = {
    "chat": (
        '- **A delegation** — "your call", "go with your recommendation" — where you offered no'
        " answer, is no answer of theirs",
        "After you offered one, the same words are a yes to it, their ruling, as that section has"
        " it.",
        "or, on a yes to an answer you offered, the note you offered unless they give words of their"
        " own (Acting's Asked about an open block)",
    ),
    "create": (
        '- **A delegation** — "your call", "go with your recommendation" — where you offered no'
        " answer, is no answer of theirs",
        "After you offered one, its option and its note, the same words are a yes to it, their"
        " ruling, its note the one you offered unless they give words of their own, as that section"
        " has it.",
    ),
}
# A small correction the chat makes unasked and says so (P-353, the store's memory note
# small-corrections-unasked; P-194's chat half without it).
SMALL_CORRECTION = (
    "- **A small correction** — to your own wording, a typo, an obvious fix to what you just wrote"
    " — you make in the turn, unasked, and say so in the reply (the operator, 2026-11-05: \"Small"
    " corrections are generally ok.\"): a correction to what the chat itself wrote, within what Not"
    " this skill's and the invariants leave it to write."
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
# What the pass makes of it (F52.4): nothing; only where the operator must know or do something,
# ending with its suggestion (D142, D144), a note on the run's document that has a block and is
# still open after the pass, a notice where none is, `note` refusing a document with no block
# (F168.9); a card, none of a finding a stage's document holds; or a fieldnote, one already there
# for the same friction fine.
DEBRIEF_FATES = (
    "- **Nothing**, where it holds nothing the operator must know or do and nothing to change.",
    "- **A note or a notice**, only where the operator must know or do something",
    "and ending with what you suggest",
    "your note on the run's document that has a block and is still open after the pass, where there"
    " is one, `note` with `item` its id and no `block`",
    "where none with a block is open, a notice through `add_item`, since `note` refuses a document"
    " with no block",
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
    "yours to read with, and to make a card, comment on an open card or close one, make a fleet call"
    " or post to Fieldnotes, where a rule says so"
)
# The debrief's notice (F26.12 to F26.14, P-363): the server places it, so the map names its kind in
# `add_item`'s line as no `add_item`'s, its row carrying no debrief, and the store's list gives it a
# form `add_item` makes none of; a member's word alone reads it, `read` with `for` them, in the
# map's `mark` line and where the chat records a person's Read; and the pass's two lines on where
# the operator reads a debrief name the notice beside the Debrief, where they named it alone.
DEBRIEF_NOTICE_KIND = "debrief_notice"
DEBRIEF_NOTICE_NAMED = (
    "A debrief's notice, the kind `debrief_notice`, is the server's, never made through `add_item`:"
    " placed as a work item whose stage session's debrief completes its subject is done, a slice's"
    ' run carrying its planning\'s debrief with its own, titled "Debrief · <subject>"; its row in'
    " `timeline.json` has no file and none of the debriefs' words, which the operator reads in the"
    " app."
)
ADD_ITEM_FORMS = {"prose", "work", "wait"}
DEBRIEF_NOTICE_READ_BY = {
    "CLAUDE.md": (
        "- `mark`: ",
        (
            "A debrief's notice is read only on a member's word, `read` with `for` them, never on"
            " your own."
        ),
    ),
    ".claude/skills/chat/SKILL.md": (
        "- **Done, Read and Reviewed** a person gives go through `mark` with `for` them",
        (
            "`read` on a notice, and on a debrief's notice, which you read only so, on a member's"
            " word, never on your own;"
        ),
    ),
}
DEBRIEF_READ = (
    "the operator reads it in the debrief's notice and behind the Debrief of the done work item.",
    (
        "Never one that retells the debrief or says the loop went well: the operator reads it in the"
        " debrief's notice and behind the Debrief."
    ),
)
DEBRIEF_READ_RETIRED = (
    "the operator reads it on the done work item, behind its Debrief.",
    "the operator reads it behind the Debrief.",
)
# A worker's brief on a secret: never shown, read back or passed on, and placed only where the brief
# says, so that the worker the grants send to place one is not told it must not handle one
# (consolidation review R1.4, the operator's "New wording", 2026-11-15).
SECRET_IN_THE_BRIEF = (
    "A secret's value is never shown, read back or passed on; you place one only where this brief"
    " says, through the repository's tooling."
)
SECRET_IN_THE_BRIEF_RETIRED = "never yours to handle"
SECRET_IN_THE_BRIEF_RULED = (
    '(the operator, 2026-11-15: "New wording", to "Never shown, read back or passed on, placed only'
    ' where the brief says")'
)
# The chat's Learning writes a "from now on" at once, whoever says it, and the kept column says the
# Learning is outside it (consolidation review R3.2, the operator's "Always at once", 2026-11-15).
LEARNING_OUTSIDE_KEPT = (
    "The chat's Learning is outside it: a standing change a person asks for in the chat, \"from now"
    " on …\", is written at once as `/chat`'s Learning has it, whoever says it (the operator,"
    ' 2026-11-15: "Always at once", to "Learning as it stands, whoever says it").'
)
LEARNING_AT_ONCE = (
    "- **A standing change** the person asks for — \"from now on …\", \"never again …\" — is"
    " written where it belongs"
)
# A change to the rules is a decision whose proposal is the new wording, never a confirmation,
# which has no code for it (consolidation review R1.3, the operator's "A decision", 2026-11-15).
RULE_CHANGE_A_DECISION = (
    "An act that asks, but a change to the rules themselves (below), is a confirmation item",
    "A change to the rules themselves is never a confirmation, and takes no code: there is no act"
    " for the switch to answer. It goes to the operator as a decision whose proposal is the new"
    ' wording, theirs to Agree (the operator, 2026-11-15: "A decision", to "The new wording as its'
    ' proposal, yours to Agree").',
)
# Pilot's own acts on the tracker and on Fieldnotes are never asked, a fleet call keeping its act's
# column, so no confirmation covers a card (consolidation review R1.2, the operator's "Never
# asked", 2026-11-15).
TRACKER_NEVER_ASKED = (
    "- Pilot's own acts on the tracker and on Fieldnotes: a card made, a comment on one, a card's"
    ' close and a Fieldnotes post (the operator, 2026-11-15: "Never asked", to "The tracker and'
    ' Fieldnotes acts join the never-asked list"). A fleet call keeps the column its act falls in.'
)
TRACKER_DONE_AT_ONCE = (
    "where Pilot's own hands do it in the pass — a card, never asked (`rules/grants.md`), or a fleet"
    " call its column lets go. |"
)
TRACKER_CONFIRMED_RETIRED = "a tool call: a card, a fleet call"
# A stage's documents get no card and no fold of the pass's, the stage's continuation carrying out
# their fates; a card on the stage session's debrief is the one exception; and the stage's brief
# says nothing of its debrief or of notices.
STAGE_DOCUMENTS_NO_CARD = "you make no card and fold nothing, or it is done twice"
STAGE_DEBRIEF_CARD = (
    "Two cards stay yours, the exceptions: the stage session's debrief, which the brief after the"
    " turn its loop completed in carries, is no document of the stage's, and a card on it is yours"
    " (`/pre-rule`'s The debrief)",
    "and a finding you defer to the project's end takes its `Later` card, yours too"
    " (`rules/routing.md`'s The `Later` card)",
)
STAGE_BRIEF_SILENT = "no list of what to register, and nothing on its debrief or on notices"
# A hand-over to another project in a stage's document is the answer's card fate naming it, and the
# stage's continuation makes the card (consolidation review R4.3's hand-over, the operator's "The
# stage", 2026-11-15).
HAND_OVER_IN_A_STAGE = (
    "In a stage's document the stage makes it: the hand-over is the answer's `card` fate naming the"
    " other project, and the stage's continuation makes the card, carrying the section's text, marked"
    " chosen by Pilot where Pilot chose (`rules/stages.md`'s A fate in a stage's document; the"
    ' operator, 2026-11-15: "The stage", to "Pilot answers with the card fate, the continuation'
    ' makes the card").'
)
HAND_OVER_CARD_FATE = (
    "- **card**, in the project the proposal or your answer names — a hand-over to another project"
    " among them (`rules/routing.md`'s Another project's decision) — else the slice's own"
)
# Taking a slice: triage's rules for a slice, the definition chat's and the project's chat's alike,
# in the stages' rule file, which both chats cite, create keeping the draft's part, the chat its
# items, its three tasks and a note for the slices it must follow.
TAKING_A_SLICE = "## Taking a slice"
TAKING_A_SLICE_RULES = (
    "A card's diagnosis or cause stays the card's claim. Requirements, not solutions: no fix, no"
    " phases, no acceptance criteria, which the planning grounds.",
    "An ask that contradicts a current decision is an ask of its own: the decision's id and its"
    " ruling quoted, overrule it or drop the ask, with your recommendation.",
    "never one only the code answers, which the planning grounds and asks itself",
    "and the slices it must follow, which its record names",
)
TAKING_A_SLICE_CITED = "`rules/stages.md`'s Taking a slice has it"
# A slice or a work item: the operator's two tests, in the stages' rule file, which the definition
# chat, the chat and the plan weigh a change by before they make it a slice (P-251, the operator's
# "Agree", 2026-11-15, to the four passages as drafted).
SLICE_OR_WORK_ITEM = "## A slice or a work item"
SLICE_OR_WORK_ITEM_RULE = (
    'A slice is for work that needs the whole workflow, and the operator\'s two tests say which: "(1)'
    " more complex (multi step/multi project) and (2) whether checks and balances are needed to"
    ' ensure success" (the operator, P-251). Where either holds, or you cannot tell, the work is a'
    " slice.",
    "Where neither does — one step in one repository, which a session does safely and confidently"
    " and whose result its own check shows — it is a free-form work item off the plan, in a"
    " repository onboarded to the workflow as in any other, and you propose it as one, saying in a"
    " line which test it does not meet.",
    "A project's handbook, or the repository's own instructions, that send every code change through"
    " a slice still bind: there it is a slice, whatever the tests say.",
)
SLICE_OR_WORK_ITEM_WEIGHED = {
    "create": (
        "and needs the whole workflow by `rules/stages.md`'s A slice or a work item, the project is"
        " one slice of it or more",
        "Where it does not, `## The plan` gives it a task of its own, done by a free-form work item,"
        " and the reply says in a line why it is no slice.",
    ),
    "chat": (
        "- **A change the person asks for** in a repository onboarded to the workflow is weighed first"
        " by `rules/stages.md`'s A slice or a work item, one they name a slice included: where it"
        " needs no slice, the reply offers a free-form work item off the plan and says why, its task"
        " added and its work item started on their yes; where it needs one, or they hold to a slice"
        " after the offer, it is a new slice, taken as the definition chat takes one",
    ),
    "plan": (
        "A task you add yourself is a slice's three, its filing, its planning and its run, only where"
        " its work needs the whole workflow by `rules/stages.md`'s A slice or a work item, and a"
        " single task done by a free-form work item otherwise.",
    ),
}
TAKING_A_SLICE_IN_THE_CHAT = "the slices it must follow a note on its filing's task"
# A person's Fable for a task, asked in a draft: quoted on the task's line, carried into its note.
FABLE_IN_A_DRAFT = {
    "create": "Where a person asks for Fable for a task's work in their own words, those words go on"
    " that task's line, quoted, which the setup carries into its note",
    "plan": "as is a person's request for Fable the draft quotes on a task's line",
}
FABLE_PLACED = (
    "a draft's quoted on the task's line in its `## The plan`, which the setup carries into the note"
)
# A wait the person asks for in the chat takes what routing's row gives a wait.
CHAT_WAIT = (
    "with its `step`, its note and its backstop as `rules/routing.md`'s A wait has it, the task it"
    " serves in place of an action's"
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
# The pass's routes by the table's names, each with its command, a research among them, and a block
# left to the operator one step: no answer line, its front matter and Pilot's note on it.
PASS_ROUTES = (
    "- **Answered**, `by: agent`:",
    "a routing ask's fate as `rules/stages.md`'s A fate in a stage's document names it",
    "- **Deferred**,",
    "- **Done at once**,",
    "- **Confirmed first**,",
    "- **Claimed**,",
    "- **Researched**, a block whose choice waits on a fact nobody read that the store does not"
    " hold (`rules/routing.md`'s Due diligence, step 4)",
    "- **Waited on**,",
    "- **Asked of its writer**,",
    "- **Left to the operator**: step 7.",
)
PASS_LEFT = (
    "7. **Left to a person**, a block or more, left to the operator by the table: no answer line is"
    " written on it, and the document stays open",
    "What only Pilot knows of the block (step 3) is your note on it, by exception (Your notes and"
    " alerts)",
)
PASS_RETIRED = ("No edit", "no edit", "overrule a passage of the design record")
ROUTES_NAMED = (
    "| answered: its fate as the answer, in the words of `rules/stages.md`'s A fate in a stage's"
    " document, the reason as the note.",
    "| answered, Pilot's choice, the recommendation or not,",
    "| answered, Pilot's choice, only where",
    "| waited on: the wait, its backstop and its note, the action deferred to its task and any other"
    " block answered naming the wait (A wait). |",
    "| confirmed first: no answer line,",
)
# A requirement Pilot rules only where it can rule it safely: one it cannot, one the due diligence
# leaves in doubt among them, is the operator's, in routing's choice row, which stages cite
# (consolidation review R4.2 and R1.14, the operator's "A condition", 2026-11-15).
REQUIREMENT_SAFELY = (
    "A slice's requirement only where Pilot can rule it safely (the operator, 2026-10-31: \"If it can"
    " rule safely, let it.\"): one Pilot cannot rule safely, one the due diligence leaves in doubt"
    " among them, is left to the operator, with no edit (the operator, 2026-11-15: \"A condition\","
    " to \"A requirement Pilot cannot rule safely is left to you\"). |"
)
REQUIREMENT_SAFELY_CITED = (
    "and left to them where you cannot, one the due diligence leaves in doubt among them, as"
    " routing's choice row has it"
)
REQUIREMENT_SAFELY_RETIRED = "where it is theirs, as routing's last row has it"
# A close-out's ask to correct design/database.md to what was built is Pilot's to accept, auto
# pilot on or off, on the operator's standing word of 2026-11-07, and the stages' rule that keeps
# such an edit for the operator's word names it as its one exception (P-353, the store's memory
# note close-out-handling; the operator's "Absorb with the exception", 2026-11-15).
DATABASE_CORRECTION_ROUTED = (
    "| a close-out's ask to correct design/database.md to what was built — an attribute's line, an"
    " assertion, an entity's note: the record brought in line with the build, the product unchanged"
    " | answered, auto pilot on or off: `Agree`, or the option that makes the edit, the note saying"
    " it stands on the operator's standing word, in at most two sentences.",
    'It is a correction (D015), even where the entry says "on the operator\'s word" (the operator,'
    ' 2026-11-07: "database.md correction asks may always be done … You may always accept these.";'
    ' 2026-11-15: "Absorb with the exception", to "Pilot accepts a database.md correction, and'
    ' stages.md names the exception").',
    "An entry whose ruling picks between behaviours or changes the code is routed by the other rows,"
    " even where one option edits design/database.md; a change to the record's conventions stays in"
    " the grants' kept column. |",
)
DATABASE_CORRECTION_STAGES = (
    "is made on theirs alone: a fix now you chose for it comes back in a new document. The one"
    " exception is a correction of design/database.md to what was built, which the operator's"
    " standing word lets you accept, auto pilot on or off: the fix now you chose for it is made"
    " (`rules/routing.md`'s routes)."
)
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
    "run `/plan`, its mode What is next, in this session, with no arguments",
)
# The hand-on passes no brief: `/plan` is run with no arguments and reads the brief the session
# opened with, so that the pass writes the brief out no second time (P-405).
HAND_ON_NO_BRIEF = (
    "the brief is in this session already, where `/plan` reads it, and it is never passed on or"
    " written out again"
)
HAND_ON_READ = (
    "Entered from `/pre-rule` once its pass is done, in the same session, this skill comes with no"
    " arguments and nothing is below: the brief is the one the session opened with, above, and you"
    " read it there."
)
HAND_ON_RETIRED = ("its arguments the brief", "the brief as you got it", "as the job received it")
# The job after a worker's turn opens on `/plan` where its run left the pass nothing (PilotApp's
# BriefService, `_worker_turn_ended`: `/pre-rule` where the run registered a document, gave a
# debrief or researched a block, else `/plan`, under the same kind line; the job after a writer's
# answer always on `/pre-rule`): CLAUDE.md's map of kinds, the pass's lead, and the plan's first
# step and What is next, which reads the lines such a brief holds with no pass before it (P-405,
# the operator's "Agree", 2026-11-17).
PASS_MAPPED = (
    "a worker's turn ended, `/pre-rule`, then `/plan`, where its run left the pass something — a"
    " document it registered, one whose read failed among them, the stage session's debrief or a"
    " block it researched — and `/plan` alone, with no pass, where it left nothing; its writer"
    " answered, `/pre-rule`, then `/plan`;"
)
PASS_MAPPED_RETIRED = "a worker's turn ended, or its writer answered, `/pre-rule`, then `/plan`"
NOTHING_FOR_THE_PASS = (
    "A worker's turn whose run left the pass nothing — no document registered, no debrief and no"
    " researched block — opens on `/plan` itself, and this skill is not run for it."
)
PLAN_OPENED_ON = (
    "A worker's turn ended whose run left the pass nothing opens on this skill itself, its brief"
    " below, with no pass before it (What is next)."
)
PLAN_START = (
    "A worker's turn ended opens on `/plan` where its run registered no document, gave no debrief"
    " and researched no block.",
    "the work item's line, with its task and its turn's end; `Registered nothing this run.`, with"
    " its final message whole where its turn ended with one; the files attached; and the claimed"
    " actions given to the work item, where it was given any (An action of Pilot's done)",
    'No pass came before it, and no "Pre-ruled:" line: what the turn did is read from those lines.',
)
# The brief of the job after a person's close of an item of Pilot's own as PilotApp's BriefService
# writes it: its kind line and the item's line.
ITEM_DONE_KIND = "`Pilot's brief · an item of yours is done · …`"
ITEM_DONE_LINE = '`The item: <path> (<item id>), <kind> "<title>"[, task <id>] — <close>.`'
# The plan skill's modes, each a section of its own, in the order a job meets them: the setup; the
# three that act before What is next; What is next; a wait's run; the sweep and the finish it leads to.
PLAN_MODES = (
    "## The setup",
    "## An action of Pilot's done",
    "## An item done",
    "## An offer taken",
    "## What is next",
    "## A wait's firings",
    "## The sweep",
    "## The finish decision",
)
# What is next's lead names every way in; its step 1 closes a free-form work item's own card by the
# rule file; its notes are a deferral's, the waits-on and collision notes step 5's; a confirmation
# is the grants' one term; and the sweep and the finish open where step 8 sends them.
WHAT_IS_NEXT_LEAD = (
    "After the pass, entered from `/pre-rule` on a worker's turn ended or the writer answered, with"
    " no arguments, its brief the one this session opened with; on a worker's turn ended whose run"
    " left the pass nothing, opened on by its brief; after An item done and An offer taken; and in"
    " the chat, which carries out in its own turn a close it records (`/chat`)"
)
WHAT_IS_NEXT_FORMS = (
    "A free-form work item's own card is closed then, as `rules/work-items.md`'s Its own card has"
    " it.",
    "2. **A deferral's notes**",
    "a note on what a task waits on, on a collision or on a wait's event is no deferral's: step 5"
    " and A wait's firings read those",
    "5. **Every task whose inputs are done, started**, as In every mode's Starting a task has it.",
    "7. **A confirmation**, where the grants hold the next act — the granted column with the"
    " brief's switch line off, or the kept column: a confirmation item, asked as"
    " `rules/grants.md`'s The confirmation reasons has it.",
    "8. **The plan's end**",
)
WHAT_IS_NEXT_RETIRED = (
    "**A run's open documents.**",
    "a decision whose one block is a confirmation",
)
STEP_8_SENDS = "Where What is next's step 8 sends here"
# The sweep task is plan work, added and started unasked with auto pilot on or off (consolidation
# review R2.1, the operator's "Unasked", 2026-11-15).
SWEEP_TASK_UNASKED = (
    "- or put into a sweep task you scope yourself, added and its work item started unasked, auto"
    " pilot on or off, as any task is: what its work then pushes or promotes is asked as any task's"
    ' would be (the operator, 2026-11-15: "Unasked", to "The sweep task is plan work, added and'
    ' started either way").'
)
SWEEP_TASK_RETIRED = "Add a sweep task covering these"
# Starting a task, one passage in In every mode, which the setup, What is next, a wait's Over and the
# chat cite: the task set going as its work item starts (consolidation review R2.6 and R2.7, the
# operator's "One passage", 2026-11-15).
STARTING_A_TASK = (
    "- **Starting a task**: every task whose inputs are done and that waits on nothing the plan says"
    " it waits on gets its work item, in an environment of its own, all at once",
    "and is set going as its work item starts, `pilot.py plan task set <task id> --status"
    " in_progress`, never a job later",
    "Each run waits only on its own documents: the task a finished document unblocks is started at"
    " once, whatever other runs still wait on theirs.",
    "A task with no repository to work in places no work item: an act of a person's hands is an"
    " action item for them, exact; a task that waits stays pending.",
    '(the operator, 2026-11-15: "One passage", to "Starting a task once, the wait\'s note struck and'
    ' the status set")',
)
STARTING_A_TASK_CITED = "as In every mode's Starting a task has it"
STARTING_A_TASK_CITING = ("## The setup", "## What is next")
# Pilot's `done` on the last open block of an item of its own is the item's close (PilotApp's
# RecordService.done_by_its_save), with no `mark` after it; an answer of its own closes nothing,
# and a registered document, a worker's, still closes by Pilot's own `mark`.
OWN_ITEM_CLOSED = (
    "done, by a work item's run or your own hands, it takes its `done`",
    "Where that was the item's last open block, every other one answered, deferred or done, that"
    " `done` is the item's close, yours, as `CLAUDE.md`'s `mark` has it: no `mark` follows it, and"
    " the server refuses one, and the item leaves the operator's queue",
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
# With auto pilot off, an action of the granted column, a run's held push above all, goes to the
# operator as a confirmation, and on their Yes Pilot claims it for the work item that does it; a
# close-out's promotion stays deferred, its confirmation asked when it is due (consolidation review
# R1.1 and R4.1, the operator's "Confirmation, then an agent", 2026-11-15).
HELD_PUSH_ROUTED = (
    "| an action of the granted column while auto pilot is off — a run's held push above all |"
    " confirmed first: no answer line, and a confirmation item asked for it, `because`"
    " `auto-pilot-off` (`rules/grants.md`'s The confirmation reasons), naming the block,"
    " `<item id>/<local id>`; on its Yes, claimed for the work item that does it (The claim), never"
    ' left for the operator\'s hands (the operator, 2026-11-15: "Confirmation, then an agent", to "On'
    ' your Yes Pilot claims the action and a work item does it").',
    "A close-out's promotion takes its own row, its confirmation asked when it is due. |",
)
HELD_PUSH_STAGES = (
    "the close-out carries each held push as an action, the granted column's: put to the operator as"
    " a confirmation and, on their Yes, made by a work item of Pilot's, never by them",
    "An `action` is one only a person's hands do, or a held push (above)",
)
HELD_PUSH_PASS = (
    "- **Confirmed first**, an action of the granted column while auto pilot is off, a run's held"
    " push above all: no answer line, and a confirmation item through `add_item`",
    "the job after its close claims it on its Yes (`/plan`'s An item done)",
)
HELD_PUSH_CLAIMED = (
    "a worker's block it names, a held push above all, claimed on that work item's `add_item`"
    " (`rules/routing.md`'s The claim)"
)
HELD_PUSH_RETIRED = "the close-out carries each held push as an action."
# The claim route's row, which points at the section and writes the claim out no more.
OWN_ACTION_ROW = "claimed, unless the row after takes it (The claim). Done at once"
# The rule's head while it routed what a worker registered alone.
OWN_ACTION_SCOPE_RETIRED = "and what each route writes. The route is"
OWN_ACTION_CITED = "as `rules/routing.md`'s The claim has it"
OWN_ACTION_CITING_SKILLS = ("chat", "plan")
OWN_ACTION_IN_CLAUDE = (
    "`rules/routing.md` (where an open block goes: the routes, the claim, of a worker's document or"
    " of an item of yours, a block a run holds,",
    "`claims` the actions you claimed that it does, of a worker's document or of an item of yours,",
    "An item of yours closes at the `done` of its last open block, a claimed action's included,"
    " with no undo and no `mark` after it, which the server refuses.",
)
# After the work's turn, the plan writes the `done` and marks a worker's document Done; an item of
# its own takes no `mark`, its `done` its close.
OWN_ACTION_DONE = (
    "Its path is a worker's document's, in `inbox/`, or an item of yours, in `items/`.",
    "Then a worker's document is marked Done where that was its last open block",
    "An item of yours takes no `mark` (In every mode).",
)
# The plan's every mode and the chat's work claim it on the work item's add_item.
OWN_ACTION_BY_A_JOB = (
    "- **An action of an item of yours**, an open action of an item you added: handed to a work"
    " item, one you put to the operator among them, it is claimed on that work item's `add_item`"
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
    "`pilot.py plan task set <task id> --status done`",
    "`pilot.py plan note strike <note id>`",
    "`pilot.py plan note add --task <task id> --summary <line> --ref <item id>/<block id> <content>`",
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
# turn ends, which retries it or writes its note on the block while its run still holds it (F21.6;
# the planning ruling on slice 062's D1, "Let the job write it"); one the brief gives as handed back
# is theirs, and nothing is written of it.
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
# A run whose resume waits on work Pilot knows about has the blocks the pass would settle left
# unanswered and held through that work's run, as a researched block is: a due promotion's, named
# in its work item's `researches` by What is next (PROMOTION_DUE); the pass neither settles nor
# marks the document Done, and routes the blocks once that run is done with them (P-282, the
# operator's "Hold the block", 2026-11-16, Pilot v1.1 task t19).
RESUME_SECTION = "## A resume that waits on work"
RESUME_RULE = (
    "A run that must not resume before work Pilot knows about has done its part — a close-out's"
    " promotion that is due, which the handbook's rules on other work running held back while this"
    " run's turn ran and which its end lets go, the handbook holding the project's new starts while"
    " it is owed — has the blocks of its document that the pass would settle left unanswered and"
    " held through that work's run, as a researched block is (the operator, 2026-11-16: \"Hold the"
    ' block", P-282):',
    "- **A due promotion**: the blocks left for What is next, which names them in the `researches`"
    " of the promotion's work item as it starts it (`/plan`'s What is next, step 3).",
    "- **The note** on that work's task says what comes between, where anything does, which the job"
    " after its turn does before the pass routes the blocks.",
    "- **The person's blocks** are left to them as ever: a block the table leaves to a person is"
    " never held, so that they can answer it while the work runs.",
)
RESUME_PASS = (
    "In a run whose resume waits on work, a block you would settle is left unanswered for it (step"
    " 6).",
    "A run whose resume waits on work (`rules/routing.md`'s A resume that waits on work) is not"
    " settled whole: the blocks you would settle are left unanswered for that work, as that section"
    " has it, and the document is not marked Done.",
    "A block held for work its run's resume waits on is found once that work's run is done with it:"
    " do first what the note on that work's task says comes between, then route the block as the"
    " pass would have.",
)
CLAIM_HANDED_BACK = (
    "**Left undone**, its act refused or never reached in a turn that registered no document with"
    " a block in it: the claim stays and the block open, the operator's once this job ends",
    "the operator gets it with the reason: your note on the block, `note` with `item` its"
    " document's id and `block` its id, `<item id>/<local id>`",
    "You write it in this job, while the run still holds the block, which `note` takes from the job"
    " after a turn of that run alone",
    f"**Handed back to the operator** — its line ending `{HANDED_BACK}`",
    "nothing is written, no Done, retry or note",
)
# The notice the job sent the operator on a claimed action left undone, before the note.
CLAIM_NOTICE_RETIRED = "a notice of yours quoting the block's words"
# A claimed action whose claim is gone was taken back by whoever took the claim off: the operator's,
# nothing written (consolidation review R2.2, the operator's "Yours, nothing written", 2026-11-15).
CLAIM_GONE = (
    "6. **Its claim gone** — its line ending `open, its claim gone`, open with no answer at all now:"
    " no step of yours takes a claim off, so whoever did took the action back. It is the operator's,"
    " and nothing is written, no Done, retry, note or new claim (the operator, 2026-11-15: \"Yours,"
    ' nothing written", to "No retry, no notice, no new claim").'
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
    "`rules/routing.md`'s A wait has it",
    "on a fresh read through youtrack of the card it watches",
)
# A backstop's title, by which a card wait's backstop is told from a timed wait a person asked
# for on the same task.
BACKSTOP_TITLE = "its title `Backstop: <the card wait's title>`"
# One routing section holds a wait: the arming, the backstop, the note on the task and the block's
# write, an action deferred to its task and any other block answered naming the wait, a deferred
# action taking its `done` once the work has done it (consolidation review R1.10 and R4.6, the
# operator's "One section, the action deferred", 2026-11-15).
WAIT_SECTION = "## A wait"
ROUTING_WAIT = (
    "- **The wait**, through `add_item`, its `step` the task the action belongs to: a `card_wait`"
    " armed on a fresh read of the card it watches, or a `timed_wait` with its `due_at`",
    "- **The backstop**: a timed wait beside a card wait that outlives the plan's horizon, its"
    f" `step` the same task and {BACKSTOP_TITLE}",
    "- **The note** on that task, naming the wait and saying what is to happen once its event comes",
    "- **The block's write**: an action deferred to its task, through `pilot.py defer`, whose plan"
    " note is that note; any other block answered naming the wait, through `pilot.py answer`, and"
    " the note added beside it",
    "- **Its `done`**: deferred, an action still takes its `done` once the event has come and the"
    " work has done it, `pilot.py done` — in the wait's run where Pilot's own hands do it, and where"
    " a work item does it, by the job after that work's turn, the note standing until then",
    '(the operator, 2026-11-15: "One section, the action deferred", to "A wait written once, an'
    ' action always deferred to its task")',
)
WAIT_DEFERRED_DONE = (
    "So are the actions deferred to a wait after the turn of the work item its Over started, by the"
    " note standing on its task (`rules/routing.md`'s A wait)."
)
WAIT_RETIRED = ("the block answered naming the wait. |", "routing's row for an owed action")
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
    "**The backstop**, as `rules/routing.md`'s A wait arms one beside a card wait that outlives the"
    " plan's horizon, where it has none open that has not fired at its due time",
    "**Over**, its event come: the action after it started — a work item, as Starting a task starts"
    " one, its task set going, or your own hands' act — and the note beside it on the task struck,"
    " `pilot.py plan note strike <note id>`, but for one that names an action deferred to the wait:"
    " that takes its `done` once done, as `rules/routing.md`'s A wait has it",
    "its note standing until the job after the work's turn writes it and strikes the note",
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
# What only Pilot knows of an ask left to a person stands on the ask, by exception (F168, F168.9,
# P-388, the operator's "Exceptions only", 2026-11-16): the pre-rule and plan skills say it in the
# same words — the note through pilot-store's `note`, on a block or on the document as a whole, and
# the alert through `alert` (PilotApp's pilot_mcp/tools.py); the three things a note is for and the
# alert's one; what is never written, in the operator's words; the replace and the take-off; a note
# that cannot wait marking its document urgent, the turn to urgent alone alerting again (F168.8);
# and the notice kept for news with no open document to sit on.
NOTE_EXCEPTION_LEAD = "**Your notes and alerts, by exception.**"
NOTE_EXCEPTION_END = "A notice stays for news with no open document to sit on."
NOTE_EXCEPTION = (
    "What only you know of an ask left to a person stands on the ask, where they answer it, never in"
    " a notice after its document: your note on the block, `note` with `item` the document's id and"
    " `block` the block's id, `<item id>/<local id>`, or without `block` on the document as a whole,"
    " `text` alone; and your alert on the document, `alert`.",
    "its text and fence stay the writer's, and nothing of it goes back to the writer.",
    "A block with nothing of yours on it is the normal case, and you write one only for one of these:",
    "- **An answer you would give otherwise** than the writer recommends: `suggested_answer`, with"
    " the `suggested_note` you would write beside it",
    "takes the recommendation away, the document's Send waiting on the person's answer to that"
    " block; where you would give the recommendation, you suggest none.",
    "- **A fact the document does not say** that could change the answer",
    "- **Work you would do** about an open action on the person's word, the action itself or"
    " something beside it: `offer`, in a line.",
    "- **An alert**, where the document's Send starts work that another open ask must come before:"
    " `awaits` that ask, `<item id>/<local id>`, and `text`, what to answer first and what the Send"
    " starts.",
    "Never one to say a block is fine, that a check came out well or that you agree, and never one"
    ' that retells the document — the operator, 2026-11-16, of "notices basically explaining that'
    " it's just fine, or that pilot checked this with that and saw it was good and stuff like that\":"
    ' "Exceptions only. Otherwise it becomes noise in no time."',
    "a call with none of `text`, `suggested_answer`, `suggested_note` and `offer` takes it off",
    "A note written once the document is the person's is read as any other, nothing marking it new:"
    " where it cannot wait for them to open the document, `urgent: true` in its front matter alerts"
    " them again, the turn to urgent alone, so that on a document urgent already it alerts no one.",
    NOTE_EXCEPTION_END,
)
NOTE_SKILLS = ("pre-rule", "plan")
# The pass's note on a block left to a person (F52, F168.1), the pre-rule half of P-194's notice,
# which it replaces: what only Pilot knows of the block, beside the document's text, the answer it
# would give suggested only where it would answer otherwise, no note where it would give the
# recommendation and knows nothing more, and no notice after the document; the pass reads the notes
# standing on a document first.
PASS_NOTES = (
    "on a block left to a person, into your note on the block (step 7), beside the document's text"
    " and never in it",
    "`note` with `block` its id, the answer you would give suggested only where you would answer"
    " otherwise than the writer recommends, the fact alone where you know something that could"
    " change the answer, and no note where you would give the recommendation and know nothing more",
    "What the document as a whole needs said that it does not show is your note without `block`;"
    " where its Send starts work another open ask must come before, your `alert` on it.",
    "No notice of yours follows the document.",
    "prints its line and its blocks with their answer lines, and your notes and alert standing on it",
)
PASS_NOTICE_RETIRED = (
    "into a notice of yours after the document",
    "ending with the answer you suggest and the note for it",
)
# The job an offer's taking places (F168.7, F59; PilotApp's brief_service.py, OFFER_TAKEN_KIND and
# `_taken`): its kind line, the offer's line and the note's fields as taken; the mode starts the
# offered work as any work item and writes nothing on the block, the action staying the person's
# (the operator, 2026-11-16).
OFFER_TAKEN_KIND = "`Pilot's brief · an offer of yours was taken · …`"
OFFER_TAKEN_LINES = (
    '`The offer, on action <local id> of <path> (<item id>), <kind> "<title>"[, task <id>]:`',
    '`Your note: "…"`, `Your suggested answer: "…"` and `Your suggested note: "…"`',
    '`Your offer: "…"`',
    "`Taken by <handle> at <time>.`",
)
OFFER_TAKEN_WORK = (
    "Do what it offered, then What is next:",
    "1. **The work, started**: one work item doing what the offer said, added and placed as any is"
    " (`rules/work-items.md`, `rules/placement.md`)",
    "and saying that the action is the person's",
    "2. **Nothing on the block**: the action stays the person's, with its Done. No `claims` names it,"
    " and no answer, `done`, note or mark is written on it",
)
OFFER_TAKEN_MAPPED = "an offer of yours taken, a wait fired `/plan`"
# Pilot's notes in CLAUDE.md's map (F86.10, F86.11, F74.2): pilot-store's two tools by their
# arguments (PilotApp's pilot_mcp/tools.py), one written by exception as the skills say, a block a
# run holds noted by the job after a turn of that run alone (the planning ruling on slice 062's D1,
# "Let the job write it"), and what each prose item's row in timeline.json carries of them
# (PilotApp's engine/views.py, `_notes`).
NOTES_IN_THE_MAP = (
    "- `note`: your note on an ask of an open document, a person's to answer, `block` its id, or"
    " without `block` on the document as a whole, `text` alone",
    "`suggested_answer` and `suggested_note`, the answer you would give and its note; `offer`, work"
    " you would do about an open action on the person's word.",
    "a later one in the same place replaces it, and a call with none of the four takes it off.",
    "A block you answered is refused, and so is one a run holds, but in the job after a turn of that"
    " run.",
    "You write one by exception alone, as `/pre-rule` and `/plan` say.",
    "- `alert`: your alert on an open document whose Send starts work that another open ask must"
    " come before, `awaits` that ask, `<item id>/<local id>`, and `text`",
    "a prose item's with your notes and alert standing on it: each note with its block's local id,"
    " or none on the item as a whole, its text, suggested answer, suggested note and offer, whether"
    " the offer was taken, and its time; the alert with the ask it awaits, `<item id>/<local id>`",
)
# The chat reads a quoted block with Pilot's note on it, so that a Discuss on a block reads the
# note (F74.2, the operator's "Can the store agent see it though?", 2026-11-16).
NOTES_READ = (
    "`pilot.py items show <id>` prints the item's line and its blocks with their answer lines, your"
    " note under the block it stands on, and your note on the item and its alert: a block quoted"
    " from the app, a Discuss's, is read with your note on it."
)
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
    "`environment`",
    "`cwd`",
    "`model`",
    "`reasoning_effort`",
    "`step`",
    "`claims`",
    "`researches`",
    "`attachments`",
    "`brief`",
)
# What a brief says by its work's kind, each at home beside that kind's rules, pointed at from the
# brief's section.
WORK_ITEM_BY_KIND = (
    "`rules/placement.md`'s A design",
    "`rules/placement.md`'s The repository, by the work's nature",
    "`rules/routing.md`'s Due diligence, step 4",
    "`rules/stages.md`'s Filing a slice",
)
WORK_ITEM_BRIEF = (
    "The task in a line.",
    "never paste the handbook",
)
WORK_ITEM_SKILLS = ("chat", "plan", "pre-rule")
# The grants text is no part of the brief the brain writes: PilotApp's server appends the block the
# switch selects, read from the store's rules/grants.md as the work item is added, the work's topic
# branch written in (its PilotStoreService.add_item and BriefService.work_item; P-404, the
# operator's "Overrule D056", 2026-11-17). The rule files say so, each skill that starts work says
# its brief is the work's own part alone, and no file of the map has the brain copy the text.
GRANTS_APPENDED = (
    "Pilot's server appends the text below that the switch selects to a work item's brief, read"
    " from this file as the work item is added",
    "the brief you write is the work's own part alone, and holds no copy of it (the operator,"
    ' 2026-11-17: "Overrule D056", to "The server appends the switch\'s text from the store repo;'
    ' the brain writes only the work\'s own part")',
    "A work item whose text it cannot read, the file out of its reach or no block here for the"
    " switch, is refused at its add: none starts without its grants text.",
)
GRANTS_APPENDED_TO_THE_BRIEF = (
    "Pilot's server appends the rest to every work item's brief, a stage's and a promotion's"
    " included: the plan task it serves, the switch with the grants text it selects, read from"
    " `rules/grants.md`'s In a worker's brief, the work's topic branch written into it, and the"
    " handbook.",
    "The brief you write is the work's own part alone: never copy the grants text or write the"
    " work's topic branch into it, and never paste the handbook.",
    "then the task in a line and the ticket, and nothing of what to do",
)
GRANTS_APPENDED_TO_A_STAGE = (
    "the grants text is Pilot's server's to append, as to any work item's brief"
    " (`rules/work-items.md`)"
)
GRANTS_APPENDED_TO_A_PROMOTION = (
    "copied verbatim (`rules/work-items.md`): Pilot's server appends the grants text to the brief,"
    " and nothing of this file"
)
GRANTS_THE_SERVERS = (
    "its brief the work's own part alone, since Pilot's server appends the grants text the switch"
    " selects"
)
GRANTS_COPY_RETIRED = (
    "The grants text the switch selects",
    "copied verbatim from `rules/grants.md`",
    "as it carries the grants",
    "the ticket and the grants text",
    "The brain writes the work's topic branch",
)
# The grants' section as PilotApp's server reads it (its brief_service.py: GRANTS_SECTION,
# SWITCH_LABELS, TOPIC_BRANCH, and the two patterns of `switch_grants`): the section runs from its
# heading to the next line that begins `# ` or `## `, one inside a fenced block included, and a
# position's text is the fenced block right under its label, blank lines alone between. A block the
# server does not find refuses every work item's add under that position of the switch.
GRANTS_SECTION = "## In a worker's brief"
SWITCH_LABELS = ("Auto pilot on:", "Auto pilot off:")
TOPIC_BRANCH = "pilot/<project>/<task>"
GRANTS_SECTION_READ = re.compile(
    rf"^{re.escape(GRANTS_SECTION)}[ \t]*$(.*?)(?=^##? |\Z)", re.MULTILINE | re.DOTALL
)
GRANTS_BLOCK_READ = re.compile(
    rf"^({'|'.join(re.escape(label) for label in SWITCH_LABELS)})[ \t]*\n"
    r"(?:[ \t]*\n)*```[^\n]*\n((?:(?!```)[^\n]*\n)*)```[ \t]*$",
    re.MULTILINE,
)
GRANTS_SHAPE = (
    "The server finds the text by its shape here: this section's heading, then each label alone on"
    " its line, `Auto pilot on:` and `Auto pilot off:`, its fenced block right under it, blank"
    " lines alone between, and no line of a block beginning `# ` or `## `, which ends the section"
    " for the server."
)
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
# one home is the work item's rule file, its two cases, replaced and dropped, which the chat's
# correction and the plan's jobs cite.
STOP_TOOL = (
    "- `stop_work`: a work item's session stopped, running, starting or held, for a person to"
    " resume; a job of yours is refused. With `reason`, a line its done line carries, the work"
    " item is closed for good in the same act, for one you replaced or a person dropped"
    " (`rules/work-items.md`): stopped where it was not, one stopped earlier included, and done as"
    " cancelled, with no Resume and no undo; one that failed is refused."
)
REPLACED_SECTION = "## A work item closed for good"
REPLACED_RULE = (
    "- **Replaced**: another takes its place — the same work started anew, on a brief a correction"
    " or a ruling changed — and it is closed in the turn that adds the other, its `reason` a line"
    " saying what replaced it and why",
    "Either is `stop_work` with `item` its id and `reason`, which its done line carries",
    "It is stopped where it was not, one stopped earlier included, and done as cancelled",
    "takes no Resume and no undo",
    '"Closed · <title>"',
    "The documents its run put to a person stay open and theirs",
    'Without `reason`, `stop_work` only stops, "Stopped · <title>"',
    'One that failed is refused, "it has failed, and keeps its Resume"',
)
REPLACED_CITED = (
    "`stop_work` with `reason`, as `rules/work-items.md`'s A work item closed for good has it"
)
REPLACED_BY_THE_CHAT = (
    "is closed for good where the new one replaces it or the person drops it, never left stopped"
    " beside it",
    "and otherwise stopped, `stop_work` with no `reason`, for them to resume",
    "nothing is said stopped or closed before `stop_work` answered its effect,"
    ' "Stopped · <title>" or "Closed · <title>"',
)
# A work item the person drops in the chat, with nothing in its place, closed for good on their
# word, their words the reason (P-298, the operator's "Agreed", 2026-11-15, widening "Pilot closes
# what it replaces, with its reason" to what a person drops): the rule file's second case.
DROPPED_RULE = (
    "- **Dropped**: a person drops it in the chat, its work no longer wanted with nothing in its"
    " place",
    "it is closed for good on their word: `stop_work` with `reason` their words, never left stopped"
    " for them to close",
    "Only on their word that it is dropped for good: a stop they may resume takes no `reason`.",
)
REPLACED_BY_A_JOB = (
    "A work item you replace with another, its task changed by a ruling or its brief outdated, is"
    " closed for good with it, never left stopped beside it"
)
# The map's line while `stop_work` took no reason.
STOP_TOOL_RETIRED = "running, starting or held; a job of yours is refused"
# A promotion's procedure, at home in one rule file whose text a promotion's brief carries, copied
# by the brain, since the worker runs outside the store (P-184): the job and its parameter,
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
    "A close-out's promotion, auto pilot on or off, goes with the update that follows it, the"
    " store's after a PilotApp promotion, and every action the close-out owes after the promotion —"
    " a criterion's `Settle <id> after …`",
    "with auto pilot off, its confirmation is asked then, and the work item starts on its Yes.",
    "deferred to the running task, never claimed: each through `pilot.py defer`, `--to` the run's"
    " own task, so that the close-out closes once its other blocks are answered and the run's"
    " continuation goes on, and so that the promotion takes the fixes of the run's continuation",
    "the event it waits on is the end of the run's continuation, whose turn a job of Pilot's"
    " follows",
    "They are due once that continuation has ended, the work item that continues the run done after"
    " a turn that registered no document with a block in it; until then their notes stand",
    "One work item then does them all but a criterion owed after an act of Pilot's own (below), the"
    " promotion first, its brief carrying `rules/promote.md`",
)
PROMOTION_POINTED = (
    "| a close-out's promotion, with what follows it, auto pilot on or off | deferred to the running"
    " task, never claimed, its confirmation, with auto pilot off, asked when it is due (A close-out's"
    " promotion). |",
    "| the run's end: a close-out's promotion and what follows it | a note on the running task, due"
    " once the run's continuation has ended (A close-out's promotion) |",
    "A close-out's promotion is the one exception (A close-out's promotion).",
    "A deferral from a close-out, the task's last document, goes to the next task or to the end, but"
    " for its promotion and what follows it, which go to the running task (A close-out's"
    " promotion).",
)
PROMOTION_CITED = "`rules/routing.md`'s A close-out's promotion"
# A criterion owed after an act of Pilot's own in the store stays out of the promotion's work item,
# whose worker cannot see the act: deferred with the act, and settled by the job that does it, in
# the same turn (P-217, the operator's "Same job", 2026-11-15); the pass settles it where it does
# the act at once.
PROMOTION_STORE_ACT = (
    "A criterion the close-out owes after an act of Pilot's own in the store — a handbook line it"
    " rewrites, a memory it removes — stays out of the promotion's work item",
    "It is deferred with that act, wherever the act is deferred, its note naming both blocks.",
    "The job that meets that note does the act and then settles the criterion in the same turn, its"
    " `done` written: after a promotion, the job after the promotion's work item's turn, which reads"
    " the run task's notes; where the pass does the act at once, the pass settles it",
    '(the operator, 2026-11-15: "Same job", to "The job that does the act settles the check in that'
    ' turn")',
)
PROMOTION_STORE_ACT_IN_THE_PASS = (
    "but a criterion owed after an act of Pilot's own in the store, which goes with that act, as"
    " that section has it",
    f"a criterion the close-out owes after that act is settled in the same turn ({PROMOTION_CITED})",
)
# The rule's words while a close-out's promotion was claimed and its deferral barred the run.
PROMOTION_ROUTED_RETIRED = ("goes to the next task or to the end, never to the running task",)
PROMOTION_DEFERRED = (
    "A close-out's promotion, the update that follows it and every action the close-out owes after"
    f" it are deferred so, `--to` the run's own task, never claimed ({PROMOTION_CITED})"
)
PROMOTION_DUE = (
    "**A close-out's promotion**, deferred to the run's own task with what follows it,",
    f"is met only once it is due, as {PROMOTION_CITED} has it: until then its notes stand, neither"
    " acted on nor struck",
    "one work item does them all but a criterion owed after an act of Pilot's own in the store, its"
    " `step` the run's task, the promotion first, the blocks the pass left for it, of a run whose"
    " resume waits on the promotion (`rules/routing.md`'s A resume that waits on work), named in its"
    " `researches`, its brief carrying `rules/promote.md`",
    "an act of Pilot's own deferred with them that job does itself, settling the criterion owed"
    " after it in the same turn",
    "and naming the application's commit read then, its `main` as the continuation left it, never"
    " the commit or the build the close-out's block names, which predate the continuation's fixes",
    "that `main` read on GitHub itself, never through gitblit, a daily mirror that may not hold the"
    " continuation's push yet",
)
# A close-out's promotion's notes stand through its work, and the job after its turn writes the
# `done` of each owed action it did, then strikes them, as An action of Pilot's done does for a
# claim (consolidation review R2.3, the operator's "Notes stand, Done written", 2026-11-15).
PROMOTION_DONE_WRITTEN = {
    "## What is next": (
        "Their notes stand through that work, which gets no second, and the job after its turn"
        " writes the `done` of each action of them it did, as An action of Pilot's done has it,"
        " then strikes them",
    ),
    "## An action of Pilot's done": (
        "After the turn of a close-out's promotion's work item, the actions deferred to the run's"
        " task with it, which the notes on that task name, are read the same way, never claimed:"
        " each the work did takes its `done` as step 2 has it, and the notes are struck after",
        '(What is next, step 3; the operator, 2026-11-15: "Notes stand, Done written", to "The job'
        ' after the promotion writes each Done, then strikes the notes")',
    ),
}
PROMOTION_DONE_ROUTED = (
    "Their notes stand through that work, and the job after its turn writes the `done` of each"
    " action it did, then strikes them, so that the record shows each owed action done."
)
PROMOTION_DONE_ENTERED = (
    "An action of Pilot's done first where the brief names claimed actions or its work item is a"
    " close-out's promotion's"
)
PROMOTION_STRUCK_AT_ITS_START = "and the notes of what it does are struck"
# What is next reads the owed promotions of every task of the plan, and starts one as soon as the
# handbook lets it go, whichever task the job's brief names (P-218, the operator's "Every task",
# 2026-11-15).
PROMOTION_ON_EVERY_TASK = (
    "is read on every task of the plan, never the brief's task alone, the open notes naming each",
    "Then, as soon as the handbook's rules on other work running let it go, whichever task this"
    " job's brief names — with auto pilot off, on its confirmation's Yes (step 7) — one work item"
    " does them all",
    "Held by other work, its notes stand, and the first What is next after the handbook lets it go"
    ' starts it (the operator, 2026-11-15: "Every task", to "What is next reads every task\'s owed'
    ' promotions and starts one once the handbook lets it go")',
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
# What every session shares has its one home in CLAUDE.md, each skill keeping its own clause beside
# a pointer: the server's follow-up turn on a held save, the effect lines a call answers, the facts
# read through the fleet servers, a prose item's fields and an attachment's copy, and the draft's
# exception to the invariants on a person's answer and an ask.
FOLLOW_UP = (
    "A turn of Pilot's server that names a save of yours still held — \"Your save of `<path>` is"
    " held: `<path>:<line>: <message>`. Fix it and end your turn.\" — is no person's either: fix the"
    " file until the report after your write names no line of it, and end the turn."
)
FOLLOW_UP_CITED = (
    "A turn of Pilot's server that names a save of yours still held is `CLAUDE.md`'s The server's"
    " notices."
)
FOLLOW_UP_OWN = {
    "chat": "The chat shows your reply to it as the rest of your last one.",
    "create": "The chat shows your reply to it as the rest of your last one.",
    "plan": "The job is done when that turn ends.",
}
EFFECT_LINES = (
    "Each call answers its effect line, `<verb> · <what>` — \"Answered · D1 · <title>\", \"Marked"
    " done · <title>\", \"Cancelled · <title>\" — which a chat shows where the call ran; a refused"
    " call changes nothing and answers why: say so, with its reason, or fix the call. Say a thing is"
    " recorded only once its call answered so."
)
EFFECT_LINES_CITED = (
    "Each call answers its effect line, as `CLAUDE.md`'s The tools and the scripts has it."
)
READ_ELSEWHERE = (
    "Facts outside the project — a repository's code or history, a card, a tracker's projects, an"
    " environment's files, a session's log, a Fieldnotes post — are read through the fleet servers,"
    " never recalled or guessed",
    "`get_session_log`, which cuts every line at about 80 characters",
)
READ_ELSEWHERE_CITED = "`CLAUDE.md`'s Reading elsewhere has it"
PROSE_ITEM_AND_COPY = (
    "a prose item, its `kind` and `title`, and `step`, `urgent`, `for` and `summary` where they hold,"
    " born with its file",
    "a short one whole as `markdown`, and a person's answer never in its text but `answer`'s, after"
    " the add",
    "every file of one call one batch",
    "A copy is the file as it stood: a change at its source later is not seen.",
)
DRAFT_EXCEPTIONS = (
    "In a draft alone a block may be changed or deleted, answered or not, a person's answer lines"
    " still the record's (`/create`'s The draft).",
    "An ask to a person is an item, never a question in a transcript; in a draft, a block of the"
    " draft (`/create`'s The draft).",
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
# A worker leaves no work committed in its environment alone before the turn that frees it: what
# may not go to its branch yet goes to the work's topic branch, never asked, which the server writes
# into the grants text, the next task's brief names to fetch, and that task deletes once landed
# (P-293, the operator's "Topic branch", 2026-11-15; "Never asked" and "The task deletes it",
# 2026-11-16, Pilot v1.1 task t34).
TOPIC_BRANCH_ENTRY = (
    "- the topic-branch push: before a turn that leaves its environment free to be reset, a worker"
    " pushes what it committed there alone and may not push to its branch yet to the work's topic"
    " branch, `pilot/<project>/<task>`, which no pipeline builds or deploys; the task that takes it"
    " deletes the branch once its work has landed, which loses nothing and is no irreversible act"
    ' (the operator, 2026-11-15: "Topic branch", P-293);'
)
TOPIC_BRANCH_WRITTEN_IN = (
    "The server writes the work's topic branch into it, in place of `pilot/<project>/<task>`: the"
    " project's slug and the plan task's id, or the work's title in kebab case where it serves no"
    " task."
)
TOPIC_BRANCH_PRE_APPROVED = "a push to this work's topic branch, `pilot/<project>/<task>`"
TOPIC_BRANCH_BRIEF = (
    "Before a turn that ends with none of your registered documents open, after which this"
    " environment may be reset, leave no work committed here alone: push what may not go to its"
    " branch yet to the topic branch, and name it in your turn's last line, so that the next task"
    " fetches it."
)
TOPIC_BRANCH_IN_THE_BRIEF = (
    "A task whose input is work an earlier task left on its topic branch, which that task's turn's"
    " last line names, has its brief name the branch, `pilot/<project>/<task>` of the earlier task,"
    " to fetch, and to delete once the work has landed on the branch it was meant for"
    " (`rules/grants.md`'s never-asked list).",
)
# A worker's turn that ends its work follows each push of its own that deploys to its roll with the
# host's track_build.py first, its result in the turn's last line, which the job after the turn
# reads; no wait is armed for it (P-295, the operator's "Worker follows", 2026-11-16, Pilot v1.1
# task t19).
DEPLOY_FOLLOWED_BRIEF = (
    "Follow each push of yours that deploys to its roll first, `track_build.py <job> --hash <sha>`"
    " run in the background, and give its result in that line, so that Pilot's next step starts on"
    " the deploy as it stands."
)
DEPLOY_NO_WAIT = (
    "- **A deploy a worker pushed** is no wait: the worker follows it before its work ends"
    " (`rules/grants.md`'s In a worker's brief), and the job after its turn reads the result in its"
    " last line; a wait is armed only on a build no worker of the project follows (the operator,"
    ' 2026-11-16: "Worker follows", P-295).'
)
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
# work item, the granted column's, never a new capability, in the grants' section on an operator
# action Pilot can run itself; its brief's command, and a secret by its path and key, minted on
# stdin, in placement's section on the work's nature (P-353, the store's memory note
# infra-through-ansible; the operator, 2026-11-03, generalising D121 of 2026-11-02).
OPERATOR_ACTION_SECTION = "## An operator action Pilot can run itself"
INFRA_THROUGH_ANSIBLE = (
    "Infrastructure access Pilot's environments lack — `kubectl exec` or a write on prd, an OpenBao"
    " leaf, a host change — is the same: a work item in `pvginkel/Ansible`, `/work/Ansible`",
    "an operator action Pilot can run itself, the granted column's, and never a new capability for"
    " the app's environments",
    "Its brief, a secret's included, is `rules/placement.md`'s The repository, by the work's"
    " nature.",
)
INFRA_PLACED = (
    "an operator action that needs infrastructure access Pilot's environments lack in"
    " `pvginkel/Ansible`, its `cwd` `/work/Ansible` (`rules/grants.md`)",
    "That work item's brief gives the exact command and says not to work around a failure",
    "what needs another environment checked, Pilot checks itself",
    "For a secret, the brief names its OpenBao path and key, `kv/eso/<stage>/<app>/<stage>/<leaf>`,"
    " and the agent mints the value and writes it on stdin, `bao kv put -mount=kv <leaf> <key>=-`",
    "is their convention for a person at a terminal: for Pilot's work the ruling"
    " `rules/grants.md`'s An operator action Pilot can run itself quotes stands",
)
# The grants' lists by their names, the spec-repo push granted for good where "a standing grant"
# is the kept column's alone.
GRANTS_LISTS = (
    "**Never asked**, outside the table's two columns:",
    "**Granted**, the granted column: asked while auto pilot is off, done under it.",
    "**Kept**, the kept column: always asked, auto pilot on or off.",
    "the spec-repo push, granted for good",
)
# The repository's pick is the judgment the handbook bends, and its example a key that is its own.
PLACEMENT_SCOPE = (
    "`owner/Name`: Pilot's judgment, guided by the two sections below and the project's own facts in"
    " its `handbook.md`, enforced nowhere, and what the project's handbook says of its repositories"
    " comes before their rules",
    "`P (PilotApp)` is `pvginkel/PilotApp`",
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


def switch_grants(source: str) -> dict[str, str] | None:
    """The grants text by its label, as PilotApp's server reads `source`, the grants file: None
    where it finds no section, and a position whose block it does not find left out."""
    section = GRANTS_SECTION_READ.search(source)
    if section is None:
        return None
    grants: dict[str, str] = {}
    for label, block in GRANTS_BLOCK_READ.findall(section.group(1)):
        if block.strip():
            grants.setdefault(label, block)
    return grants


def passages(text: str) -> list[str]:
    """The text's passages, each on one line: a paragraph, or a list's item, a numbered step or
    a bullet, with the lines that continue it."""
    parts = re.split(r"\n[ \t]*\n|\n(?=[ \t]*(?:- |\d+\. ))", text)
    return [" ".join(part.split()) for part in parts if part.strip()]


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


# The verbs that write, each given in CLAUDE.md's list by its usage line; the others by their name.
WRITE_VERBS = {
    "pilot.py answer",
    "pilot.py done",
    "pilot.py defer",
    "pilot.py plan task add",
    "pilot.py plan task set",
    "pilot.py plan task remove",
    "pilot.py plan task move",
    "pilot.py plan note add",
    "pilot.py plan note strike",
    "pilot.py plan set",
}


def pilot_usages() -> dict[str, str]:
    """The usage line `--help` prints for each write verb, without its `usage: ` prefix."""
    module = pilot_module()
    return {
        leaf.prog: " ".join(leaf.format_usage().removeprefix("usage: ").split())
        for leaf in module._leaves(module.build_parser())
        if leaf.prog in WRITE_VERBS
    }


def command_fault(command: str, options: dict[str, set[str]]) -> str | None:
    """Why a quoted pilot.py command line is not one its parser takes — a word after the
    script's name that is no verb of it, or an option its verb does not have; None for one it
    takes. A word after the verb is an option, `--…`, or a placeholder, `<…>`; in a usage line, as
    `--help` prints it, either may stand in `[…]` or beside another as `a|b`."""
    words = command.split()
    verb = max((prog for prog in options if words[: len(prog.split())] == prog.split()), key=len)
    rest = words[len(verb.split()) :]
    named = list(itertools.takewhile(lambda word: not word.startswith(("-", "<", "[")), rest))
    if named:
        return f"`{verb}` has no verb `{' '.join(named)}`"
    flags = [part for word in rest for part in word.lstrip("[").split("|")]
    flags = [part.rstrip("].") for part in flags if part.startswith("--")]
    unknown = [flag for flag in flags if flag not in options[verb]]
    return f"`{verb}` takes no {', '.join(unknown)}" if unknown else None


# CLAUDE.md's map line for each rule file names the sections it holds, in the map's words.
MAP_SECTIONS = {
    "rules/grants.md": ("never asked, granted and kept", "an operator action Pilot can run itself",
                        "the confirmation reasons",
                        "a worker's brief's text, which Pilot's server appends"),
    "rules/routing.md": ("the routes", "the claim", "a block a run holds",
                         "a resume that waits on work", "due diligence",
                         "deferral", "a wait", "a close-out's promotion", "the `Later` card",
                         "a delegated answer", "another project's decision", "the friction half"),
    "rules/work-items.md": ("fields", "brief", "the answer", "its own card", "its close for good"),
    "rules/placement.md": ("by project key", "by the work's nature",
                           "work born of a conversation", "a design",
                           "model and effort"),
    "rules/stages.md": ("the plugin's update", "a slice or a work item", "taking a slice",
                        "filing it"),
}


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

    def test_every_skill_but_create_reads_the_brief_first_and_no_handbook_before_it(self) -> None:
        for name in STATE_SKILLS:
            with self.subTest(name):
                text = skill_file(name).read_text()
                _, body = front_matter(text)
                self.assertTrue(first_step(body).startswith(BRIEF_FIRST))
                self.assertIn(NO_HANDBOOK_FIRST, " ".join(text.split()))
        claude = " ".join(CLAUDE.read_text().split())
        self.assertIn(NO_HANDBOOK_FIRST, claude)
        for source, page in the_map().items():
            with self.subTest(source=source):
                self.assertNotIn("Read `handbook.md` before", " ".join(page.split()))

    def test_claude_md_s_map_names_each_rule_file_s_sections(self) -> None:
        text = " ".join(CLAUDE.read_text().split())
        for path, sections in MAP_SECTIONS.items():
            _, _, rest = text.partition(f"`{path}` (")
            line, _, _ = rest.partition(")")
            for section in sections:
                with self.subTest(path=path, section=section):
                    self.assertIn(section, line)

    def test_claude_md_names_every_skill_by_its_command(self) -> None:
        text = CLAUDE.read_text()
        for name in SKILL_NAMES:
            with self.subTest(name):
                self.assertIn(f"`/{name}`", text)


class BriefStateTest(unittest.TestCase):
    def test_the_skills_read_the_state_and_the_handbook_as_the_server_writes_them(self) -> None:
        for name, forms in STATE_IN_THE_BRIEF.items():
            text = " ".join(skill_file(name).read_text().split())
            for form in forms:
                with self.subTest(skill=name, form=form):
                    self.assertIn(form, text)
        create = " ".join(skill_file("create").read_text().split())
        for form in STATE_IN_THE_BRIEF["plan"]:
            with self.subTest(skill="create", form=form):
                self.assertNotIn(form, create)

    def test_no_listing_is_run_for_what_the_brief_carries_on_the_turn_it_opens(self) -> None:
        claude = " ".join(CLAUDE.read_text().split())
        for form in (*STATE_IN_THE_MAP, NO_LISTING):
            with self.subTest(source="CLAUDE.md", form=form):
                self.assertIn(form, claude)
        for name in STATE_SKILLS:
            with self.subTest(skill=name):
                self.assertIn(NO_LISTING, " ".join(skill_file(name).read_text().split()))
        for source, page in the_map().items():
            for form in STATE_RETIRED:
                with self.subTest(source=source, retired=form):
                    self.assertNotIn(form, " ".join(page.split()))

    def test_a_listing_a_skill_quotes_names_its_turn_or_what_the_brief_leaves_out(self) -> None:
        for name in STATE_SKILLS:
            quoting = [
                passage
                for passage in passages(skill_file(name).read_text())
                if LISTING.search(passage)
            ]
            self.assertTrue(quoting)
            for passage in quoting:
                with self.subTest(skill=name, passage=passage[:60]):
                    self.assertTrue(any(form in passage for form in LISTING_PLACED))

    def test_a_later_turn_reads_what_it_acts_on_fresh(self) -> None:
        claude = " ".join(CLAUDE.read_text().split())
        for form in LATER_TURN_IN_THE_MAP:
            with self.subTest(source="CLAUDE.md", form=form):
                self.assertIn(form, claude)
        for name, forms in LATER_TURN.items():
            text = " ".join(skill_file(name).read_text().split())
            for form in forms:
                with self.subTest(skill=name, form=form):
                    self.assertIn(form, text)

    def test_the_chat_reads_the_handbook_again_on_the_server_s_notice_alone(self) -> None:
        chat = " ".join(skill_file("chat").read_text().split())
        for form in HANDBOOK_AGAIN:
            with self.subTest(form):
                self.assertIn(form, chat)
        self.assertIn(HANDBOOK_AGAIN_IN_THE_MAP, " ".join(CLAUDE.read_text().split()))

    def test_a_wait_s_later_firing_reads_the_handbook_again(self) -> None:
        _, _, rest = skill_file("plan").read_text().partition("\n## A wait's firings\n")
        mode, _, _ = rest.partition("\n## ")
        self.assertIn(HANDBOOK_AGAIN_ON_A_LATER_FIRING, " ".join(mode.split()))

    def test_the_chat_takes_a_quoted_item_from_its_message_and_what_changed_from_its_brief(
        self,
    ) -> None:
        text = skill_file("chat").read_text()
        _, _, rest = text.partition("\n## Reading\n")
        reading, _, _ = rest.partition("\n## ")
        reading = " ".join(reading.split())
        for form in (*QUOTED_IN_THE_MESSAGE[:-1], *CHANGED_SINCE):
            with self.subTest(form):
                self.assertIn(form, reading)
        steps, _, _ = text.partition("\nThe rules it applies:")
        self.assertIn(QUOTED_IN_THE_MESSAGE[-1], " ".join(steps.split()))


class GrantsReadTest(unittest.TestCase):
    """The reader itself: what PilotApp's server finds of a grants file, and what it does not."""

    ON = "Pre-approved: a push to pilot/<project>/<task>.\n"
    OFF = "Pre-approved: reads.\nNot pre-approved: a push.\n"

    def file(self, on: str | None = None, between: str = "\n") -> str:
        return (
            f"# The grants\n\n{GRANTS_SECTION}\n\nWhat a brief carries.\n\n"
            f"Auto pilot on:\n{between}```text\n{self.ON if on is None else on}```\n\n"
            f"Auto pilot off:\n\n```text\n{self.OFF}```\n\n## After it\n\n```text\nNo grant.\n```\n"
        )

    def test_each_label_s_block_right_under_it_is_read_whole(self) -> None:
        self.assertEqual(
            switch_grants(self.file()), {"Auto pilot on:": self.ON, "Auto pilot off:": self.OFF}
        )

    def test_a_block_the_server_does_not_find_is_left_out(self) -> None:
        for name, source in (
            ("a `# ` line in the block", self.file(on="Pre-approved:\n# reads\n")),
            ("a `## ` line in the block", self.file(on="Pre-approved:\n## reads\n")),
            ("a line between the label and its block", self.file(between="\nAs follows.\n\n")),
            ("an empty block", self.file(on="")),
        ):
            with self.subTest(name):
                self.assertNotIn("Auto pilot on:", switch_grants(source))

    def test_a_file_without_the_section_has_no_grants(self) -> None:
        self.assertIsNone(switch_grants(self.file().replace(GRANTS_SECTION, "## In a brief")))


class PassagesTest(unittest.TestCase):
    """The passage split itself: what the listing check reads as one passage."""

    def test_a_paragraph_a_step_and_a_bullet_are_each_a_passage_with_their_lines(self) -> None:
        self.assertEqual(
            passages(
                "A lead\nof two lines.\n\n1. A step\n   that goes on.\n2. Another:\n"
                "   - a bullet\n     of its own.\n   - and one more.\n\n- A last one.\n"
            ),
            [
                "A lead of two lines.",
                "1. A step that goes on.",
                "2. Another:",
                "- a bullet of its own.",
                "- and one more.",
                "- A last one.",
            ],
        )


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
                self.assertNotIn(form, chat)
                self.assertIn(form, item_done)
        self.assertIn(RULING_ACTS_CITED, chat)
        self.assertIn("`rules/promote.md`", chat)
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

    def test_go_with_your_recommendation_after_an_offer_is_the_person_s_ruling(self) -> None:
        _, _, rest = (ROOT / "rules" / "routing.md").read_text().partition(
            "\n## A delegated answer\n"
        )
        section, _, _ = rest.partition("\n## ")
        for form in DELEGATION_AFTER_AN_OFFER:
            with self.subTest(form):
                self.assertIn(form, " ".join(section.split()))
        for name, forms in DELEGATION_CITED.items():
            text = " ".join(skill_file(name).read_text().split())
            for form in forms:
                with self.subTest(skill=name, form=form):
                    self.assertIn(form, text)

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
        self.assertIn(CANCEL_CARRIED_OUT, recording)
        claude = " ".join(CLAUDE.read_text().split())
        self.assertIn(CANCEL_TOOL, claude)
        self.assertIn(CANCEL_EFFECT, claude)

    def test_cancel_ask_is_named_by_the_map_and_the_chat_skill_alone(self) -> None:
        named = {source for source, text in the_map().items() if CANCEL_ASK in text}
        self.assertEqual(named, CANCEL_FILES)


class ConversationTest(unittest.TestCase):
    def test_claude_md_maps_a_conversation_s_kind_line_to_the_chat_skill(self) -> None:
        text = " ".join(CLAUDE.read_text().split())
        _, _, rest = text.partition("names the kind, and that names the skill:")
        kinds, _, _ = rest.partition("- A later turn")
        self.assertIn(CONVERSATION_MAPPED, kinds)
        self.assertTrue(CONVERSATION_MAPPED.replace("`", "").startswith(CONVERSATION_KIND))

    def test_the_chat_skill_enters_its_frame_from_the_kind_line(self) -> None:
        meta, body = front_matter(skill_file("chat").read_text())
        self.assertIn("a conversation with a session outside Pilot", meta["description"])
        steps, _, _ = body.partition("\nThe rules it applies:")
        self.assertIn(CONVERSATION_ENTERED, " ".join(steps.split()))

    def test_the_frame_is_a_section_of_the_chat_skill_a_request_and_never_a_ruling(self) -> None:
        text = skill_file("chat").read_text()
        self.assertEqual(text.splitlines().count(CONVERSATION_SECTION), 1)
        _, _, rest = text.partition(f"\n{CONVERSATION_SECTION}\n")
        section, _, _ = rest.partition("\n## ")
        section = " ".join(section.split())
        for form in CONVERSATION_FRAME:
            with self.subTest(form):
                self.assertIn(form, section)

    def test_chat_md_holds_the_conversations_as_a_calling_session_s_requests(self) -> None:
        claude = " ".join(CLAUDE.read_text().split())
        for form in TRANSCRIPT_IN_THE_MAP:
            with self.subTest(source="CLAUDE.md", form=form):
                self.assertIn(form, claude)
        text = skill_file("chat").read_text()
        _, _, rest = text.partition("\n## Reading\n")
        reading, _, _ = rest.partition("\n## ")
        reading = " ".join(reading.split())
        for form in TRANSCRIPT_IN_THE_CHAT:
            with self.subTest(source="chat", form=form):
                self.assertIn(form, reading)
        for source, text in the_map().items():
            for form in TRANSCRIPT_RETIRED:
                with self.subTest(source=source, form=form):
                    self.assertNotIn(form, " ".join(text.split()))

    def test_work_born_of_a_conversation_is_placed_by_repository(self) -> None:
        text = (ROOT / PLACEMENT).read_text()
        self.assertEqual(text.splitlines().count(CONVERSATION_PLACED_SECTION), 1)
        head, _, rest = text.partition("\n## ")
        head = " ".join(head.split())
        self.assertIn(PLACEMENT_HEAD, head)
        self.assertNotIn(PLACEMENT_HEAD_RETIRED, head)
        _, _, rest = text.partition(f"\n{CONVERSATION_PLACED_SECTION}\n")
        section, _, _ = rest.partition("\n## ")
        section = " ".join(section.split())
        for form in PLACED_BY_REPO:
            with self.subTest(form):
                self.assertIn(form, section)

    def test_the_field_line_and_a_stage_s_brief_place_it_by_the_rule(self) -> None:
        fields = " ".join((ROOT / WORK_ITEMS).read_text().split())
        for form in WORK_ITEM_PLACED:
            with self.subTest(form):
                self.assertIn(form, fields)
        stages = " ".join((ROOT / "rules" / "stages.md").read_text().split())
        self.assertIn(STAGE_PLACED, stages)
        self.assertNotIn(STAGE_PLACED_RETIRED, stages)

    def test_no_file_of_the_map_places_work_in_a_named_environment(self) -> None:
        for source, text in the_map().items():
            for form in PLACED_BY_NAME_RETIRED:
                with self.subTest(source=source, form=form):
                    self.assertNotIn(form, " ".join(text.split()))


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
            OFFER_TAKEN_KIND,
            WAIT_FIRED_KIND,
            "entered from `/pre-rule`",
        ):
            with self.subTest(form):
                self.assertIn(form, text)

    def test_what_is_next_is_opened_on_by_a_turn_that_left_the_pass_nothing(self) -> None:
        plan = skill_file("plan").read_text()
        _, body = front_matter(plan)
        self.assertIn(PLAN_OPENED_ON, " ".join(first_step(body).split()))
        _, _, rest = plan.partition("\n## What is next\n")
        lead, _, _ = rest.partition("\n1. ")
        for form in PLAN_START:
            with self.subTest(form):
                self.assertIn(form, " ".join(lead.split()))

    def test_entered_from_the_pass_the_plan_reads_the_brief_the_session_opened_with(self) -> None:
        _, body = front_matter(skill_file("plan").read_text())
        self.assertIn(HAND_ON_READ, " ".join(first_step(body).split()))

    def test_each_mode_is_a_section_of_its_own_in_the_order_a_job_meets_it(self) -> None:
        lines = skill_file("plan").read_text().splitlines()
        for heading in PLAN_MODES:
            with self.subTest(heading):
                self.assertEqual(lines.count(heading), 1)
        self.assertEqual([line for line in lines if line in PLAN_MODES], list(PLAN_MODES))

    def test_what_is_next_names_its_ways_in_and_its_steps_and_step_8_leads_on(self) -> None:
        plan = skill_file("plan").read_text()
        _, _, rest = plan.partition("\n## What is next\n")
        mode, _, _ = rest.partition("\n## ")
        text = " ".join(mode.split())
        for form in (WHAT_IS_NEXT_LEAD, *WHAT_IS_NEXT_FORMS):
            with self.subTest(form):
                self.assertIn(form, text)
        for form in WHAT_IS_NEXT_RETIRED:
            with self.subTest(form):
                self.assertNotIn(form, " ".join(plan.split()))
        for heading in ("## The sweep", "## The finish decision"):
            _, _, rest = plan.partition(f"\n{heading}\n")
            with self.subTest(heading):
                self.assertTrue(rest.lstrip().startswith(STEP_8_SENDS))

    def test_a_task_is_started_by_one_passage_which_the_modes_and_the_chat_cite(self) -> None:
        plan = skill_file("plan").read_text()
        _, _, rest = plan.partition("\n## In every mode\n")
        every_mode, _, _ = rest.partition("\n## ")
        for form in STARTING_A_TASK:
            with self.subTest(form):
                self.assertIn(form, " ".join(every_mode.split()))
        for heading in STARTING_A_TASK_CITING:
            _, _, rest = plan.partition(f"\n{heading}\n")
            mode, _, _ = rest.partition("\n## ")
            with self.subTest(heading):
                self.assertIn(STARTING_A_TASK_CITED, " ".join(mode.split()))
                self.assertNotIn("all at once", mode)
        self.assertEqual(" ".join(plan.split()).count("--status in_progress"), 1)

    def test_the_sweep_task_is_added_and_started_unasked(self) -> None:
        _, _, rest = skill_file("plan").read_text().partition("\n## The sweep\n")
        sweep, _, _ = rest.partition("\n## ")
        sweep = " ".join(sweep.split())
        self.assertIn(SWEEP_TASK_UNASKED, sweep)
        self.assertNotIn(SWEEP_TASK_RETIRED, sweep)

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
        for form in (*CLAIM_HANDED_BACK, CLAIM_GONE):
            with self.subTest(form):
                self.assertIn(form, text)
        for form in CLAIM_LINE_RETIRED:
            with self.subTest(form):
                self.assertNotIn(form, text)
        self.assertNotIn(CLAIM_NOTICE_RETIRED, text)

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
        for form in (*WORK_ITEM_FIELDS, *WORK_ITEM_BRIEF, *WORK_ITEM_BY_KIND):
            with self.subTest(form):
                self.assertIn(form, text)

    def test_the_grants_text_is_in_the_section_and_the_shape_pilot_s_server_reads(self) -> None:
        text = (ROOT / "rules" / "grants.md").read_text()
        self.assertEqual(text.splitlines().count(GRANTS_SECTION), 1)
        grants = switch_grants(text)
        self.assertEqual(list(grants), list(SWITCH_LABELS))
        for label, block in grants.items():
            with self.subTest(label):
                self.assertEqual(text.splitlines().count(label), 1)
                self.assertIn(TOPIC_BRANCH, block)
        _, _, rest = text.partition(f"\n{GRANTS_SECTION}\n")
        self.assertEqual(
            list(grants.values()),
            re.findall(r"^```text\n(.*?)^```$", rest, re.MULTILINE | re.DOTALL),
        )
        intro, _, _ = rest.partition("```text")
        self.assertIn(GRANTS_SHAPE, " ".join(intro.split()))

    def test_pilot_s_server_appends_the_grants_text_and_the_brief_is_the_work_s_own_part(
        self,
    ) -> None:
        _, _, rest = (ROOT / "rules" / "grants.md").read_text().partition(f"\n{GRANTS_SECTION}\n")
        intro, _, _ = rest.partition("```text")
        for form in GRANTS_APPENDED:
            with self.subTest(form):
                self.assertIn(form, " ".join(intro.split()))
        _, _, rest = (ROOT / WORK_ITEMS).read_text().partition("\n## The brief\n")
        brief, _, _ = rest.partition("\n## ")
        for form in GRANTS_APPENDED_TO_THE_BRIEF:
            with self.subTest(form):
                self.assertIn(form, " ".join(brief.split()))
        self.assertEqual(re.findall(r"^\d+\. ", brief, re.MULTILINE), ["1. ", "2. ", "3. "])
        stages = " ".join((ROOT / "rules" / "stages.md").read_text().split())
        self.assertIn(GRANTS_APPENDED_TO_A_STAGE, stages)
        for name in WORK_ITEM_SKILLS:
            with self.subTest(skill=name):
                self.assertIn(GRANTS_THE_SERVERS, " ".join(skill_file(name).read_text().split()))
        for source, page in the_map().items():
            for form in GRANTS_COPY_RETIRED:
                with self.subTest(source=source, retired=form):
                    self.assertNotIn(form, " ".join(page.split()))

    def test_with_auto_pilot_off_an_approved_push_is_an_agent_s(self) -> None:
        text = (ROOT / "rules" / "grants.md").read_text()
        _, _, rest = text.partition("\n## In a worker's brief\n")
        on, off = re.findall(r"^```text\n(.*?)^```$", rest, re.MULTILINE | re.DOTALL)
        self.assertIn(PUSH_AFTER_APPROVAL, " ".join(text.split()))
        self.assertIn(PUSH_AFTER_APPROVAL_BRIEF, " ".join(off.split()))
        self.assertNotIn(PUSH_AFTER_APPROVAL_BRIEF, " ".join(on.split()))
        for block in (on, off):
            self.assertIn(SECRET_IN_THE_BRIEF, " ".join(block.split()))
        self.assertNotIn(SECRET_IN_THE_BRIEF_RETIRED, text)
        self.assertIn(SECRET_IN_THE_BRIEF_RULED, " ".join(text.split()))

    def test_a_worker_follows_its_deploy_before_its_work_ends(self) -> None:
        text = (ROOT / "rules" / "grants.md").read_text()
        _, _, rest = text.partition("\n## In a worker's brief\n")
        on, off = re.findall(r"^```text\n(.*?)^```$", rest, re.MULTILINE | re.DOTALL)
        for name, block in (("on", on), ("off", off)):
            pre_approved, _, not_pre_approved = " ".join(block.split()).partition(
                "Not pre-approved"
            )
            with self.subTest(name):
                self.assertIn(TOPIC_BRANCH_BRIEF + " " + DEPLOY_FOLLOWED_BRIEF, pre_approved)
                self.assertNotIn("track_build.py", not_pre_approved)
        routing = (ROOT / "rules" / "routing.md").read_text()
        _, _, rest = routing.partition(f"\n{WAIT_SECTION}\n")
        section, _, _ = rest.partition("\n## ")
        self.assertIn(DEPLOY_NO_WAIT, " ".join(section.split()))

    def test_a_worker_leaves_no_work_committed_in_its_environment_alone(self) -> None:
        text = (ROOT / "rules" / "grants.md").read_text()
        table, _, rest = text.partition("\n## In a worker's brief\n")
        never, _, _ = table.partition("**Granted**")
        self.assertIn(TOPIC_BRANCH_ENTRY, " ".join(never.split()))
        intro, _, _ = rest.partition("```text")
        self.assertIn(TOPIC_BRANCH_WRITTEN_IN, " ".join(intro.split()))
        on, off = re.findall(r"^```text\n(.*?)^```$", rest, re.MULTILINE | re.DOTALL)
        for name, block in (("on", on), ("off", off)):
            pre_approved, _, not_pre_approved = " ".join(block.split()).partition(
                "Not pre-approved"
            )
            with self.subTest(name):
                self.assertIn(TOPIC_BRANCH_PRE_APPROVED, pre_approved)
                self.assertIn(TOPIC_BRANCH_BRIEF, pre_approved)
                self.assertNotIn("topic branch", not_pre_approved)
        work_items = " ".join((ROOT / WORK_ITEMS).read_text().split())
        for form in TOPIC_BRANCH_IN_THE_BRIEF:
            with self.subTest(form):
                self.assertIn(form, work_items)

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
        for form in (*REPLACED_RULE, *DROPPED_RULE):
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
        for form in (REPLACED_CITED, *REPLACED_BY_THE_CHAT):
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
                text = " ".join(skill_file(name).read_text().split())
                self.assertNotIn("a line saying what replaced it", text)
                self.assertNotIn("dropped for good", text)


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

    def test_a_promotion_s_brief_carries_the_text_copied_and_its_grants_from_the_server(
        self,
    ) -> None:
        self.assertIn(PROMOTE_BRIEF, " ".join((ROOT / WORK_ITEMS).read_text().split()))
        self.assertIn(
            GRANTS_APPENDED_TO_A_PROMOTION, " ".join((ROOT / PROMOTE).read_text().split())
        )

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
        for form in (*PROMOTION_ROUTED, PROMOTION_CANCELLED_ROUTED, *PROMOTION_STORE_ACT):
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
        for form in PROMOTION_STORE_ACT_IN_THE_PASS:
            with self.subTest(form):
                self.assertIn(form, text)
        self.assertNotIn("a close-out's promotion aside", text)

    def test_what_is_next_starts_it_once_the_run_s_continuation_has_ended(self) -> None:
        _, _, rest = skill_file("plan").read_text().partition("\n## What is next\n")
        mode, _, _ = rest.partition("\n## ")
        text = " ".join(mode.split())
        for form in (*PROMOTION_DUE, *PROMOTION_ON_EVERY_TASK):
            with self.subTest(form):
                self.assertIn(form, text)

    def test_its_notes_stand_through_its_work_and_the_job_after_writes_each_done(self) -> None:
        plan = skill_file("plan").read_text()
        for heading, forms in PROMOTION_DONE_WRITTEN.items():
            _, _, rest = plan.partition(f"\n{heading}\n")
            mode, _, _ = rest.partition("\n## ")
            for form in forms:
                with self.subTest(heading=heading, form=form):
                    self.assertIn(form, " ".join(mode.split()))
        plan = " ".join(plan.split())
        self.assertIn(PROMOTION_DONE_ENTERED, plan)
        self.assertNotIn(PROMOTION_STRUCK_AT_ITS_START, plan)
        _, _, rest = (ROOT / "rules" / "routing.md").read_text().partition(
            f"\n{PROMOTION_SECTION}\n"
        )
        section, _, _ = rest.partition("\n## ")
        self.assertIn(PROMOTION_DONE_ROUTED, " ".join(section.split()))

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
        grants = (ROOT / "rules" / "grants.md").read_text()
        self.assertEqual(grants.splitlines().count(OPERATOR_ACTION_SECTION), 1)
        _, _, rest = grants.partition(f"\n{OPERATOR_ACTION_SECTION}\n")
        section, _, _ = rest.partition("\n## ")
        section = " ".join(section.split())
        for form in INFRA_THROUGH_ANSIBLE:
            with self.subTest(form):
                self.assertIn(form, section)
        self.assertNotIn("bao kv put", grants)
        placement = " ".join((ROOT / PLACEMENT).read_text().split())
        for form in INFRA_PLACED:
            with self.subTest(form):
                self.assertIn(form, placement)

    def test_pilot_s_tracker_and_fieldnotes_acts_are_never_asked(self) -> None:
        grants = (ROOT / "rules" / "grants.md").read_text()
        never, _, _ = grants.partition("**Granted**")
        self.assertIn(TRACKER_NEVER_ASKED, " ".join(never.split()))
        routing = " ".join((ROOT / "rules" / "routing.md").read_text().split())
        self.assertIn(TRACKER_DONE_AT_ONCE, routing)
        for source, text in the_map().items():
            with self.subTest(source):
                self.assertNotIn(TRACKER_CONFIRMED_RETIRED, " ".join(text.split()))

    def test_the_grants_name_their_lists_and_placement_scopes_the_handbook(self) -> None:
        grants = " ".join((ROOT / "rules" / "grants.md").read_text().split())
        for form in GRANTS_LISTS:
            with self.subTest(form):
                self.assertIn(form, grants)
        placement = " ".join((ROOT / PLACEMENT).read_text().split())
        for form in PLACEMENT_SCOPE:
            with self.subTest(form):
                self.assertIn(form, placement)
        self.assertNotIn("this file's rules", placement)

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

    def test_the_pass_hands_on_to_the_plan_with_no_arguments_and_no_brief(self) -> None:
        self.assertIn(HAND_ON_NO_BRIEF, self.text)
        for source, page in the_map().items():
            for form in HAND_ON_RETIRED:
                with self.subTest(source=source, retired=form):
                    self.assertNotIn(form, " ".join(page.split()))

    def test_a_turn_that_left_the_pass_nothing_opens_on_the_plan_alone(self) -> None:
        self.assertIn(NOTHING_FOR_THE_PASS, self.text)
        claude = " ".join(CLAUDE.read_text().split())
        _, _, rest = claude.partition("names the kind, and that names the skill:")
        kinds, _, _ = rest.partition("- A later turn")
        self.assertIn(PASS_MAPPED, kinds)
        self.assertNotIn(PASS_MAPPED_RETIRED, claude)

    def test_the_pass_reads_the_writer_answered_brief_as_the_server_writes_it(self) -> None:
        for form in (WRITER_ANSWERED_KIND, *WRITER_ANSWERED_LINES):
            with self.subTest(form):
                self.assertIn(form, self.text)

    def test_the_pass_names_the_table_s_routes_and_leaves_a_block_in_one_step(self) -> None:
        for form in (*PASS_ROUTES, *PASS_LEFT):
            with self.subTest(form):
                self.assertIn(form, self.text)
        for form in PASS_RETIRED:
            with self.subTest(form):
                self.assertNotIn(form, self.text)
        routing = " ".join((ROOT / "rules" / "routing.md").read_text().split())
        for form in ROUTES_NAMED:
            with self.subTest(form):
                self.assertIn(form, routing)

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

    def test_the_operator_reads_the_debrief_in_its_notice_and_behind_the_debrief(self) -> None:
        for form in DEBRIEF_READ:
            with self.subTest(form):
                self.assertIn(form, self.text)
        for form in DEBRIEF_READ_RETIRED:
            with self.subTest(retired=form):
                self.assertNotIn(form, self.text)


class DebriefNoticeTest(unittest.TestCase):
    def test_the_map_names_the_debrief_s_notice_in_add_item_s_line_as_the_server_s(self) -> None:
        _, _, rest = CLAUDE.read_text().partition("\n- `add_item`: ")
        bullet, _, _ = rest.partition("\n- ")
        self.assertIn(DEBRIEF_NOTICE_NAMED, " ".join(bullet.split()))
        reference = json.loads(
            (ROOT / "tests" / "fixtures" / "tree" / "reference.json").read_text()
        )
        forms = {kind["code"]: kind["form"] for kind in reference["item_kinds"]}
        self.assertIn(DEBRIEF_NOTICE_KIND, forms)
        self.assertNotIn(forms[DEBRIEF_NOTICE_KIND], ADD_ITEM_FORMS)

    def test_a_debrief_s_notice_is_read_only_on_a_member_s_word(self) -> None:
        for source, (head, form) in DEBRIEF_NOTICE_READ_BY.items():
            _, found, rest = (ROOT / source).read_text().partition(f"\n{head}")
            bullet, _, _ = rest.partition("\n- ")
            with self.subTest(source):
                self.assertTrue(found)
                self.assertIn(form, " ".join(bullet.split()))


PROJECTS_NEVER_COORDINATE_ORDER = (
    "No ask, rule, hold, wait or plan note orders, holds or synchronises work across projects: each"
    " project runs alone, its order its own, and the card a ruling hands to another project"
    " (`rules/routing.md`'s Another project's decision) is made and left to run (the operator,"
    " 2026-11-15:"
)
PROJECTS_NEVER_COORDINATE_DRAFT = (
    "the plan, the rules and the asks order, hold or wait on no other project's work, each project"
    " running alone (`rules/stages.md`'s The order; the operator, 2026-11-15:"
)
PROJECTS_NEVER_COORDINATE_QUOTE = (
    '"The projects run completely independently and I also don\'t want any attempt to synchronize'
    ' work across them."'
)

PLUGIN_UPDATE = (
    "The plugin's update is always a work item, never run in your own turn (the operator's D1,"
    ' 2026-11-17: "A work item, always"): its session runs `claude plugin marketplace update'
    " aiworkflow`, then `claude plugin update dev@aiworkflow --yes`. The home is shared, so one"
    " update reaches every environment of every project; a session already running keeps the"
    " version it started with, and one started after has the new one."
)


class StagesRuleTest(unittest.TestCase):
    def setUp(self) -> None:
        self.text = " ".join((ROOT / "rules" / "stages.md").read_text().split())

    def test_a_card_on_the_debrief_is_the_one_exception_to_a_stage_s_documents(self) -> None:
        for form in (STAGE_DOCUMENTS_NO_CARD, *STAGE_DEBRIEF_CARD):
            with self.subTest(form):
                self.assertIn(form, self.text)

    def test_a_requirement_is_pilot_s_only_where_it_can_rule_it_safely(self) -> None:
        self.assertIn(REQUIREMENT_SAFELY_CITED, self.text)
        self.assertNotIn(REQUIREMENT_SAFELY_RETIRED, self.text)
        routing = (ROOT / "rules" / "routing.md").read_text()
        (row,) = [
            line
            for line in routing.splitlines()
            if line.startswith("| a choice outside the grants table,")
        ]
        self.assertIn(REQUIREMENT_SAFELY, row)

    def test_a_database_md_correction_is_pilot_s_to_accept_the_one_exception_to_fix_now(
        self,
    ) -> None:
        self.assertIn(DATABASE_CORRECTION_STAGES, self.text)
        routing = " ".join((ROOT / "rules" / "routing.md").read_text().split())
        for form in DATABASE_CORRECTION_ROUTED:
            with self.subTest(form):
                self.assertIn(form, routing)

    def test_the_plugin_s_update_is_always_a_work_item_run_by_its_session(self) -> None:
        head, _, _ = self.text.partition(" ## A slice or a work item ")
        self.assertIn(PLUGIN_UPDATE, head)

    def test_projects_never_coordinate_in_the_order_and_in_the_draft(self) -> None:
        _, _, rest = self.text.partition("## The order ")
        order, _, _ = rest.partition(" ## Taking a slice ")
        self.assertIn(PROJECTS_NEVER_COORDINATE_ORDER, order)
        self.assertIn(PROJECTS_NEVER_COORDINATE_QUOTE, order)
        draft = " ".join(skill_file("create").read_text().split())
        _, _, rest = draft.partition(" ## The draft ")
        section, _, _ = rest.partition(" ## A slice of the workflow ")
        self.assertIn(PROJECTS_NEVER_COORDINATE_DRAFT, section)
        self.assertIn(PROJECTS_NEVER_COORDINATE_QUOTE, section)

    def test_a_hand_over_in_a_stage_s_document_is_the_card_fate_the_stage_makes(self) -> None:
        self.assertIn(HAND_OVER_CARD_FATE, self.text)
        _, _, rest = (ROOT / "rules" / "routing.md").read_text().partition(
            "\n## Another project's decision\n"
        )
        section, _, _ = rest.partition("\n## ")
        self.assertIn(HAND_OVER_IN_A_STAGE, " ".join(section.split()))

    def test_the_stage_s_brief_says_nothing_of_its_debrief_or_of_notices(self) -> None:
        self.assertIn(STAGE_BRIEF_SILENT, self.text)

    def test_taking_a_slice_is_the_stages_rule_which_both_chats_cite(self) -> None:
        lines = (ROOT / "rules" / "stages.md").read_text().splitlines()
        self.assertEqual(lines.count(TAKING_A_SLICE), 1)
        for form in TAKING_A_SLICE_RULES:
            with self.subTest(form):
                self.assertIn(form, self.text)
        for name in ("create", "chat"):
            text = " ".join(skill_file(name).read_text().split())
            with self.subTest(name):
                self.assertIn(TAKING_A_SLICE_CITED, text)
                self.assertNotIn("Requirements, not solutions", text)
        chat = " ".join(skill_file("chat").read_text().split())
        self.assertIn(TAKING_A_SLICE_IN_THE_CHAT, chat)
        self.assertIn(CHAT_WAIT, chat)

    def test_a_slice_is_for_work_that_needs_the_whole_workflow_and_the_skills_weigh_it(
        self,
    ) -> None:
        lines = (ROOT / "rules" / "stages.md").read_text().splitlines()
        self.assertEqual(lines.count(SLICE_OR_WORK_ITEM), 1)
        self.assertLess(lines.index(SLICE_OR_WORK_ITEM), lines.index("## The order"))
        for form in SLICE_OR_WORK_ITEM_RULE:
            with self.subTest(form):
                self.assertIn(form, self.text)
        for name, forms in SLICE_OR_WORK_ITEM_WEIGHED.items():
            text = " ".join(skill_file(name).read_text().split())
            for form in forms:
                with self.subTest(skill=name, form=form):
                    self.assertIn(form, text)
        chat = " ".join(skill_file("chat").read_text().split())
        self.assertNotIn("**A new slice the person asks for**", chat)

    def test_a_person_s_fable_in_a_draft_reaches_the_task_s_note(self) -> None:
        for name, form in FABLE_IN_A_DRAFT.items():
            with self.subTest(name):
                self.assertIn(form, " ".join(skill_file(name).read_text().split()))
        self.assertIn(FABLE_PLACED, " ".join((ROOT / PLACEMENT).read_text().split()))


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


class PilotsNotesTest(unittest.TestCase):
    def test_the_pre_rule_and_plan_skills_say_the_exception_rule_in_the_same_words(self) -> None:
        said = {}
        for name in NOTE_SKILLS:
            text = " ".join(skill_file(name).read_text().split())
            _, lead, rest = text.partition(NOTE_EXCEPTION_LEAD)
            rule, end, _ = rest.partition(NOTE_EXCEPTION_END)
            with self.subTest(skill=name):
                self.assertTrue(lead and end)
            said[name] = rule
            for form in NOTE_EXCEPTION:
                with self.subTest(skill=name, form=form):
                    self.assertIn(form, f"{rule}{end}")
        self.assertEqual(said["pre-rule"], said["plan"])

    def test_the_pass_puts_what_only_pilot_knows_of_a_block_left_to_a_person_in_its_note(
        self,
    ) -> None:
        text = " ".join(skill_file("pre-rule").read_text().split())
        for form in PASS_NOTES:
            with self.subTest(form):
                self.assertIn(form, text)
        for form in PASS_NOTICE_RETIRED:
            with self.subTest(retired=form):
                self.assertNotIn(form, text)

    def test_the_plan_skill_starts_the_offered_work_and_writes_nothing_on_the_block(self) -> None:
        plan = skill_file("plan").read_text()
        _, _, rest = plan.partition("\n## An offer taken\n")
        mode, _, _ = rest.partition("\n## ")
        text = " ".join(mode.split())
        for form in (*OFFER_TAKEN_LINES, *OFFER_TAKEN_WORK):
            with self.subTest(form):
                self.assertIn(form, text)
        self.assertIn(OFFER_TAKEN_KIND, " ".join(plan.split()))

    def test_claude_md_maps_the_offer_s_kind_line_to_the_plan_skill(self) -> None:
        text = " ".join(CLAUDE.read_text().split())
        _, _, rest = text.partition("names the kind, and that names the skill:")
        kinds, _, _ = rest.partition("- A later turn")
        self.assertIn(OFFER_TAKEN_MAPPED, kinds)

    def test_claude_md_names_note_and_alert_and_the_notes_in_timeline_json(self) -> None:
        text = " ".join(CLAUDE.read_text().split())
        for form in NOTES_IN_THE_MAP:
            with self.subTest(form):
                self.assertIn(form, text)

    def test_the_chat_reads_a_quoted_block_with_pilot_s_note_on_it(self) -> None:
        self.assertIn(NOTES_READ, " ".join(skill_file("chat").read_text().split()))


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

    def test_with_auto_pilot_off_a_held_push_is_confirmed_then_claimed(self) -> None:
        routing = " ".join((ROOT / "rules" / "routing.md").read_text().split())
        for form in HELD_PUSH_ROUTED:
            with self.subTest(form):
                self.assertIn(form, routing)
        stages = " ".join((ROOT / "rules" / "stages.md").read_text().split())
        for form in HELD_PUSH_STAGES:
            with self.subTest(form):
                self.assertIn(form, stages)
        self.assertNotIn(HELD_PUSH_RETIRED, stages)
        pre_rule = " ".join(skill_file("pre-rule").read_text().split())
        for form in HELD_PUSH_PASS:
            with self.subTest(form):
                self.assertIn(form, pre_rule)
        _, _, rest = skill_file("plan").read_text().partition("\n## An item done\n")
        item_done, _, _ = rest.partition("\n## ")
        self.assertIn(HELD_PUSH_CLAIMED, " ".join(item_done.split()))

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


class ResumeWaitsOnWorkTest(unittest.TestCase):
    def test_a_resume_that_waits_on_work_holds_its_blocks_through_that_work(self) -> None:
        routing = (ROOT / "rules" / "routing.md").read_text()
        self.assertEqual(routing.splitlines().count(RESUME_SECTION), 1)
        _, _, rest = routing.partition(f"\n{RESUME_SECTION}\n")
        section, _, _ = rest.partition("\n## ")
        for form in RESUME_RULE:
            with self.subTest(form):
                self.assertIn(form, " ".join(section.split()))
        pre_rule = " ".join(skill_file("pre-rule").read_text().split())
        for form in RESUME_PASS:
            with self.subTest(form):
                self.assertIn(form, pre_rule)


class WaitTest(unittest.TestCase):
    def test_no_file_of_the_map_refuses_a_wait(self) -> None:
        for source, text in the_map().items():
            for words in WAIT_REFUSALS:
                with self.subTest(source=source, words=words):
                    self.assertNotIn(words, text)

    def test_the_skills_that_add_a_wait_name_its_kinds_and_arm_it_as_routing_does(self) -> None:
        for name in WAIT_ADDING_SKILLS:
            text = " ".join(skill_file(name).read_text().split())
            for form in (*WAIT_KINDS, *WAIT_ARMED):
                with self.subTest(skill=name, form=form):
                    self.assertIn(form, text)
        routing = (ROOT / "rules" / "routing.md").read_text()
        self.assertEqual(routing.splitlines().count(WAIT_SECTION), 1)
        _, _, rest = routing.partition(f"\n{WAIT_SECTION}\n")
        section, _, _ = rest.partition("\n## ")
        for form in ROUTING_WAIT:
            with self.subTest(form):
                self.assertIn(form, " ".join(section.split()))
        for source, text in the_map().items():
            for form in WAIT_RETIRED:
                with self.subTest(source=source, form=form):
                    self.assertNotIn(form, " ".join(text.split()))
        _, _, rest = skill_file("plan").read_text().partition("\n## An action of Pilot's done\n")
        mode, _, _ = rest.partition("\n## ")
        self.assertIn(WAIT_DEFERRED_DONE, " ".join(mode.split()))

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


class ReadingElsewhereSyntaxTest(unittest.TestCase):
    def test_claude_md_s_reading_elsewhere_carries_the_trackers_and_gitblits_syntax(self) -> None:
        text = " ".join(CLAUDE.read_text().split())
        _, _, rest = text.partition("## Reading elsewhere ")
        section, _, _ = rest.partition(" ## ")
        for form in (
            "YouTrack refuses a query with parentheses",
            "`tag: X` is meant",
            "New, Accepted, Later, In Progress, Resolved and Done",
            "`State: {In Progress}`",
            "`#Unresolved` for open",
            "Gitblit names a repo `pvginkel/<Name>.git`",
            "daily mirror that may not hold a repo created recently",
            "through the fleet's `read_file` in an environment holding its checkout",
        ):
            with self.subTest(form):
                self.assertIn(form, section)


class SharedHomesTest(unittest.TestCase):
    def test_claude_md_holds_what_every_session_shares_and_the_skills_point_at_it(self) -> None:
        claude = " ".join(CLAUDE.read_text().split())
        shared = (FOLLOW_UP, EFFECT_LINES, *READ_ELSEWHERE, *PROSE_ITEM_AND_COPY, *DRAFT_EXCEPTIONS)
        for form in shared:
            with self.subTest(form):
                self.assertIn(form, claude)
        for name, own in FOLLOW_UP_OWN.items():
            text = skill_file(name).read_text()
            _, _, rest = text.partition("\n## The server's follow-up turn\n")
            section, _, _ = rest.partition("\n## ")
            section = " ".join(section.split())
            with self.subTest(name):
                self.assertIn(FOLLOW_UP_CITED, section)
                self.assertIn(own, section)
                self.assertNotIn("Fix it and end your turn", section)
        for name in ("chat", "create"):
            text = " ".join(skill_file(name).read_text().split())
            with self.subTest(name):
                self.assertIn(EFFECT_LINES_CITED, text)
                self.assertIn(READ_ELSEWHERE_CITED, text)
                self.assertNotIn("never recalled or guessed", text)
                self.assertNotIn("every file of one call one batch", text)


class CitationsTest(unittest.TestCase):
    def test_claude_md_and_every_skill_cite_the_format_skill_by_its_name(self) -> None:
        for path in [CLAUDE, *(skill_file(name) for name in SKILL_NAMES)]:
            with self.subTest(path.relative_to(ROOT)):
                text = path.read_text()
                self.assertIn(f"`{FORMAT_SKILL}`", text)
                self.assertEqual(set(re.findall(r"/[\w:-]*format\b", text)), {FORMAT_SKILL})

    def test_the_format_skill_is_loaded_where_its_format_is_written_and_nowhere_else(self) -> None:
        _, _, rest = " ".join(CLAUDE.read_text().split()).partition("## Writing ")
        writing, _, _ = rest.partition(" ## ")
        for phrase in (
            "The lead first.",
            "Load it before you write an item's file, whole through `add_item`'s `markdown` or"
            " at the path `add_item` returns, a block's answer line by hand, or the draft.",
            "Not for `handbook.md`, `plan.json`'s notes or a `pilot.py` write:"
            " `pilot.py` writes its answer lines and notes in their format itself.",
        ):
            with self.subTest(phrase):
                self.assertIn(phrase, writing)
        for name, phrase in {
            "pre-rule": "loaded before you write one; a `pilot.py` write is not.",
            "chat": "loaded before you write an item's file or an answer line by hand; never for"
            " `handbook.md` or a `pilot.py` write (CLAUDE.md's Writing).",
            "plan": "loaded before you write one; `plan.json`'s notes, `handbook.md` and a"
            " `pilot.py` write are not (CLAUDE.md's Writing).",
            "create": "loaded before you write the draft.",
        }.items():
            with self.subTest(name):
                text = " ".join(skill_file(name).read_text().split())
                self.assertIn(f"`{FORMAT_SKILL}`'s, {phrase}", text)

    def test_every_path_the_map_cites_is_there(self) -> None:
        names = repo_names()
        for source, text in the_map().items():
            for path in cited_paths(text):
                with self.subTest(source=source, path=path):
                    self.assertTrue(is_there(path, names))

    def test_claude_md_gives_every_verb_of_pilot_py_its_one_line(self) -> None:
        text = " ".join(CLAUDE.read_text().split())
        verbs = pilot_verbs()
        usages = pilot_usages()
        for verb, description in verbs.items():
            with self.subTest(verb):
                self.assertIn(f"`{usages.get(verb, verb)}`: {description}", text)
        named = {
            max((verb for verb in verbs if f"{span} ".startswith(f"{verb} ")), key=len)
            for span in re.findall(r"- `(pilot\.py [^`]+)`:", text)
        }
        self.assertEqual(named, set(verbs))

    def test_claude_md_gives_every_write_verb_its_usage_line_as_pilot_py_prints_it(self) -> None:
        text = " ".join(CLAUDE.read_text().split())
        usages = pilot_usages()
        self.assertEqual(set(usages), WRITE_VERBS)
        for verb, usage in usages.items():
            with self.subTest(verb):
                self.assertIn(f"- `{usage}`: ", text)
        for verb in set(pilot_verbs()) - WRITE_VERBS:
            with self.subTest(verb):
                self.assertIn(f"- `{verb}`: ", text)

    def test_claude_md_names_every_tool_call_the_hook_locks_around(self) -> None:
        settings = json.loads((ROOT / ".claude" / "settings.json").read_text())
        (entry,) = settings["hooks"]["PreToolUse"]
        text = CLAUDE.read_text()
        for tool in entry["matcher"].split("|"):
            with self.subTest(tool):
                self.assertIn(f"`{tool}`", text)

    def test_a_task_or_a_note_is_quoted_by_the_metavar_pilot_py_gives_it(self) -> None:
        for source, text in the_map().items():
            for command in quoted_commands(text):
                if not command.startswith("pilot.py plan "):
                    continue
                with self.subTest(source=source, command=command):
                    self.assertNotIn("<id>", command)
                    self.assertNotIn("--ref <block id>", command)

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

    def test_the_chat_s_learning_is_outside_the_kept_column(self) -> None:
        grants = (ROOT / "rules" / "grants.md").read_text()
        _, _, kept = grants.partition("**Kept**")
        kept, _, _ = kept.partition("\n## ")
        self.assertIn(LEARNING_OUTSIDE_KEPT, " ".join(kept.split()))
        self.assertIn(LEARNING_AT_ONCE, " ".join(skill_file("chat").read_text().split()))

    def test_a_change_to_the_rules_is_a_decision_and_never_a_confirmation(self) -> None:
        _, _, rest = (ROOT / "rules" / "grants.md").read_text().partition(
            "\n## The confirmation reasons\n"
        )
        section, _, _ = rest.partition("\n## ")
        for form in RULE_CHANGE_A_DECISION:
            with self.subTest(form):
                self.assertIn(form, " ".join(section.split()))

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

    def test_a_usage_line_as_pilot_py_prints_it_is_taken(self) -> None:
        options = pilot_options()
        for usage in pilot_usages().values():
            with self.subTest(usage):
                self.assertIsNone(command_fault(usage, options))

    def test_an_option_a_usage_line_gives_its_verb_and_has_not_is_refused(self) -> None:
        options = pilot_options()
        self.assertEqual(
            command_fault("pilot.py plan set [--ticket <ticket>|--no-label] [--repo <r>]", options),
            "`pilot.py plan set` takes no --no-label",
        )
        self.assertEqual(
            command_fault("pilot.py plan task move <task id> [--to <task id>]", options),
            "`pilot.py plan task move` takes no --to",
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
