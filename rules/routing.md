# Routing

Where an open block goes when Pilot pre-rules what a worker registered, and what each route
writes. The route is Pilot's own choice: the operator gets a block only where it has impact now
and is theirs. An answer of Pilot's is `by: agent`, its note saying why in words that stand alone,
since the block's collapsed line is the operator's first read of it. What the grants allow is
`rules/grants.md`'s; which column holds, the brief's switch line.

## The routes

| the block | the route, and what it writes |
|---|---|
| a routing ask — card it, close it, fold it, fix it now | routed: the route as the answer, the reason as the note. A card is made in the same turn through youtrack, in the operator's words where the entry carries them, and the note names it. A fold is the worker's own: the answer says fold, and the workflow folds it at its next run. In a stage's document the stage carries out every route itself, the card included (`rules/stages.md`). |
| a choice outside the grants table, or in the granted column with auto pilot on | chosen, the recommendation or not, the note saying what the choice optimised for; first a bounded check where a fact would move it. |
| a choice in the granted column with auto pilot off, or in the kept column | left to the operator, with no edit — or deferred where it has a home and is not due now (below). |
| a choice wholly another project's | answered with the hand-over (below); never deferred across projects. |
| a question the record, the handbook or the memory answers | answered. |
| an action that is the operator's hands alone — a secret, a device, an account | left to the operator, with no edit. |
| an action Pilot may run under the grants | claimed: the block named in `claims` on the `add_item` of the work item that does it, added in the same turn, then `pilot.py answer` with `--value "Pilot does it"`, the note naming that work item in words; the block stays open, Pilot's, until that work ends and `pilot.py done` writes the paste-back. Done at once, through `pilot.py done`, where Pilot's own hands do it in the pass — a card, a fleet call. |
| an owed action waiting on an event — "re-run the import once the operator has restored the backup" | a wait through `add_item`, armed on a fresh read of the card it watches; a note on the task the action belongs to; the block answered naming the wait. |
| a block Pilot cannot read — what it asks, which option the writer means, what a thing it names is — and the record does not answer | asked of its writer, once: `ask_writer` with `block`, `<item id>/<local id>`, and `question`, one question per block. |
| anything with impact now and the operator's | left to the operator, with no edit. |

## Deferral

A block is deferred only to where it returns, and never otherwise; what has no such place is
decided now, or closed.

| where it returns | its home |
|---|---|
| a planned task of this project | a note on that task |
| the running task's next turn: not in this turn | a note on the running task |
| the project's end — a sweep, a follow-up after go-live | a note on the plan, and the `Later` card (below) |
| an event — a hold lifting, a step the operator runs first | a wait, with a note beside it on the task the action belongs to |
| another project's work | none: never deferred |

- `pilot.py defer` writes the block's `answer: deferred`, `to` and note, and in the same call the
  plan note: its summary the question in a line, its content what to ask and how when the task
  comes up, its ref the block. A note points; it does not copy.
- A deferral to the running task is for an ask the turn should finish without — a clean-up the
  work does not need, a choice better made with its result in hand — never for one that waits on
  an event, which is a wait: nothing guarantees the task another turn before the event.
- A deferral from a close-out, the task's last document, goes to the next task or to the end,
  never to the running task.
- A deferral never asks the operator, with auto pilot on or off: it reads as its done line, and
  the operator quotes it into the chat to disagree.
- A person's deferral from the chat is their answer, through `answer` with `deferred` and `to`;
  Pilot writes its note in the same turn, `pilot.py plan note add` with the block as its `--ref`.

## The `Later` card

For a deferral to the project's end, when the project has an epic — the plan's ticket: a card in
the epic's tracker project, in the `Later` state and linked to the epic, its body the entry
verbatim and the note's words; the card's id goes into the note's content. It is a handle, not a
queue: it shows what the project still owes, nobody works from it, and the sweep before the
finish drains it. With no epic, the note on the plan is the one home.

## A delegated answer

When the operator delegates — "your call", "go with your recommendation", in the chat or in a
block's free words — Pilot writes the chosen option with `by: agent` and the operator's words as
the note, so that the record shows who chose. It is never restated as the operator's ruling: every
item, note or card that cites it says "chosen by Pilot on a delegated ruling: '<the operator's
words>'", and every card the choice produces carries that line.

## Another project's decision

A decision is never deferred into another project: it is this project's, decided here, now or
through a deferral within the plan, and its ruling may produce work elsewhere — a task card in the
other project, in the operator's words, marked delegated where it was. A choice wholly another
project's is answered with the hand-over: a task card in that project, in the operator's words,
named in the answer's note, marked delegated where it was.

## The friction half

An entry whose root cause is a gap in an environment or in tooling — a capability missing, a tool
absent, a wait that should not exist — is two things. The decision or action about the work stays
in the document and is routed as any block; the friction is posted to Fieldnotes, and the block's
note names the post.
