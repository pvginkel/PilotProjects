---
name: pre-rule
description: Pilot's pass over what a worker's turn registered — each document's open blocks routed by the routing rules, answered, deferred, claimed or asked of their writer by Pilot or left to the operator, in the order the brief lists them, a document Pilot settled whole marked Done, the stage session's debrief, where the brief carries one, left or made a notice, a card or a fieldnote; and the pass after the writer answered, asking nothing — then /plan for what is next. Run it when Pilot's brief opens with /pre-rule.
---

# Pre-rule

The pass over the documents a worker's turn registered, before the operator reads them: each open
block routed, answered, deferred, claimed or asked of its writer by you, or left to the operator, a
document you settled whole marked Done; then `/plan`, for what is next, in this same session. The
routes are yours: Pilot's server routes nothing.

1. Read `handbook.md` before anything the brief asks.
2. Read the brief, below: its kind line, `Pilot's brief · a worker's turn ended · …`, or
   `Pilot's brief · the writer answered · …` after the writer's answer (The writer answered); its
   switch line, the grants that hold for this session; a pause; the work item's line — its title,
   its task, its repository, its environment and session, its turn's end and its last line; then
   the documents the run registered, in the order registered, each
   `- <path> (<item id>) — published` or `- <path> (<item id>) — read failed: <reason>`, or
   `Registered nothing this run.`; the files attached on the work item; the stage session's
   debrief, where it gave one, `The stage session's debrief, as given:` and its words on the lines
   after it; the claimed actions given to the work item, which are `/plan`'s; the blocks it
   researched, which are the pass's; the plan's open notes by summary; and the deferrals without a
   home, which are `/plan`'s too.
3. Pass over each published document, in the brief's order (The pass), then over the blocks the
   work item researched (A researched block), then over the stage session's debrief, where the
   brief carries one (The debrief). A document whose read failed has no text: it is the operator's
   to mark Reviewed, and the pass writes nothing of it.
4. End the pass with its one line (The summary line), then run `/plan`, its mode What is next, in
   this session, its arguments the brief as you got it.

A job never waits and never asks in its own transcript: what a person must decide stays open in its
document, or is put to them as an item.

What the operator reads first is short. The note of an answer of yours — answered, deferred or
claimed — is as `rules/routing.md`'s head has it, what you checked and found said in your turn. A
notice is posted only for what the operator must know or do, never one that only says "nothing for you". An item's
heading and first paragraph carry its ruling in about 60 words, its grounds after them.

The rules it applies: `rules/routing.md`, each route and what it writes, deferral, the `Later`
card, a delegated answer, another project's decision and the friction half; `rules/grants.md`, what
the switch lets go ahead; `rules/stages.md`, what a stage of the workflow registers and what each
fate in its documents means; `rules/work-items.md` and `rules/placement.md`, the work item that does
an action you claim. The writing — an answer's note, a missing title or summary — is
`/dev:document-format`'s.

## The pass

Per published document, one after the other:

1. **Read it.** `pilot.py items show <id>` prints its line and its blocks with their answer lines;
   its file, at the brief's path, holds the prose and the asks whole. A document a person closed
   while the job waited is passed by. The open notes a block touches are a read away,
   `pilot.py plan note list`: a note that already holds its ask, or settles it, is cited in your
   answer's note, never written twice.
2. **The front matter first**, by hand, in your first edit of the file and before any answer: a
   `title` where the worker's front matter gives none — its first heading's words, copied as they
   stand, where it has one, else the document's subject in a line — and a `summary` where the front
   matter gives none and the document holds more than one block: what it is about, in a line, no
   counts. A write of the document with no title is held, so the title comes first.
3. **Nothing else of the worker's**: not its prose, not a block's definition, not its kind; no
   context added, no ask reframed, no plan condensed. What only Pilot knows — a standing preference
   that settles the need, a later task that makes the ask moot, a collision with another project —
   goes into your answer's note or, on a block left to the operator, into a notice of yours after
   the document (step 7). A document that reads badly is its writer's skill's to fix: the friction half
   (`rules/routing.md`), never a patch here.
