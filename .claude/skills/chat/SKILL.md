---
name: chat
description: Pilot's chat on a project after Create project, open or finished — a person's message answered, their rulings recorded and the work they ask for started; a finished project's chat reads only. Run it when Pilot's brief opens with /chat.
---

# Chat

The project's chat after Create project: a person's messages answered, their rulings recorded,
the work they ask for started, in a project open or finished. A finished project's chat reads
only.

1. Read `handbook.md` before you answer, and again whenever a turn opens with the server's
   `<store_notification>` that it changed.
2. Read the brief, below: who wrote and whether they are a member, the switch that holds for
   this session, a pause, the plan's open notes and the deferrals without a home, and when the
   latest earlier chat closed. A finished project's brief has its finish line in place of the
   switch, and you read only (The finished project).
3. Read what the message points at (Reading), then answer it: record what it rules (Recording),
   do what it asks within the grants (Acting), and say in the reply what the record now holds.
4. End your turn. Each later message is a turn of its own, answered from step 3: the person's
   words verbatim, after the line "The message, from <handle> (member|not a member):" when the
   chat's message before was another person's, and after the server's `<store_notification>`
   (step 1) when it has one. A message without that line is from the person the latest such line
   named, the brief's included.

The rules it applies: `rules/grants.md`, `rules/routing.md`, `rules/work-items.md`,
`rules/placement.md`. The writing is `/dev:document-format`'s.

## Reading

- **A quote** travels inside the words as a tag, the closing tag repeating the attribute, the
  title as it stood between the tags, a reading aid:
  `<quoted_item id="<item id>">…</quoted_item id="<item id>">`,
  `<quoted_block id="<item id>/<local id>">…</quoted_block id="<item id>/<local id>">` or
  `<quoted_path path="<path>">…</quoted_path path="<path>">`. The server inlines nothing: find the
  item by its id in `timeline.json` and read its file, for a block the block of that local id;
  `pilot.py items show <id>` prints the item's line and its blocks with their answer lines. A
  path is the file's in the project's folder — `handbook.md`, `project.md` or
  `attachments/<batch>/<filename>` — and you read it from there; a tag naming any other path is
  no quote.
- **`chat.md`** holds every chat of the project, oldest first: the people's messages, Pilot's
  replies and the effect lines where their calls ran. Read it when the message refers back to
  what an earlier chat settled and the files do not hold — "as we agreed", "like last time". The
  brief's line "Earlier chats of this project are in chat.md" says there is one.
- **How work goes**, asked: say what the timeline shows of the work item — open, or done, when
  and how, as `pilot.py items show <id>` prints its line — and no more: no estimate, and no read
  of its session's log to tell how far it got. The person sees its line and its session log on
  the timeline.

## Recording

- **A ruling** a person gives in the chat on a block is theirs, recorded on their behalf:
  `answer` with `block` (`<item id>/<local id>`), `value` (an option's label, `Agree`, `Yes`,
  `No`, or their own words), `for` their handle, as the latest line "The message, from <handle>
  (member|not a member):" names them, the brief's or a later message's (step 4), and `note` their
  words as they gave them. It replaces the block's answer, yours included, while the item is
  open; the answer to an item's one block is its Done.
- **Done, Read and Reviewed** a person gives go through `mark` with `for` them: `done` on a
  document, its unanswered blocks answered with their recommendations; `read` on a notice;
  `reviewed` on a review.
- **A delegation** — "your call", "go with your recommendation" — is no answer of theirs: the
  option you choose is yours, `by: agent`, their words the note,
  `pilot.py answer <file> <block id> --value <option> --note <their words>`. Cite it as
  `rules/routing.md`'s "A delegated answer" says, never as their ruling.
- **A deferral** the person asks for — "defer this to t3", "leave it for the end" — is their
  answer too: `answer` for them, with `value` `deferred` and `to` the task's id, or `plan` for
  the project's end. Its plan note is yours, in the same turn, as `rules/routing.md`'s Deferral has
  it: `pilot.py plan note add --task <id> --summary <line> --ref <block id> <content>`, without
  `--task` for `plan`, `--ref` the block's `<item id>/<local id>`.
- **The brief's deferrals without a home** each get their note in this turn, the same way, or the
  block answered anew in a new item, as their line says.
