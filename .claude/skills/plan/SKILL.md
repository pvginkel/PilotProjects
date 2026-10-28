---
name: plan
description: Pilot's upkeep of a project's plan and its work — the setup from the draft, what is next after a worker's turn or an item of Pilot's own done, placement, the confirmations, the sweep and the finish decision. Run it when Pilot's brief opens with /plan, or when /pre-rule hands on to it.
---

# Plan

The plan's upkeep and the work: the setup from the draft, what is next after a worker's turn and
after an item of yours is done, the sweep before the finish and the finish decision, in the mode
the brief names.

1. Read `handbook.md` before anything the brief asks; at the setup it is empty, unless the setup
   is a Retry (In every mode).
2. Read the brief, below: its kind line, `Pilot's brief · <the kind> · …`, names the mode —
   `Pilot's brief · the setup · …`, The setup; `Pilot's brief · a worker's turn ended · …`, What
   is next, entered from `/pre-rule` once its pass is done, in the same session, its arguments the
   brief as the job received it; `Pilot's brief · an item of yours is done · …`, An item done, then
   What is next —; its switch line, the grants that hold for this session; a pause; the trigger's
   lines; the plan's open notes, by summary; and the deferrals without a home.
3. Do the mode's work, then end your turn with one line saying what it did. A job never waits
   and never asks in its own transcript: a question to a person is an item.

The rules it applies: `rules/grants.md`, `rules/work-items.md`, `rules/placement.md`,
`rules/stages.md`, `rules/routing.md`. The writing — an item, a note — is `/dev:document-format`'s.

## In every mode

- **What is there first.** The brief says what triggered the job; the store says what is there:
  `plan.json` (`pilot.py plan task list`, `pilot.py plan note list`) and `timeline.json`
  (`pilot.py items list --open`) are read before you write. A job may be a person's Retry of one
  that failed or stopped: the same kind line and brief, composed as it starts — a setup's word for
  word, `The plan: plan.json, empty.` included — while the store holds whatever the failed job
  wrote first: a handbook, the plan's tasks, a work item it started, a note, an item. Take up what
  is there, and never add a second of it.
- **As lean as the project**: the plan holds the tasks the project needs and no more — a task
  added where the work shows one missing, removed where it turns moot,
  `pilot.py plan task remove <id>` once its notes are struck or moved; no task is a fixture.
- **Work** is a work item, its fields and its brief as `rules/work-items.md` has them: free-form,
  from a brief of yours, since no stage runs from Pilot (`rules/stages.md`), each placed by
  `rules/placement.md` and what the handbook says of the project's repositories.
- **The bounded check** before an ask you are about to put — a decision, a confirmation, the
  finish decision — where a survey, an isolated test or a read could change its recommendation:
  a sub-agent or a fleet read first, with the premise, the check, how each result moves the
  recommendation and the stop; "would you like me to investigate?" is never asked where the
  grants already allow it.

## The setup

The first job of a project, at Create project: the brief says the project was created from
`draft-<number>`, its folder now `/work/Projects/<slug>`; names the opening item, which holds the
words that started it and on which the draft's copy and what the definition chat attached hang;
and says `plan.json` is empty. It writes the handbook's first version and the plan from the
draft, and starts the work that can start.

1. Read `project.md` as it stands at Create — its lead, `## The plan`, `## Rules`, `## Context`
   and its asks, an ask still open included — the opening's words, its file at the path
   `timeline.json` gives it, and what hangs on the opening. The draft is what the chat agreed,
   and nothing in the app fixes it; it is read, not rewritten, and the opening stays the request.
2. **The handbook's first version**, `handbook.md`: the result the project is for, stated from
   the draft — what will be demonstrated and the evidence that will show it; then the prose of the
   draft's `## Rules` and `## Context`, copied, and never an ask's block: an ask fenced there stays
   in `project.md`, the handbook stating a ruled ask's outcome as a plain rule line, and an ask
   still open is step 5's. The report in the tool's result after the write is read for its lines
   naming `handbook.md` — a line dropped or reverted, a fault that holds the save — and the
   handbook written again until it names none; that the write landed is not enough.
3. **The plan**, `plan.json`, through `pilot.py`'s plan verbs: the tasks as the chat agreed
   them, in its order, with ids you give, `t1`, `t2`, … —
   `pilot.py plan task add --id <id> --title <text>` — a task's title naming what it waits on
   where the draft agreed an order; and the ticket and the repository where the draft names
   them, `pilot.py plan set --ticket <id> --repo <owner/Name>`.
4. **As lean as the project**: nothing is required of a plan but what the project needs —
   "the build is failing" is a task or two — and no task is a fixture. A sweep task before the
   end only where the project will have something to sweep, an epic with `Later` cards or
   deferrals to the plan's end; never otherwise.
5. **An ask the draft left open** stays open there, and nothing answers it past Create: where a
   task needs its answer, ask it anew as an item (`add_item`, a decision or a question, its `step`
   the task); where none does, the plan goes on without it.
6. **Every task that can start, started**: each whose inputs are there and that waits on no
   other task gets its first work item, and the task is set going,
   `pilot.py plan task set <id> --status in_progress`. A task with no repository to work in
   places no work item: an act of a person's hands is an action item for them, exact; a task
   that waits stays pending.

## What is next

After the pass, entered from `/pre-rule` on a worker's turn ended, and after An item done: the
plan brought up to date with what happened, and every piece of work that can go, going.

