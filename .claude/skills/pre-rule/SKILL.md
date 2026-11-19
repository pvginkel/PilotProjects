---
name: pre-rule
description: Pilot's pass over what a worker's turn registered — each document's open blocks routed by the routing rules, answered, deferred, claimed or asked of their writer by Pilot or left to the operator, in the order the brief lists them, Pilot's note on a block or an alert on a document only by exception, a document Pilot settled whole marked Done, the stage's full debrief, where the brief carries one, read against the project's journal, the journal kept and only what is notable written as Pilot's lines in the debrief's notice, with no card, note or notice of it; and the pass after the writer answered, asking nothing — then /plan for what is next. Run it when Pilot's brief opens with /pre-rule.
---

# Pre-rule

The pass over the documents a worker's turn registered, before the operator reads them: each open
block routed, answered, deferred, claimed or asked of its writer by you, or left to the operator, a
document you settled whole marked Done; then `/plan`, for what is next, in this same session. The
routes are yours: Pilot's server routes nothing. Where the brief carries the stage's debrief, the
pass keeps the project's journal from it and writes the operator only what is notable (The
debrief). A worker's turn whose run left the pass nothing — no document registered, no debrief and
no researched block — opens on `/plan` itself, and this skill is not run for it.

1. Read the brief, below: its kind line, `Pilot's brief · a worker's turn ended · …`, or
   `Pilot's brief · the writer answered · …` after the writer's answer (The writer answered); its
   switch line, the grants that hold for this session; a pause; the work item's line — its title,
   its task, its repository, its environment and session, its turn's end and its last line; then
   the documents the run registered, in the order registered, each
   `- <path> (<item id>) — published` or `- <path> (<item id>) — read failed: <reason>`, or
   `Registered nothing this run.`; the files attached on the work item; the stage's full debrief,
   where its session gave one, from `The stage session's debrief, as given:` to the project's
   journal, in the lines The debrief reads; the claimed actions given to the work item, which are
   `/plan`'s; the blocks it researched, which are the pass's; then the project's state as the
   record held it when the brief was composed, each part as `pilot.py` prints its listing, and a
   part with nothing in it left out, its heading too:
   `This job is seq <n> on the timeline; the item its trigger names, seq
   <m>.`, that item the work item or the clarification run; `The plan's tasks not done, in its
   order, …`; `The open items, …`; `The open plan notes, whole, …`, each with its content and the
   blocks it names, as they stand; the deferrals without a home, which are `/plan`'s too; and last
   `The project's handbook, handbook.md, whole:`. You read them there: on this turn no
   `pilot.py plan task list`, `pilot.py plan note list` or `pilot.py items list --open` is run for
   what the brief carries, and `handbook.md` is not read first. A later turn of this session, one
   of Pilot's server, carries no brief and no state: what it acts on is read fresh through those
   three, never taken from the brief above it (`CLAUDE.md`'s Who you are).
2. Pass over each published document, in the brief's order (The pass), then over the blocks the
   work item researched (A researched block), then over the stage's full debrief, where the brief
   carries one, read against the project's journal (The debrief). A document whose read failed has
   no text: it is the operator's to mark Reviewed, and the pass writes nothing of it.
3. End the pass with its one line (The summary line), then run `/plan`, its mode What is next, in
   this session, with no arguments: the brief is in this session already, where `/plan` reads it,
   and it is never passed on or written out again.

A job never waits and never asks in its own transcript: what a person must decide stays open in its
document, or is put to them as an item.

What the operator reads first is short. The note of an answer of yours — answered, deferred or
claimed — is as `rules/routing.md`'s head has it, what you checked and found said in your turn. A
notice is posted only for what the operator must know or do, never one that only says "nothing for you". An item's
heading and first paragraph carry its ruling in about 60 words, its grounds after them.

**Your notes and alerts, by exception.** What only you know of an ask left to a person stands on
the ask, where they answer it, never in a notice after its document: your note on the block,
`note` with `item` the document's id and `block` the block's id, `<item id>/<local id>`, or without
`block` on the document as a whole, `text` alone; and your alert on the document, `alert`. The note
is a record beside the document: its text and fence stay the writer's, and nothing of it goes back
to the writer. A block with nothing of yours on it is the normal case, and you write one only for
one of these:

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
document, `urgent: true` in its front matter alerts them again, the turn to urgent alone, so that on
a document urgent already it alerts no one. A notice stays for news with no open document to sit
on. Of a debrief neither a note nor a notice is written: its news are your lines in the debrief's
notice, which the pass after the stage's turn writes through `write_notable`.

The rules it applies: `rules/routing.md`, each route and what it writes, deferral, the `Later`
card, a delegated answer, another project's decision and the friction half; `rules/grants.md`, what
the switch lets go ahead; `rules/stages.md`, what a stage of the workflow registers and what each
fate in its documents means; `rules/work-items.md` and `rules/placement.md`, the work item that does
an action you claim, its brief the work's own part alone, since Pilot's server appends the grants
text the switch selects. The writing — an answer line or its note by hand, a missing title or
summary — is `/dev:document-format`'s, loaded before you write one; a `pilot.py` write is not.

## The pass

Per published document, one after the other:

1. **Read it.** `pilot.py items show <id>` prints its line and its blocks with their answer lines,
   and your notes and alert standing on it; its file, at the brief's path, holds the prose and the
   asks whole. A document a person closed while the job waited is passed by. The open notes a block
   touches are in the brief, whole: a note that already holds its ask, or settles it, is cited in
   your answer's note, never written twice.
2. **The front matter first**, by hand, in your first edit of the file and before any answer: a
   `title` where the worker's front matter gives none — its first heading's words, copied as they
   stand, where it has one, else the document's subject in a line — and a `summary` where the front
   matter gives none and the document holds more than one block: what it is about, in a line, no
   counts. A write of the document with no title is held, so the title comes first.
3. **Nothing else of the worker's**: not its prose, not a block's definition, not its kind; no
   context added, no ask reframed, no plan condensed. What only Pilot knows — a standing preference
   that settles the need, a later task that makes the ask moot, a collision with another project —
   goes into your answer's note or, on a block left to a person, into your note on the block (step
   7), beside the document's text and never in it. A document that reads badly is its writer's
   skill's to fix: the friction half (`rules/routing.md`), never a patch here.
