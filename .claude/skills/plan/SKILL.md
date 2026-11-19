---
name: plan
description: Pilot's upkeep of a project's plan and its work — the setup from the draft, an action Pilot claimed done when its work ends, what is next after a worker's turn, an item of Pilot's own done or an offer of Pilot's taken, the work that offer starts, a wait's firings, placement, the confirmations, the sweep and the finish decision. Run it when Pilot's brief opens with /plan, or when /pre-rule hands on to it.
---

# Plan

The plan's upkeep and the work: the setup from the draft, an action you claimed done when its
work ends, what is next after a worker's turn, after an item of yours is done and after an offer of
yours is taken, the work that offer starts, a wait's firings, the sweep before the finish and the
finish decision, in the mode the brief names.

1. Read the brief, below: its kind line, `Pilot's brief · <the kind> · …`, names the mode —
   `Pilot's brief · the setup · …`, The setup; `Pilot's brief · a worker's turn ended · …` and
   `Pilot's brief · the writer answered · …`, What is next, An action of Pilot's done first where
   the brief names claimed actions or its work item is a close-out's promotion's or does an action
   deferred to a wait; `Pilot's brief · an item of yours is done · …`, An item done, then What is
   next; `Pilot's brief · an offer of yours was taken · …`, An offer taken, then What is next;
   `Pilot's brief · a wait fired · …`, A wait's firings —; its switch line, the grants that hold
   for this session; a pause; the trigger's lines; then the project's state — the job's seq and its
   trigger's item's, the plan's tasks not done, the open items, the open notes whole, your return
   list and the deferrals without a home — and the handbook, whole, which you read here and not
   from the store (In every mode's What is there first). Entered from `/pre-rule` once its pass is
   done, in the same session, this skill comes with no arguments and nothing is below: the brief is
   the one the session opened with, above, and you read it there. A worker's turn ended whose run
   left the pass nothing opens on this skill itself, its brief below, with no pass before it (What
   is next). A later turn of a wait's run, `Another firing of "<title>" since your last run:` and
   its lines, has no brief: A wait's firings again, on those firings, what it acts on read fresh
   (In every mode's A later turn).
2. Do the mode's work, then end your turn with one line saying what it did. A job never waits
   and never asks in its own transcript: a question to a person is an item.

The rules it applies: `rules/grants.md`, `rules/work-items.md`, `rules/placement.md`,
`rules/stages.md`, `rules/routing.md`, `rules/promote.md`. The writing — an item's file, an answer
line by hand — is `/dev:document-format`'s, loaded before you write one; `plan.json`'s notes,
`handbook.md` and a `pilot.py` write are not (CLAUDE.md's Writing).

## In every mode

- **What is there first.** The brief says what triggered the job and what is there: the project's
  state as the record held it when the brief was composed, each part as `pilot.py` prints its
  listing, and a part with nothing in it left out, its heading too. In its order:
  `This job is seq <n> on the timeline; the item its trigger names, seq <m>.`, the setup's its own
  seq alone; `The plan's tasks not done, in its order, …`, each `<task id> · <status> · <title>`
  with its open notes' ids, and none there where no task is left undone; `The open items, …`, each
  with the task it serves, `step <task id>`; `The open plan notes, whole, …`, each
  `<note id> · <task id> · <summary>`, or `<note id> · plan · <summary>` for the plan's own, its
  content and the blocks it names, as they stand, under it; `Your return list, …`, the open notes
  of the trigger's task and the plan's own, after an item done, an offer taken and a wait fired;
  the deferrals without a home; and last
  `The project's handbook, handbook.md, whole:`, at the setup none, its handbook empty, unless the
  setup is a Retry. Read them there before you write: on the turn the brief opens, no
  `pilot.py plan task list`, `pilot.py plan note list` or `pilot.py items list --open` is run for
  what it carries, and `handbook.md` is not read first. A job may be a person's Retry of one that
  failed or stopped: the same kind line and trigger's lines — a setup's word for word,
  `The plan: plan.json, empty.` included — while the brief's state holds whatever the failed job
  wrote first: a handbook, the plan's tasks, a work item it started, a note, an item. Take up what
  is there, and never add a second of it.
- **A later turn** carries no brief and no state: a wait's run resumed on another firing, a turn
  of Pilot's server, and a chat's later message, on which `/chat` carries out What is next. The
  record moved meanwhile, by workers, jobs and people, so what such a turn acts on is read fresh —
  `pilot.py plan task list`, `pilot.py plan note list`, a task's alone with
  `pilot.py plan note list --task <task id>`, and `pilot.py items list --open` — never taken from
  the opening brief's state.
- **As lean as the project**: the plan holds the tasks the project needs and no more — "the
  build is failing" is a task or two — a task added where the work shows one missing, removed
  where it turns moot, `pilot.py plan task remove <task id>` once its notes are struck or moved; no
  task is a fixture. A task you add yourself is a slice's three, its filing, its planning and its
  run, only where its work needs the whole workflow by `rules/stages.md`'s A slice or a work item,
  and a single task done by a free-form work item otherwise.
- **Work** is a work item, its fields and its brief as `rules/work-items.md` has them, its brief the
  work's own part alone, since Pilot's server appends the grants text the switch selects: a stage of
  the workflow for a slice's planning and its run, filed first by a work item of its own
  (`rules/stages.md`), and free-form from a brief of yours otherwise, each placed by
  `rules/placement.md` and what the handbook says of the project's repositories. A work item you
  replace with another, its task changed by a ruling or its brief outdated, is closed for good
  with it, never left stopped beside it: `stop_work` with `reason`, as `rules/work-items.md`'s A
  work item closed for good has it.
- **Starting a task**: every task whose inputs are done and that waits on nothing the plan says it
  waits on gets its work item, in an environment of its own, all at once — the gate throttles them,
  and a held start is a line, never a reason to start less — and is set going as its work item
  starts, `pilot.py plan task set <task id> --status in_progress`, never a job later. Held back only
  what the plan says waits — what a task waits on is a note on it, one of the open notes (What is
  there first; A later turn), which you strike, `pilot.py plan note strike <note id>`, once what it
  waits on is met — and what would collide: two
  runs on one repository's same files, or work whose input is a run's open document; a task held
  back for a collision says so in a note on it. Each run waits only on its own documents: the task a
  finished document unblocks is started at once, whatever other runs still wait on theirs. One at a
  time is the exception the plan writes, never the default. A task with an open work item, its run
  waiting on its documents among them, is going already: it gets no second, and Pilot's server
  resumes the run once the last is closed, never you. A task with no repository to work in places no
  work item: an act of a person's hands is an action item for them, exact; a task that waits stays
  pending. The setup, What is next, a wait's Over and the chat start a task by this passage alone
  (the operator, 2026-11-15: "One passage", to "Starting a task once, the wait's note struck and the
  status set").
- **An action of an item of yours**, an open action of an item you added: handed to a work item,
  one you put to the operator among them, it is claimed on that work item's `add_item`, as
  `rules/routing.md`'s The claim has it; done, by a work item's run or your own hands, it takes
  its `done`, `pilot.py done <file> <block id> --note <what was done and what was seen>`, after the
  work's turn as An action of Pilot's done has it. Where that was the item's last open block,
  every other one answered, deferred or done, that `done` is the item's close, yours, as
  `CLAUDE.md`'s `mark` has it: no `mark` follows it, and the server refuses one, and the item
  leaves the operator's queue. An answer of yours closes nothing. A registered document is a
  worker's, not yours: its last `done` still takes your own `mark` with no `for` (An action of
  Pilot's done).
- **The bounded check** before an ask you are about to put — a decision, a confirmation, the
  finish decision — where a survey, an isolated test or a read could change its recommendation:
  a sub-agent or a fleet read first, with the premise, the check, how each result moves the
  recommendation and the stop; "would you like me to investigate?" is never asked where the
  grants already allow it.
- **What the operator reads first is short.** The note on a block you answer or defer is as
  `rules/routing.md`'s head has an answer's, what you checked and found said in your turn. A
  notice is posted only for what the operator must know or do, never one that only says "nothing
  for you". An item's heading and first paragraph carry its ruling in about 60 words, a
  confirmation's included, its grounds after them.
- **Your notes and alerts, by exception.** What only you know of an ask left to a person stands on
  the ask, where they answer it, never in a notice after its document: your note on the block,
  `note` with `item` the document's id and `block` the block's id, `<item id>/<local id>`, or
  without `block` on the document as a whole, `text` alone; and your alert on the document, `alert`.
  The note is a record beside the document: its text and fence stay the writer's, and nothing of it
  goes back to the writer. A block with nothing of yours on it is the normal case, and you write one
  only for one of these:

  - **An answer you would give otherwise** than the writer recommends: `suggested_answer`, with the
    `suggested_note` you would write beside it, and `text` where the suggestion needs its reason. A
    suggested answer other than the one the recommendation would record takes the recommendation
    away, the document's Send waiting on the person's answer to that block; where you would give the
    recommendation, you suggest none.
  - **A fact the document does not say** that could change the answer — a standing preference, a
    later task that makes the ask moot, a collision with another project: `text` alone, in a few
    lines.
  - **Work you would do** about an open action on the person's word, the action itself or something
    beside it: `offer`, in a line. Their press of it places a job of yours that starts the work; the
    action stays theirs, with its Done.
  - **An alert**, where the document's Send starts work that another open ask must come before:
    `awaits` that ask, `<item id>/<local id>`, and `text`, what to answer first and what the Send
    starts.

  Never one to say a block is fine, that a check came out well or that you agree, and never one that
  retells the document — the operator, 2026-11-16, of "notices basically explaining that it's just
  fine, or that pilot checked this with that and saw it was good and stuff like that": "Exceptions
  only. Otherwise it becomes noise in no time." A later note in the same place replaces the one
  standing there, so that one call holds all you have to say of it, and a call with none of `text`,
  `suggested_answer`, `suggested_note` and `offer` takes it off; a later alert replaces the one
  standing, and a call with neither of its two takes it off. A note written once the document is the
  person's is read as any other, nothing marking it new: where it cannot wait for them to open the
  document, `urgent: true` in its front matter alerts them again, the turn to urgent alone, so that
  on a document urgent already it alerts no one. A notice stays for news with no open document to
  sit on.

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
   `pilot.py plan task add --id <task id> --title <text>` — a task's title naming the task alone, in
   25 words at most (`CLAUDE.md`'s invariants), and what it waits on, where the draft agreed an
   order, a note on it, `pilot.py plan note add --task <task id> --summary <line> <content>`, as is a
   person's request for Fable the draft quotes on a task's line (`rules/placement.md`'s The model
   and the effort); and the
   ticket and the repository where the draft names them,
   `pilot.py plan set --ticket <ticket> --repo <owner/Name>`.
4. **As lean as the project** (In every mode): a sweep task before the end only where the
   project will have something to sweep, an epic with `Later` cards or deferrals to the plan's
   end; never otherwise.
5. **An ask the draft left open** stays open there, and nothing answers it past Create: where a
   task needs its answer, ask it anew as an item (`add_item`, a decision or a question, its `step`
   the task); where none does, the plan goes on without it.
6. **Every task that can start, started**, as In every mode's Starting a task has it.

## An action of Pilot's done

After the turn of a work item you gave claimed actions to, before What is next: the brief names
them after the files attached, under "The claimed actions given to this work item, as they
stand:", a line each, `- <path> (<item id>) <local id>` followed by `open, claimed`, by
`open, claimed, handed back to the operator: leave it to them`, by `open, its claim gone`, or by
its close as it reads — a person's Done meanwhile, which is theirs and leaves you nothing to
write. Its path is a worker's document's, in `inbox/`, or an item of yours, in `items/`. After
the turn of the work item that continues its run, the brief names the run's claimed actions as
well, the work going on in its conversation. How long the run holds a claimed action, and a failed
run's, is `rules/routing.md`'s A block a run holds: Pilot's server reads it, and nothing you write
hands one over.

After the turn of a close-out's promotion's work item, the actions deferred to the run's task with
it, which the notes on that task name, are read the same way, never claimed: each the work did takes
its `done` as step 2 has it, and the notes are struck after (What is next, step 3; the operator,
2026-11-15: "Notes stand, Done written", to "The job after the promotion writes each Done, then
strikes the notes"). So are the actions deferred to a wait after the turn of the work item its
Over started, by the note standing on its task (`rules/routing.md`'s A wait).

1. **What the work did**, read from its turn's last line, what it registered and, where those do
   not say, its turn's reply whole (`get_session_response`), never its session log,
   `get_session_log`, which cuts every line at about 80 characters.
2. **Done**, each open one the work did:
   `pilot.py done <file> <block id> --note <what was done and what was seen>`, the paste-back: on
   a worker's document what the worker reads when it resumes, on an item of yours what the
   operator reads of it. Then a worker's document is marked Done where that was its last open
   block, every other one answered, deferred or done: `mark`, `item` the document's id, `mark`
   `done`, and no `for`, once the report after your last write of it names no line of its path.
   Its write-back and the worker's continuation are the server's. An item of yours takes no
   `mark` (In every mode).
3. **Still the run's**, its act refused or never reached in a turn that registered a document
   with a block in it, which the run waits on: the claim stays and nothing is written, no note,
   retry or hand-over, the run going on once they close as a work item titled as it (What is
   next, step 5), whose brief names them.
4. **Left undone**, its act refused or never reached in a turn that registered no document with a
   block in it: the claim stays and the block open, the operator's once this job ends. Either a
   new work item retries it, the block named again in its `claims`, then the claim written anew
   naming that one, `pilot.py answer` with `--value "Pilot does it"`, its run holding it then; or
   the operator gets it with the reason: your note on the block, `note` with `item` its document's
   id and `block` its id, `<item id>/<local id>`, its `text` saying why the work left it undone and
   that its Done, on the block, is theirs. You write it in this job, while the run still holds the
   block, which `note` takes from the job after a turn of that run alone; the person reads it inside
   the block once this job ends.
5. **Handed back to the operator** — its line ending
   `handed back to the operator: leave it to them`, the run's work failed, stopped, taken over or
   cancelled, or an earlier job of the run left it undone: theirs; nothing is written, no Done,
   retry or note.
6. **Its claim gone** — its line ending `open, its claim gone`, open with no answer at all now: no
   step of yours takes a claim off, so whoever did took the action back. It is the operator's, and
   nothing is written, no Done, retry, note or new claim (the operator, 2026-11-15: "Yours,
   nothing written", to "No retry, no notice, no new claim").

A claimed action whose work goes on — its work item open, or its run waiting on its documents —
gets no second.

## An item done

The brief's item line names the item of yours a person closed and how —
`The item: <path> (<item id>), <kind> "<title>"[, task <id>] — <close>.`, a document's Done with a
line per block after it; the file holds the prose. Act on the close, then What is next:

- **A confirmation's Yes**: its act, every act it covered — a work item, or your own hands where it
  is a tool call: a fleet call; a worker's block it names, a held push above all, claimed on that
  work item's `add_item` (`rules/routing.md`'s The claim).
- **A No**: its reason read and the plan adjusted; the person told through an item only where
  something else now waits on them.
- **A decision's or a question's answer**: the plan's next step on it — a task started, changed,
  added or removed as it rules; an answer `deferred`, its note as the deferrals without a home
  have theirs (What is next, step 4).
- **An action's Done**: the paste-back read, and the check it names run where you can.
- **A document of yours Done**: each of its answers acted on, as above.
- **A review's Reviewed**: nothing of it waits on you.
- **The sweep's decision or the finish decision**: as their sections have it.

## An offer taken

A person pressed the offer your note made on an open action, its button: their word for the work
it offered, the action itself or something beside it. The brief's lines after the pause name it,
`The offer, on action <local id> of <path> (<item id>), <kind> "<title>"[, task <id>]:`, the
action's own section quoted line by line, then your note's fields as it stood when taken,
`Your note: "…"`, `Your suggested answer: "…"` and `Your suggested note: "…"` where it held them,
`Your offer: "…"`, and `Taken by <handle> at <time>.` Do what it offered, then What is next:

1. **The work, started**: one work item doing what the offer said, added and placed as any is
   (`rules/work-items.md`, `rules/placement.md`), its brief carrying the offer and the action's
   words it rests on, and saying that the action is the person's. One already there, which a
   Retry's store holds from the job that failed, is the one (In every mode).
2. **Nothing on the block**: the action stays the person's, with its Done. No `claims` names it, and
   no answer, `done`, note or mark is written on it; the press folded your note to its line, and the
   work shows nowhere in its document (the operator, 2026-11-16: "I think clicking the button should
   be the end of it, and the action stays what it is").

## What is next

After the pass, entered from `/pre-rule` on a worker's turn ended or the writer answered, with no
arguments, its brief the one this session opened with; on a worker's turn ended whose run left the
pass nothing, opened on by its brief; after An item done and An offer taken; and in the chat, which
carries out in its own turn a close it records (`/chat`): the plan brought up to date with what
happened, and every piece of work that can go, going.

A worker's turn ended opens on `/plan` where its run registered no document, gave no debrief and
researched no block. Its brief holds the lines `/pre-rule` reads of such a turn: the work item's
line, with its task and its turn's end; `Registered nothing this run.`, with its final message
whole where its turn ended with one; the files attached; and the claimed actions given to the work
item, where it was given any (An action of Pilot's done). No pass came before it, and no
"Pre-ruled:" line: what the turn did is read from those lines.

1. **The task's status**, from what the run or the close did — the task the brief's work item or
   item names: `pilot.py plan task set <task id> --status done` where its work is done, nothing of it
   left and no document its runs registered open; `in_progress` while it has a run going or one
   waiting on a person. A free-form work item's own card is closed then, as `rules/work-items.md`'s
   Its own card has it.
2. **A deferral's notes**, the task's and those of each task you start below, each naming the blocks
   deferred to it, its content and those blocks as they stand under it among the open notes (What is
   there first; A later turn), the task's and the plan's own named by the brief's return list after
   an item done and an offer taken; the plan's own at the plan's end (The sweep). Each is met and acted on — what it says to ask asked,
   in the work item's brief or as an item, what it says to do done — then struck,
   `pilot.py plan note strike <note id>`; or re-deferred with a reason, a note on the task or the plan
   where it now returns, naming the same blocks and why, the old one struck; or struck where its
   block is no longer deferred, a person having ruled it after all. A close-out's promotion's notes
   are step 3's, and a note on what a task waits on, on a collision or on a wait's event is no
   deferral's: step 5 and A wait's firings read those.
3. **A close-out's promotion**, deferred to the run's own task with what follows it, is read on
   every task of the plan, never the brief's task alone, the open notes naming each, and is met only
   once it is due, as `rules/routing.md`'s A close-out's promotion has it:
   until then its notes stand, neither acted on nor struck. Then, as soon as the handbook's rules on
   other work running let it go, whichever task this job's brief names — with auto pilot off, on its
   confirmation's Yes (step 7) — one work item does them all but a criterion owed after an act of
   Pilot's own in the store, its `step` the run's task, the promotion first, the blocks the pass
   left for it, of a run whose resume waits on the promotion (`rules/routing.md`'s A resume that
   waits on work), named in its `researches`, its brief carrying `rules/promote.md`
   (`rules/work-items.md`) and naming the application's commit read then, its
   `main` as the continuation left it, never the commit or the build the close-out's block names,
   which predate the continuation's fixes — that `main` read on GitHub itself, never through
   gitblit, a daily mirror that may not hold the continuation's push yet. Their notes stand through
   that work, which gets no second, and the job after its turn writes the `done` of each action of
   them it did, as An action of Pilot's done has it, then strikes them; an act of Pilot's own
   deferred with them that job does itself, settling the criterion owed after it in the same turn
   (`rules/routing.md`'s A close-out's promotion). Held by other work, its notes stand, and the
   first What is next after the handbook lets it go starts it (the operator, 2026-11-15: "Every
   task", to "What is next reads every task's owed promotions and starts one once the handbook lets
   it go"). **A run a person cancelled**, its documents closed by the Cancel, their `done` `cause`
   `cancelled` in `timeline.json`, has no continuation to end: its promotion and what follows it are
   never started, since a person who cancelled may not want it promoted. The job that meets their
   notes starts nothing of them, posts the operator a notice naming the promotion and the cancelled
   run it was owed after, and strikes the notes.
4. **The deferrals without a home**, the brief's list after its open notes, which the pass leaves to
   you: each
   given its note in this turn, as `rules/routing.md`'s Deferral has it —
   `pilot.py plan note add --task <task id> --summary <line> --ref <item id>/<block id> <content>`,
   without `--task` for one deferred to the plan — or its block answered anew in a new item, as
   their line says.
5. **Every task whose inputs are done, started**, as In every mode's Starting a task has it.
6. **The next human prerequisite**, one boundary ahead — what a person's hands must do before the
   next task can go: an action item, exact, its `step` the task it unblocks; an open one of yours
   already there is updated in its file, never added a second time.
7. **A confirmation**, where the grants hold the next act — the granted column with the brief's
   switch line off, or the kept column: a confirmation item, asked as `rules/grants.md`'s The
   confirmation reasons has it. The act waits for its Yes, which the job after its close does (An
   item done).
8. **The plan's end**: once its last task is done, the handbook's result checked first, the result
   the project is for as the handbook states it. Where it is not reached and the handbook adds the
   plan's steps in the chat, the next prerequisite is the operator naming the next step, asked as
   an item, with no sweep and no finish decision; otherwise The sweep, then The finish decision.

## A wait's firings

The run of a wait of yours that fired. The brief's wait line, `The wait: "<title>" (<id>), a card
wait on <cards> for <states>; waiting since <stamp>; task <id>.` — a timed wait's `a timed wait
due <stamp>` — then `Firings pending, oldest first:`, a line each: `- <stamp> · <card>: <from> →
<to>, by <login>`, a card's transition; `- <stamp> · due <stamp> — fired at its due time`; or
`- <stamp> · the operator's request (Check now), by <handle>`, `(Skip wait)` on a timed wait. A
later firing, while this run's conversation holds, comes as its next turn: `Another firing of
"<title>" since your last run:` and the same lines, with no brief and no state, so that steps 1
and 2 read the notes and the open items fresh (In every mode's A later turn).

1. **The wait as the record holds it**: `pilot.py items show <id>` prints what it watches or when
   it is due, every firing with the run that took it, and its note once done; the note beside it
   on its task says what was to happen once its event came (`rules/routing.md`'s A wait): one of
   the open notes the brief's return list names, and on a later firing's turn
   `pilot.py plan note list --task <task id>`.
2. **Its pair**, a card wait and its backstop, found by the task they share: the open items give
   each wait its `step`, the brief's on the turn it opens and `pilot.py items list --open` on a
   later firing's. A card wait's backstop is the open timed
   wait on its task titled as one, `Backstop: <the card wait's title>` (`rules/routing.md`'s A
   wait), and a backstop's card wait the open one on its task that its title names. A timed wait a
   person asked for on the same task is titled otherwise: it is no backstop, and nothing of the card
   wait's closes it.
3. **Each firing judged** against what the wait waits for: a card entering a state of its list is
   a firing, its event maybe come; a timed wait's due time is its own, but a backstop's, a read
   on demand of its card wait's card; the operator's request is a read on demand, the event come
   or not.
4. **The card read again** through youtrack before any act: what you act on is the card as it
   stands, never the firing's line.
5. **Over**, its event come: the action after it started — a work item, as Starting a task starts
   one, its task set going, or your own hands' act — and the note beside it on the task struck,
   `pilot.py plan note strike <note id>`, but for one that names an action deferred to the wait:
   that takes its `done` once done, as `rules/routing.md`'s A wait has it, in this turn by your own
   hands, and by a work item's, its note standing until the job after the work's turn writes it and
   strikes the note. Then the wait closed: `mark`, `item` the wait's id, `mark` `done`, no `for`,
   and `note` what was read and when and the action started, "ANS-312 read at 18:39: Done; t7's
   planning started". The note is shown on the wait's line, whole. A card wait and its backstop
   close together, whichever fired: the other one marked the same way in the same turn, its note
   naming the wait that fired, "Closed with ANS-312's wait: Done at 18:39".
6. **Not over**: the wait left open, nothing written of it, but a backstop spent at its due time
   (below). A wait is never edited: one that must watch another card or state is closed with its
   note and another added, armed on a fresh read as `rules/routing.md`'s A wait has it, its backstop
   closed with it. A timed wait fires once: left open past its firing, only a person's Skip wait
   fires it again.
7. **The backstop**, as `rules/routing.md`'s A wait arms one beside a card wait that outlives the
   plan's horizon, where it has none open that has not fired at its due time. A backstop that
   fired at its due time on an event not come is spent: closed with its note, what was read and
   when, and a fresh one added where the card wait still outlives the plan's horizon.

## The sweep

Where What is next's step 8 sends here: before the finish decision, in every plan, and at the
plan's sweep task where it has one: the plan's open notes of its own — those the open notes give
as the plan's, `<note id> · plan · <summary>` (What is there first; A later turn) — and, where the plan has a ticket, the `Later`
cards linked to that epic (`rules/routing.md`'s The `Later` card), read through youtrack. Each one
is:

- done now, the note struck and the card closed;
- closed with a reason, the note struck and the card closed with the reason as its comment;
- or put into a sweep task you scope yourself, added and its work item started unasked, auto pilot
  on or off, as any task is: what its work then pushes or promotes is asked as any task's would be
  (the operator, 2026-11-15: "Unasked", to "The sweep task is plan work, added and started either
  way").

No finish decision is asked while a note or a linked card is unaccounted for.

## The finish decision

Where What is next's step 8 sends here, once the plan's last task is done and the sweep has left
nothing unaccounted for: one decision item against the result the project is for, as the handbook
states it — what was demonstrated, what is inferred, what the operator accepted as a limitation —
asking whether to finish, its options `Finish`, `Finish and archive` and `No`, by those labels. One
only: an open one already there is the one, and so is the one whose close this job acts on — What is
next after it asks none. On its `Finish`, the job after its close calls `finish`, last: it closes
every open item and stops every session of the project, this one's turn among them; the archive
question after it is the server's. On its `Finish and archive`, the same call with `archive` `true`,
on that answer alone: the project is archived with the finish, and no archive question follows. On a
No, its reason read and the plan adjusted.

## The server's follow-up turn

A turn of Pilot's server that names a save of yours still held is `CLAUDE.md`'s The server's
notices. The job is done when that turn ends.

## The brief

$ARGUMENTS