1. **The task's status**, from what the run or the close did — the task the brief's work item or
   item names: `pilot.py plan task set <id> --status done` where its work is done, nothing of it
   left and no document its runs registered open; `in_progress` while it has a run going or one
   waiting on a person.
2. **Its notes**, and those of each task you start below, the content and blocks a read away,
   `pilot.py plan note list --task <id>`; the plan's own at the plan's end (The sweep). Each is met
   and acted on — what it says to ask asked, in the work item's brief or as an item, what it says
   to do done — then struck, `pilot.py plan note strike <id>`; or re-deferred with a reason, a note
   on the task or the plan where it now returns, naming the same blocks and why, the old one
   struck; or struck where its block is no longer deferred, a person having ruled it after all.
3. **The deferrals without a home**, the brief's last list, which the pass leaves to you: each
   given its note in this turn, as `rules/routing.md`'s Deferral has it —
   `pilot.py plan note add --task <id> --summary <line> --ref <block id> <content>`, without
   `--task` for one deferred to the plan — or its block answered anew in a new item, as their line
   says.
4. **Every task whose inputs are done, started**, a work item each, in an environment of its own,
   all at once: the gate throttles them, and a held start is a line, never a reason to start less.
   Held back only what the plan says waits — a task's title names what it is after — and what
   would collide: two runs on one repository's same files, or work whose input is a run's open
   document; a task held back for a collision says so in a note on it. One at a time is the
   exception the plan writes, never the default. A task with an open work item is going already:
   it gets no second.
5. **A run's open documents.** A run waits on the documents it registered, and Pilot's server
   resumes it once the last of them is closed — never you, and never a second work item for its
   task. Nothing that waits on those documents is started; the task a finished document
   unblocks is started at once, whatever other runs still wait on theirs, since each waits only on
   its own. A one-block document the pass answered or deferred is open still, for a person to
   confirm: what waits on it waits.
6. **The next human prerequisite**, one boundary ahead — what a person's hands must do before the
   next task can go: an action item, exact, its `step` the task it unblocks; an open one of yours
   already there is updated in its file, never added a second time.
7. **A confirmation**, where the grants hold the next act — the granted column with the brief's
   switch line off, or the kept column (`rules/grants.md`): a decision whose one block is a
   confirmation with its `because`, by its code in `rules/grants.md`'s "The confirmation reasons",
   asked when the act is due, one covering everything due at once. The act waits for its Yes,
   which the job after its close does (An item done).
8. **The plan's end**: once its last task is done, The sweep, then The finish decision.

## An item done

The brief's item line names the item of yours a person closed and how —
`The item: <path> (<item id>), <kind> "<title>"[, task <id>] — <close>.`, a document's Done with a
line per block after it; the file holds the prose. Act on the close, then What is next:

- **A confirmation's Yes**: its act, every act it covered — a work item, or your own hands where
  it is a tool call: a card, a fleet call.
- **A No**: its reason read and the plan adjusted; the person told through an item only where
  something else now waits on them.
- **A decision's or a question's answer**: the plan's next step on it — a task started, changed,
  added or removed as it rules; an answer `deferred`, its note as the deferrals without a home
  have theirs (What is next, step 3).
- **An action's Done**: the paste-back read, and the check it names run where you can.
- **A document of yours Done**: each of its answers acted on, as above.
- **A review's Reviewed**: nothing of it waits on you.
- **The sweep's decision or the finish decision**: as their sections have it.

## The sweep

Before the finish decision, in every plan, and at the plan's sweep task where it has one: the
plan's open notes of its own — those `pilot.py plan note list` lists as the plan's — and, where
the plan has a ticket, the `Later` cards linked to that epic (`rules/routing.md`'s The `Later`
card), read through youtrack. Each one is:

- done now, the note struck and the card closed;
- closed with a reason, the note struck and the card closed with the reason as its comment;
- or put into a sweep task you scope yourself: with auto pilot on, added and its work item
  started; off, one decision first, "Add a sweep task covering these four — Agree / Other", the
  task added and started on its Agree.

No finish decision is asked while a note or a linked card is unaccounted for.

## The finish decision

Once the plan's last task is done and the sweep has left nothing unaccounted for: one decision
item against the result the project is for, as the handbook states it — what was demonstrated,
what is inferred, what the operator accepted as a limitation — asking whether to finish. One
only: an open one already there is the one, and so is the one whose close this job acts on —
What is next after it asks none. On its Yes, the job after its close calls `finish`,
last: it closes every open item and stops every session of the project, this one's turn among
them. On a No, its reason read and the plan adjusted. The archive question after a finish is the
server's.

## Not yet the plan's

- **A wait's firings**, and a wait: `add_item` refuses `card_wait` and `timed_wait` ("Pilot takes
  no waits yet"). What would wait on an event goes in a note on its task, and no watch is
  promised.
- **A claimed action**, `Pilot does it`: nothing yet takes a claim up when its work ends, so none
  is claimed; an act of a tool call is done at once by your own hands.

## The server's follow-up turn

A turn of Pilot's server that names a save of yours still held — "Your save of `<path>` is held:
`<path>:<line>: <message>`. Fix it and end your turn." — is no person's: fix the file until the
report after your write names no line of it, and end the turn. The job is done when that turn
ends.

## The brief

$ARGUMENTS