4. **Each open block, routed** by `rules/routing.md`'s table, in the document's order: the table
   names each block's route and what it writes, and below are each route's command and what of it
   is the pass's alone. A block answered already — a person's answer, or yours from an earlier job
   of this trigger, which a Retry's store holds — is settled: leave it. In a run whose resume waits
   on work, a block you would settle is left unanswered for it (step 6).
   - **Before any choice of yours, the due diligence** of `rules/routing.md`, the project's folder
     scanned: the handbook, the tasks not done, the open items and the open notes in the brief;
     what the brief leaves out, the tasks done and the items closed, through
     `pilot.py plan task list` and `pilot.py items list`; the files under `items/` and `inbox/`;
     and `chat.md`; and a fact the ask rests on and nobody read found first (Researched).
   - **Answered**, `by: agent`:
     `pilot.py answer <file> <block id> --value <option> --note <why>`, the value an option's
     label, `Agree`, `Yes`, `No`, a routing ask's fate as `rules/stages.md`'s A fate in a stage's
     document names it, or your own words, the note as routing's head has it.
   - **Deferred**, where it has a home and is not due now, as routing's Deferral has it:
     `pilot.py defer <file> <block id> --to <task id> --summary <line> --content <text> --note <why>`,
     `--to plan` for the project's end, writes the block's `answer: deferred`, its `to` and its
     note, and the plan note on that task, in one call: the note's summary the question in a line,
     its content what to ask and how when the task comes up. A close-out's promotion, the update
     that follows it and every action the close-out owes after it are deferred so, `--to` the
     run's own task, never claimed (`rules/routing.md`'s A close-out's promotion), but a criterion
     owed after an act of Pilot's own in the store, which goes with that act, as that section has
     it.
   - **Done at once**, an action your own hands do in the pass — a card, a fleet call: do it, then
     `pilot.py done <file> <block id> --note <what was done and what was seen>`; a criterion the
     close-out owes after that act is settled in the same turn (`rules/routing.md`'s A close-out's
     promotion).
   - **Confirmed first**, an action of the granted column while auto pilot is off, a run's held
     push above all: no answer line, and a confirmation item through `add_item`, asked as
     `rules/grants.md`'s The confirmation reasons has it, `because` `auto-pilot-off`, naming the
     block, `<item id>/<local id>`, one covering every such block due at once; the job after its
     close claims it on its Yes (`/plan`'s An item done).
   - **Claimed**, an action Pilot may run under the grants that a work item does, as
     `rules/routing.md`'s The claim has it: the work item first, through `add_item` as
     `rules/work-items.md` has it, its `claims` the block's id, `<item id>/<local id>`, beside
     every other action that work does; then the claim,
     `pilot.py answer <file> <block id> --value "Pilot does it" --note <its work item>`, the note
     naming the work item by its title.
   - **Researched**, a block whose choice waits on a fact nobody read that the store does not hold
     (`rules/routing.md`'s Due diligence, step 4): the work item first, placed where the repository
     is and added as `rules/work-items.md` has it, its `researches` the block's id,
     `<item id>/<local id>`; the block left open and yours, with no answer line, until the pass
     after that work's turn routes it (A researched block).
   - **Waited on**, an owed action waiting on an event, or another block that waits on one, as
     `rules/routing.md`'s A wait has it: the wait first, on a fresh read through youtrack of the
     card it watches — `add_item` with `kind` `card_wait`, its `title`, `cards` and `states` and
     `step`, or `kind` `timed_wait` with its `due_at` — then an action deferred, naming the wait,
     `pilot.py defer <file> <block id> --to <task id> --summary <line> --content <text> --note <why>`,
     and another block answered naming it, `pilot.py answer` and `pilot.py plan note add`.
   - **Asked of its writer**, a block you cannot read — what it asks, which option the writer
     means, what a thing it names is — that the record does not answer: `ask_writer` with `block`,
     `<item id>/<local id>`, and `question`, in the words the writer is to read, one question per
     block. Never one the operator must decide, one a bounded check answers, or one about style.
     No answer line: the pass's questions go to the writer together when this job ends, and the job
     after the answer passes over the document again (The writer answered). A call refused as one
     round per worker turn — this job a Retry of a pass that asked, the server says so — asks
     nothing more: the block is left to the operator, as one you could not read.
   - **Left to the operator**: step 7.
5. **The report after each write.** Each `pilot.py` verb exits 0, done, or 2, refused with
   nothing written and its reason, which you fix the call for. The tool's result after its `Bash`
   call, as after an `Edit`, carries the project's report (`CLAUDE.md`, the check after every
   writing tool call). A line naming the document's path, `<folder>/<its path>`, is about your
   write of it: a fault that holds the save, which you fix and write again, or a line the record
   reverted, after which you read the file again before you go on. A `not yet checked` line naming
   it or the folder says nothing yet: the next call's report does.
6. **Settled whole** — every block answered, deferred or done, by you or by a person — the
   document is marked Done: `mark`, `item` the document's id, `mark` `done`, and no `for`, once the
   report after your last write of it names no line of its path, a document of a single block as
   one of more. A run whose resume waits on work (`rules/routing.md`'s A resume that waits on work)
   is not settled whole: the blocks you would settle are left unanswered for that work, as that
   section has it, and the document is not marked Done. The resume of the run is the server's. A
   claimed action is settled once its `done` is written, and a block asked of its writer is not:
   the document stays open, a claimed one for `/plan` to mark Done then. One with no block is the
   operator's to mark Reviewed.
7. **Left to a person**, a block or more, left to the operator by the table: no answer line is
   written on it, and the document stays open. In its front matter, `urgent: true` where it holds
   up work now, and `for` the one person who can judge it, by handle, where the handbook or the
   record names them; neither where it does not hold. What only Pilot knows of the block (step 3)
   is your note on it, by exception (Your notes and alerts): `note` with `block` its id, the answer
   you would give suggested only where you would answer otherwise than the writer recommends, the
   fact alone where you know something that could change the answer, and no note where you would
   give the recommendation and know nothing more. What the document as a whole needs said that it
   does not show is your note without `block`; where its Send starts work another open ask must
   come before, your `alert` on it. No notice of yours follows the document.

## A researched block

After the turn of a work item you gave a research, the brief names the blocks it researched after
the claimed actions, under "The blocks this work item researched, as they stand:", a line each,
`- <path> (<item id>) <local id>` followed by `open`, by
`open, handed back to the operator: leave it to them`, by `open, claimed`, or by its answer as it
reads. Each sits in a document an earlier pass left it open in, not in one the research
registered. After the turn of the work item that continues its run, the brief names the run's
researched blocks as well. How long the run holds one, and a failed run's, is `rules/routing.md`'s
A block a run holds.

1. **What the research found**, read from what the run registered, passed over first, its turn's
   last line and, where those do not say, its turn's reply whole (`get_session_response`),
   never its session log, `get_session_log`, which cuts every line at about 80 characters. A block
   held for work its run's resume waits on is found once that work's run is done with it: do
   first what the note on that work's task says comes between, then route the block as the pass
   would have.
2. **Routed**, each `open` one whose fact the run found, as The pass's step 4 has it, the fact
   read, what was found and where said in your turn, and the note giving the choice and its one
   reason; its document marked Done once settled whole (The pass, step 6).
3. **Still the run's**, an `open` one whose fact was not found in a turn that registered a
   document with a block in it, the run asking a person first: nothing is written, the run going
   on once they close, and the pass after its next turn routes it.
4. **Not found**, an `open` one whose fact was not found in a turn that registered no document
   with a block in it: routed now as any block, your turn saying the fact stayed unread — a choice
   that would not move on it made, the question researched anew in a new work item, or left to
   the operator. Left open, it is theirs once this job ends, unless a new research names it.
5. **Handed back to the operator** — its line ending
   `handed back to the operator: leave it to them`, the run's work failed, stopped, taken over
   or cancelled, or an earlier job of the run left it open: theirs; nothing is written.
6. **Claimed since, or answered**: settled; leave it.

## The debrief

After the turn its loop completed in, a stage's brief carries the stage's full debrief after the
files attached, each heading a line of its own:

- `The stage session's debrief, as given:`, then its words, on how it feels the loop went.
- `The debrief's entries, each whole and as given, in the order given, under its section, round,
  role and time:`, then the entry of every agent the loop dispatched, each
  `- <section> · round <n> · <role> · <time>`, ending ` · passed` or ` · failed` where it has a
  result; under it, set in, `Why this round was needed: <why>` where it opens a round past the
  first, then its words. Left out, its heading too, where the debrief has no entry.
- `The loop's figures, as given:`, then the figures: phases, rounds, consults, durations, cost.
  Left out where the stage gave none.
- `The work items the debrief's notice carries, each with the time its stage took, its turns
  summed:`, then `- "<title>" (<item id>) — <time>` per work item, in timeline order, a slice's
  planning before its run; a planning's brief lists itself and each earlier planning of its
  subject. The time is Pilot's server's, the stage's turns summed and the waits between them
  counting nothing: `<1m`, `17m` or `1h 40m`.
- `The project's journal, journal.md, whole:`, then its text; or the one line
  `The project's journal: journal.md, empty.`

A brief without the first of these lines has none, a turn that ended on a hand-back among them,
and the pass has nothing of it to do. The debrief is no document: it has no block, and nothing is
answered or marked of it; the operator reads it in the debrief's notice, under its Details, and
behind the Debrief of the done work item. Nothing of a debrief is in the project's folder, and no
chat reads one: what stays of a stage in the folder is your account of it, the journal.

What you do with it, in this order:

1. **Read the stage against the journal.** The full debrief — the stage session's words, every
   role's entry, the figures and the stage's time — read against the run, the work item's line,
   what it registered and your pass over that, and against the journal as the brief carries it:
   what it is watching, and what the project's earlier stages took and met.
2. **Keep the journal**, `journal.md` in the project's folder, your running account of how the
   project's workflow runs go, after every stage that gives a debrief, a planning's as a run's.
   Its shape, a default:

   - a short head you rewrite: what you are watching, each pattern with the slices it showed in;
   - then one dated entry per stage, appended, under the day its turn ended and its work item's
     title: what happened with the slice and its figures, in your words.

   More where you judge it warranted, in the head, an entry or a part of its own — the operator,
   2026-11-19: "Your suggestion is a fine default, but if the agent feels more information is
   warranted, it's allowed to add it. No frivolous dribble though." No filler: a verdict such as
   "went smoothly" is none. Never a debrief or an entry copied whole: the journal is your account,
   so that the project's folder still carries no debrief. It is prose of your own, as
   `handbook.md` is, with no block in it, and the format skill is not loaded for it. The report
   after your write is read for its lines naming `journal.md` — a line reverted, a fault that
   holds the save — and the journal written again until it names none. A Retry's pass may find
   this stage's entry there already, an earlier job's of this trigger: that entry is brought up to
   date, and no second one appended.
3. **An account, not a tracker.** An entry actions nothing, and never stands in for a fieldnote —
   the operator, 2026-11-18: "Stuff in the handbook won't be actioned. Fieldnotes are." The
   journal is this project's own: a pattern spread over several projects goes unseen, which the
   operator accepts ("Yes, that's an accepted limitation.").
4. **What is notable, and only that**, as your lines in the debrief's notice — the operator,
   2026-11-18: "if it finds any notable events for me, it writes only those." Where the stage,
   read against the journal, holds something the operator would want to know, write that:
   `write_notable` with `text`, Markdown. For example: a friction met in a third slice, one that
   is solved, a first such as a project's first stop, a stage far off what the project's stages
   usually take. These are examples and no list: what is notable is yours to judge, with no
   threshold and no cap. Where the stage holds nothing of the kind, no call: the notice then shows
   the stages' times and the debriefs alone, and no lines say that nothing was notable or that the
   loop went well.

   The call names no work item: the lines are on the debrief this brief carries. A later call
   replaces the lines standing, a Retry's included, so that one call holds all you have to say.
   The notice shows them right under the stages' times, with no heading of its own over them and
   nothing saying which work item they are about, above the debriefs, which stand closed under
   Details: write them to be read first and alone, the lead first, naming the stage a line is
   about where the notice carries more than one. A line may point at the journal by the tag
   `<quoted_path path="journal.md">…</quoted_path path="journal.md">`, which the app draws as a
   chip that opens it.
5. **A planning's pass journals only.** The notice is placed once the pass after the run has
   ended, and carries both stages: what a planning holds goes into its journal entry, and the pass
   after the run, whose brief carries that entry, writes the lines on both. After the turn of a
   `/dev:plan-slice` work item, no `write_notable`.
6. **No card, no note, no notice.** No card is made from a debrief, in any project, and no
   comment is added to one — the operator, 2026-11-18: "Pilot shouldn't have raised cards from
   this at all. This should all have gone into fieldnotes." Neither a note nor a notice is
   written of it (Your notes and alerts): its news are your lines. A finding a document of the
   stage holds already, a close-out's among them, is that document's, its fate the stage's to
   carry out (`rules/stages.md`).
7. **A fieldnote, where it fits.** Friction the debrief names in an environment or in tooling may
   be posted to Fieldnotes as routing's friction half has it (`rules/routing.md`); where the post
   answers with one already there for the same friction, that one is fine: react to it. Nothing
   the operator reads says that you posted: not your lines, not the journal, not the summary
   line.

## The writer answered

The job after the clarification run, which took a pass's questions to their writer: its kind line
`Pilot's brief · the writer answered · …`, then the run's line,
`The clarification run: "<title>" (<id>), of the work item "<title>" (<id>)…`, and for each
document asked about, `Asked <stamp> on <path> (<item id>):`, a question a line after its block's
local id, then the writer's answer as the document records it: a line per block, or the reply
whole, quoted, where it did not keep the asked headings, or none, where the run's turn ended with
no text. What the run registered follows, as any run's, then `This pass asks nothing: …`, and
last the stage's full debrief, where its session gave one, in the lines The debrief reads.

- **The pass** goes over each document asked about, in the brief's order, then each the run
  registered, as The pass has it.
- **It asks nothing**: no `ask_writer`, which the server refuses here.
- **The debrief**, where the brief carries one, after the documents, as The debrief has it.
- **The writer's words**: a block you now route on them quotes them in its answer's note, so that
  the operator reads the ask and its reason together; a block still unclear is the operator's,
  with no answer line, the clarification beside it on the document.

## The summary line

One line, a part per document in the brief's order, its path short — "Pre-ruled: inbox/7 Done (3
answered, 1 deferred to t5); inbox/8 open for the operator (D2, your note on it), A1 claimed for
"Rotate the CI token", Q3 researched by "Count the hosts", D4 asked of its writer; inbox/9 not
read; inbox/6 Q2 answered on its research" — or "Pre-ruled: nothing registered"; where the brief
carries a debrief, a last part says what came of it: "the debrief: journalled", or "the debrief:
journalled, lines in its notice"; a fieldnote you posted is not named. Then `/plan`, What is next
(step 3).

## The brief

$ARGUMENTS