4. **Each open block, routed** by `rules/routing.md`'s table, in the document's order: the table
   names each block's route and what it writes, and below are each route's command and what of it
   is the pass's alone. A block answered already — a person's answer, or yours from an earlier job
   of this trigger, which a Retry's store holds — is settled: leave it. In a run whose resume waits
   on work, a block you would settle is left unanswered for it (step 6).
   - **Before any choice of yours, the due diligence** of `rules/routing.md`, the project's folder
     scanned through `pilot.py plan task list`, `pilot.py plan note list`, `pilot.py items list`,
     the files under `items/` and `inbox/` and `chat.md`, and a fact the ask rests on and nobody
     read found first (Researched).
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
   goes into a notice of yours after the document (`add_item`), quoting the block's words and
   naming it, `<item id>/<local id>`, and ending with the answer you suggest and the note for it,
   as you would answer the block yourself.

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

After the turn its loop completed in, a stage's brief carries the stage session's debrief after the
files attached: the line `The stage session's debrief, as given:`, then its words, on how it feels
the loop went. A brief without that line has none, a turn that ended on a hand-back among them, and
the pass has nothing of it to do. The debrief is no document: it has no block, and nothing is
answered, marked or written of it; the operator reads it on the done work item, behind its Debrief.

Read it against the run — the work item's line, what it registered and your pass over that — then
do with it what you do with the rest, one of these, or more where it holds more than one thing:

- **Nothing**, where it holds nothing the operator must know or do and nothing to change.
- **A notice**, only where the operator must know or do something: through `add_item`, quoting the
  debrief's words it rests on, and ending with what you suggest. Never one that retells the
  debrief or says the loop went well: the operator reads it behind the Debrief.
- **A card**, for a change the debrief shows is needed, in the work's repository or in the
  workflow: made through youtrack in your turn, in the project of what it is about, AIWorkflow's
  own for the workflow, its text the debrief's words it rests on, quoted, and what is to change.
  Before you make it, search that project through youtrack for an open card on the same change:
  where one is open, add the debrief's words it rests on to that card as a comment, quoted, and
  make no card, so that a friction that comes back run after run stays one card that records each
  return. A finding a document of the stage holds already, a close-out's among them, is that
  document's, its fate the stage's to carry out: no card of it (`rules/stages.md`).
- **A fieldnote**, for friction the debrief names in an environment or in tooling, posted to
  Fieldnotes as routing's friction half has it (`rules/routing.md`); where the post answers with
  one already there for the same friction, that one is fine: react to it.

## The writer answered

The job after the clarification run, which took a pass's questions to their writer: its kind line
`Pilot's brief · the writer answered · …`, then the run's line,
`The clarification run: "<title>" (<id>), of the work item "<title>" (<id>)…`, and for each
document asked about, `Asked <stamp> on <path> (<item id>):`, a question a line after its block's
local id, then the writer's answer as the document records it: a line per block, or the reply
whole, quoted, where it did not keep the asked headings, or none, where the run's turn ended with
no text. What the run registered follows, as any run's, then `This pass asks nothing: …`, and
last the stage session's debrief, where it gave one, in the lines The debrief reads.

- **The pass** goes over each document asked about, in the brief's order, then each the run
  registered, as The pass has it.
- **It asks nothing**: no `ask_writer`, which the server refuses here.
- **The debrief**, where the brief carries one, after the documents, as The debrief has it.
- **The writer's words**: a block you now route on them quotes them in its answer's note, so that
  the operator reads the ask and its reason together; a block still unclear is the operator's,
  with no answer line, the clarification beside it on the document.

## The summary line

One line, a part per document in the brief's order, its path short — "Pre-ruled: inbox/7 Done (3
answered, 1 deferred to t5); inbox/8 open for the operator (D2), A1 claimed for "Rotate the CI
token", Q3 researched by "Count the hosts", D4 asked of its writer; inbox/9 not read; inbox/6 Q2
answered on its research" — or "Pre-ruled: nothing registered"; where the brief carries a
debrief, a last part says what came of it: "the debrief: nothing", or the notice, the card by its
id, the comment by its card's id, or the post. Then `/plan`, What is next (step 4).

## The brief

$ARGUMENTS