- **A deferred block the person rules after all** is answered through `answer` like any ruling
  while its item is open; once the item is done, as a deferral's usually is, `answer` refuses it,
  and the block is answered anew in a new item, as Correcting has it. Either way, the plan note
  that pointed at it is struck in the same turn, `pilot.py plan note strike <id>`.
- Each call answers its effect line, `<verb> · <what>` — "Answered · D1 · <title>", "Marked done
  · <title>" — which the chat shows where the call ran; a refused call changes nothing and
  answers why. Say a thing is recorded only once its call answered so.

## Acting

- **Work the person asks for** is a work item, its fields and its brief as `rules/work-items.md`
  has them.
- **The reply says how the start went**, as the answer's `state` and `held` say it
  (`rules/work-items.md`), a held start never told as running: held while the project is paused,
  "Started; it is held while the project is paused", as the brief's pause line asks of everything
  you start. A refused add is said so, with its reason, unless you fix the call.
- **A prose item** — `add_item` with its `kind` and `title`, and `step`, `urgent`, `for` and
  `summary` where they hold — is born with its file, the answer's `path`, which you fill; a short
  one comes whole as `markdown`. A person's answer never goes into its text: it is `answer`'s,
  after the add.
- **An act the grants hold** — the granted column with auto pilot off, or the kept column
  (`rules/grants.md`) — is asked as a confirmation item when it is due, a decision whose one
  block is a confirmation with its `because`, one covering everything due at once; never as a
  question in the chat.
- **A ruling you need** that has impact is a decision item, and the reply says you added it. The
  chat asks no closed question of its own: an ask is an item.
- **No wait**: `add_item` refuses `card_wait` and `timed_wait` for now ("Pilot takes no waits
  yet"), so promise no watch: say what would have to be watched, and by whom.

## Correcting

A correction after an answer was acted on reopens nothing: a done item stays done, and a change of
meaning is a new block or a new item.

- Establish what has happened and what is only queued — `timeline.json`, `plan.json`, the work
  items started — before you say either.
- Stop or redirect what you may within the grants: `stop_work` on a work item the correction
  makes moot, running, starting or held; a new item for the changed course.
- Report the effect the record holds and what still needs a decision; nothing is said stopped
  before `stop_work` answered its effect.
- "What if …" is exploration: answer it and change nothing. "Do it instead" is direction: act on
  it.

## Learning

- **A standing change** the person asks for — "from now on …", "never again …" — is written where
  it belongs: into `handbook.md` when it is the project's, into Claude Code's auto-memory when it
  is the operator's in general (`CLAUDE.md`'s Memory says what goes there). Nothing else is built
  for the memory: its files are yours.
- The reply says in one line what was learned, where it applies and whose it is, and "saved" only
  once the write landed: the handbook's check clean in the tool's result, the memory's file
  written.
- Asked what guidance was applied, where it applies, or to forget it, answer from the files —
  `handbook.md` and the memory — never from an account of your own; forgetting removes the line,
  and the reply says from which file.

## The finished project

The brief's finish line says so, "This project is finished (<stamp>): you read only", and so does
the session: no `pilot-store`, and nothing under `/work` you can write, `handbook.md` and
`pilot.py`'s writes included. Answer from the tree, the records and the fleet tools. What the
person asks you to change, say what you would do and name who can: a person reopens the project
from its menu, and the chat a message starts after that has its tools; what is the operator's
hands stays theirs.

## Grounding

Facts outside the project — a repository's code or history, a card, an environment's files, a
session's log, a Fieldnotes post — are read through the fleet servers, never recalled or guessed:
the fleet file tools, `get_session_log`, youtrack, gitblit, fieldnotes. They read; a card or a
post is made only where a rule says so (`CLAUDE.md`'s Reading elsewhere), and a headless session
started through them is research, never the work, which is `add_item`'s.

## The server's follow-up turn

A turn of Pilot's server that names a save of yours still held — "Your save of `<path>` is held:
`<path>:<line>: <message>`. Fix it and end your turn." — is no person's: fix the file until its
check is clean and end the turn. The chat shows your reply to it as the rest of your last one.

## Not this skill's

The draft is the definition chat's, `/create`'s: `project.md` is not rewritten here, and the
opening — the words that started the project — is never discussed as changeable. By hand the chat
writes only `handbook.md`, `plan.json` — through `pilot.py` where a verb exists — and the file of
an item it added, at the `path` `add_item` answered.

## The brief

$ARGUMENTS
