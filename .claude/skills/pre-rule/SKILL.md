---
name: pre-rule
description: Pilot's pass over what a worker's turn registered — each document's open blocks routed by the routing rules, answered, deferred, claimed or asked of their writer by Pilot or left to the operator, in the order the brief lists them, a document Pilot settled whole marked Done; and the pass after the writer answered, asking nothing — then /plan for what is next. Run it when Pilot's brief opens with /pre-rule.
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
   `Registered nothing this run.`; the files attached on the work item; the claimed actions given
   to the work item, which are `/plan`'s; the plan's open notes by summary; and the deferrals
   without a home, which are `/plan`'s too.
3. Pass over each published document, in the brief's order (The pass). A document whose read
   failed has no text: it is the operator's to mark Reviewed, and the pass writes nothing of it.
4. End the pass with its one line (The summary line), then run `/plan`, its mode What is next, in
   this session, its arguments the brief as you got it.

A job never waits and never asks in its own transcript: what a person must decide stays open in its
document, or is put to them as an item.

The rules it applies: `rules/routing.md`, each route and what it writes, deferral, the `Later`
card, a delegated answer, another project's decision and the friction half; `rules/grants.md`, what
the switch lets go ahead; `rules/work-items.md` and `rules/placement.md`, the work item that does
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
   goes into your answer's note or, on a block left to the operator, into an item of your own after
   the document (`add_item`), quoting the block's words and naming it, `<item id>/<local id>`. A
   document that reads badly is its writer's skill's to fix: the friction half
   (`rules/routing.md`), never a patch here.
4. **Each open block, routed** by `rules/routing.md`'s table, in the document's order. A block
   answered already — a person's answer, or yours from an earlier job of this trigger, which a
   Retry's store holds — is settled: leave it.
   - **Answered**, `by: agent`:
     `pilot.py answer <file> <block id> --value <option> --note <why>`, the value an option's
     label, `Agree`, `Yes`, `No` or your own words. The note says why in words that stand alone:
     the block's collapsed line, its heading, the answer and the note, is the operator's first read
     of it.
   - **Deferred**, where it has a home and is not due now, as routing's Deferral has it:
     `pilot.py defer <file> <block id> --to <task id> --summary <line> --content <text> --note <why>`,
     `--to plan` for the project's end, writes the block's `answer: deferred`, its `to` and its
     note, and the plan note on that task, in one call: the note's summary the question in a line,
     its content what to ask and how when the task comes up.
   - **Done at once**, an action your own hands do in the pass — a card, a fleet call: do it, then
     `pilot.py done <file> <block id> --note <what was done and what was seen>`.
   - **Claimed**, an action Pilot may run under the grants that a work item does: the work item
     first, through `add_item` as `rules/work-items.md` has it, its `claims` the block's id,
     `<item id>/<local id>`, beside every other action that work does; then the claim,
     `pilot.py answer <file> <block id> --value "Pilot does it" --note <its work item>`, the note
     naming the work item by its title. The block stays open and yours, out of the badge, until
     `/plan` writes its `done` when that work ends.
   - **Asked of its writer**, a block you cannot read — what it asks, which option the writer
     means, what a thing it names is — that the record does not answer: `ask_writer` with `block`,
     `<item id>/<local id>`, and `question`, in the words the writer is to read, one question per
     block. Never one the operator must decide, one a bounded check answers, or one about style.
     No edit: the pass's questions go to the writer together when this job ends, and the job
     after the answer passes over the document again (The writer answered). A call refused as one
     round per worker turn — this job a Retry of a pass that asked, the server says so — asks
     nothing more: the block is left to the operator, as one you could not read.
   - **Left to the operator**: no edit.
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
   one of more. The resume of the run is the server's. A claimed action is settled once its `done`
   is written, and a block asked of its writer is not: the document stays open, a claimed one for
   `/plan` to mark Done then. One with no block is the operator's to mark Reviewed.
7. **Left to a person**, a block or more: the document stays open. In its front matter,
   `urgent: true` where it holds up work now, and `for` the one person who can judge it, by handle,
   where the handbook or the record names them; neither where it does not hold.

## The writer answered

The job after the clarification run, which took a pass's questions to their writer: its kind line
`Pilot's brief · the writer answered · …`, then the run's line,
`The clarification run: "<title>" (<id>), of the work item "<title>" (<id>)…`, and for each
document asked about, `Asked <stamp> on <path> (<item id>):`, a question a line after its block's
local id, then the writer's answer as the document records it: a line per block, or the reply
whole, quoted, where it did not keep the asked headings, or none, where the run's turn ended with
no text. What the run registered follows, as any run's, then `This pass asks nothing: …`.

- **The pass** goes over each document asked about, in the brief's order, then each the run
  registered, as The pass has it.
- **It asks nothing**: no `ask_writer`, which the server refuses here.
- **The writer's words**: a block you now route on them quotes them in its answer's note, so that
  the operator reads the ask and its reason together; a block still unclear is the operator's,
  with no edit, the clarification beside it on the document.

## Not yet the pass's

One of `rules/routing.md`'s routes waits on work Pilot has not shipped. A block it would take is
left to the operator, with no edit, and the summary line names it.

- **A wait.** `add_item` refuses `card_wait` and `timed_wait` ("Pilot takes no waits yet"), so
  neither an owed action waiting on an event nor a deferral to an event has its route.

## The summary line

One line, a part per document in the brief's order, its path short — "Pre-ruled: inbox/7 Done (3
settled, 1 deferred to t5); inbox/8 open for the operator (D2), A1 claimed for "Rotate the CI
token", D4 asked of its writer; inbox/9 not read" — or "Pre-ruled: nothing registered". Then
`/plan`, What is next (step 4).

## The brief

$ARGUMENTS
