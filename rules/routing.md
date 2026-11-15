# Routing

Where an open block goes when Pilot pre-rules what a worker registered, and what each route
writes; the claim route also takes an open action of an item of Pilot's own that a work item does
(The claim). The route is Pilot's own choice: the operator gets a block only where it has impact
now and is theirs. An answer of Pilot's — answered, deferred or claimed — is `by: agent`, its note
saying why in words that stand alone, since the block's collapsed line is the operator's first
read of it: at most two sentences, the choice and its one reason, with no "Checked:" and no bare
ids (the operator, 2026-11-04). What Pilot checked and what it found goes to the session log, said
in its turn: the note gives no account of the checks, and carries a found fact only where it is
the choice's one reason. What the grants allow is `rules/grants.md`'s; which column holds, the
brief's switch line.

## The routes

| the block | the route, and what it writes |
|---|---|
| a routing ask — card it, close it, fold it, fix it now | answered: its fate as the answer, in the words of `rules/stages.md`'s A fate in a stage's document, the reason as the note. A card is made in the same turn through youtrack, in the operator's words where the entry carries them, and the note names it. A fold is the worker's own: the answer says fold, and the workflow folds it at its next run. In a stage's document the stage carries out every fate itself, the card included (`rules/stages.md`). |
| a close-out's ask to correct design/database.md to what was built — an attribute's line, an assertion, an entity's note: the record brought in line with the build, the product unchanged | answered, auto pilot on or off: `Agree`, or the option that makes the edit, the note saying it stands on the operator's standing word, in at most two sentences. It is a correction (D015), even where the entry says "on the operator's word" (the operator, 2026-11-07: "database.md correction asks may always be done … You may always accept these."; 2026-11-15: "Absorb with the exception", to "Pilot accepts a database.md correction, and stages.md names the exception"). An entry whose ruling picks between behaviours or changes the code is routed by the other rows, even where one option edits design/database.md; a change to the record's conventions stays in the grants' kept column. |
| a choice outside the grants table, or in the granted column with auto pilot on | answered, Pilot's choice, the recommendation or not, after the due diligence below, the note saying what the choice optimised for — unless the row after takes it. A slice's requirement only where Pilot can rule it safely (the operator, 2026-10-31: "If it can rule safely, let it."): one Pilot cannot rule safely, one the due diligence leaves in doubt among them, is left to the operator, with no edit (the operator, 2026-11-15: "A condition", to "A requirement Pilot cannot rule safely is left to you"). |
| a requirement whose ruling would overrule a passage of the design record — the ask says which passage or decision | answered, Pilot's choice, only where the ask carries the operator's own words asking for that change, x into y, and the passage is the record of that very behaviour: a clean match. Left to the operator, with no edit, where the ruling's side effect lands on another passage or decision — the record pins that, as a unit test pins a behaviour — and where the operator's request names no existing behaviour and hits one (the operator, 2026-11-01). |
| a choice in the granted column with auto pilot off, or in the kept column | left to the operator, with no edit — or deferred where it has a home and is not due now (below). |
| a choice wholly another project's | answered with the hand-over (below); never deferred across projects. |
| a question the record, the handbook or the memory answers | answered. |
| an action that is the operator's hands alone — a device, an account, a secret no repository's tooling can place, a mockup, which they make themselves | left to the operator, with no edit. |
| an action of the granted column while auto pilot is off — a run's held push above all | confirmed first: no answer line, and a confirmation item asked for it, `because` `auto-pilot-off` (`rules/grants.md`'s The confirmation reasons), naming the block, `<item id>/<local id>`; on its Yes, claimed for the work item that does it (The claim), never left for the operator's hands (the operator, 2026-11-15: "Confirmation, then an agent", to "On your Yes Pilot claims the action and a work item does it"). A close-out's promotion takes its own row, its confirmation asked when it is due. |
| an action Pilot may run under the grants — a secret placed through a repository's tooling, an Ansible work item, a design, a design session or an arch design (`rules/placement.md`'s A design), among them | claimed, unless the row after takes it (The claim). Done at once, through `pilot.py done`, where Pilot's own hands do it in the pass — a card, never asked (`rules/grants.md`), or a fleet call its column lets go. |
| a close-out's promotion, with what follows it, auto pilot on or off | deferred to the running task, never claimed, its confirmation, with auto pilot off, asked when it is due (A close-out's promotion). |
| an owed action waiting on an event — "re-run the import once the operator has restored the backup" — or another block that waits on one | waited on: the wait, its backstop and its note, the action deferred to its task and any other block answered naming the wait (A wait). |
| a block Pilot cannot read — what it asks, which option the writer means, what a thing it names is — and the record does not answer | asked of its writer, once: `ask_writer` with `block`, `<item id>/<local id>`, and `question`, one question per block. |
| anything with impact now and the operator's | left to the operator, with no edit. |

## The claim

An action Pilot may run under the grants that a work item does is claimed: a worker's document's,
as the routes have it, or an open action of an item you added, in `items/`, that a work item does
— one you put to the operator and find a work item can do under the grants, or one a person hands
to a worker in the chat. The block is named in `claims` on the `add_item` of the work item that
does it, added in the same turn, then `pilot.py answer` with `--value "Pilot does it"`, the note
naming that work item in words. It stays open and Pilot's, out of the badge, through that work's
run (A block a run holds), and the job after the work's turn writes its `done`, the paste-back
(`/plan`'s An action of Pilot's done); an act the run leaves undone is the operator's again.

On an item of yours, where that was the item's last open block, its `done` is the item's close,
with no `mark` after it and no undo, so that the item leaves the operator's queue once the work has
done it; a work item that does it unclaimed leaves it open there. An action a person answered or
did is theirs, and `researches` names a worker's document's blocks alone.

## A block a run holds

A claimed action, or a block left open on a research (Due diligence, step 4), stays the run's
until the job after a turn of it that registered no document with a block in it ends (never a
clarification run's turn, which registers nothing), or its work fails or is stopped, or a person
cancels the run: Pilot's server reads that, and nothing Pilot writes hands one over. A run that
failed gets no job: its work item waits on a person's Resume, the blocks it holds standing open,
a claim with its answer, the operator's until it resumes, and the end of its next turn brings the
job after it.

## Due diligence

What Pilot does before it chooses, every choice, in the project's folder (the operator,
2026-11-01). What was checked and what was found, or that nothing in the store bears on the
choice, is said in Pilot's turn and kept from the note as the head has it.

1. **The project document and the handbook**: a goal, a rule or a standing instruction that
   settles the choice, or bends it.
2. **The store, for earlier material on the same subject**: the plan's tasks and notes, the
   earlier items and inbox documents, the chat — a cursory scan of the project's folder suffices;
   nothing outside it is owed.
3. **A match read**: where earlier work touches the choice, how it bears on it — an earlier ruling
   it follows or contradicts, a plan it was taken under — said as the head has it.
4. **A question researched**: where the ask is a question rather than a researched fact — its own
   grounds say a thing was not checked, or the recommendation rests on a fact nobody read — the
   fact is found before the choice: in the store where it is there; otherwise through a work item
   placed in an environment that has the repository, its brief the question and a document to
   register with the answer, the block named in `researches` on its `add_item`, left open and
   Pilot's meanwhile, and routed by the pass after that document, whose brief names it. A choice
   that would not move on the fact is made without it, Pilot's turn saying so.

## Deferral

A block is deferred only to where it returns, and never otherwise; what has no such place is
decided now, or closed.

| where it returns | its home |
|---|---|
| a planned task of this project | a note on that task |
| the running task's next turn: not in this turn | a note on the running task |
| the run's end: a close-out's promotion and what follows it | a note on the running task, due once the run's continuation has ended (A close-out's promotion) |
| the project's end — a sweep, a follow-up after go-live | a note on the plan, and the `Later` card (below) |
| an event — a hold lifting, a step the operator runs first | a wait, with its note on the task the action belongs to (A wait) |
| another project's work | none: never deferred |

- `pilot.py defer` writes the block's `answer: deferred`, `to` and note, and in the same call the
  plan note: its summary the question in a line, its content what to ask and how when the task
  comes up, its ref the block. A note points; it does not copy.
- A deferral to the running task is for an ask the turn should finish without — a clean-up the
  work does not need, a choice better made with its result in hand — never for one that waits on
  an event, which is a wait: nothing guarantees the task another turn before the event. A
  close-out's promotion is the one exception (A close-out's promotion).
- A deferral from a close-out, the task's last document, goes to the next task or to the end, but
  for its promotion and what follows it, which go to the running task (A close-out's promotion).
- A deferral never asks the operator, with auto pilot on or off: it reads as its done line, and
  the operator quotes it into the chat to disagree.
- A person's deferral from the chat is their answer, through `answer` with `deferred` and `to`;
  Pilot writes its note in the same turn, `pilot.py plan note add` with the block as its `--ref`.

## A wait

A block that waits on an event — an owed action, "re-run the import once the operator has restored
the backup", a hold lifting, a step the operator runs first — is waited on, written once here (the
operator, 2026-11-15: "One section, the action deferred", to "A wait written once, an action always
deferred to its task"):

- **The wait**, through `add_item`, its `step` the task the action belongs to: a `card_wait` armed
  on a fresh read of the card it watches, or a `timed_wait` with its `due_at` for an event at a
  time.
- **The backstop**: a timed wait beside a card wait that outlives the plan's horizon, its `step`
  the same task and its title `Backstop: <the card wait's title>`.
- **The note** on that task, naming the wait and saying what is to happen once its event comes,
  which the wait's run reads (`/plan`'s A wait's firings).
- **The block's write**: an action deferred to its task, through `pilot.py defer`, whose plan note
  is that note; any other block answered naming the wait, through `pilot.py answer`, and the note
  added beside it, `pilot.py plan note add`.
- **Its `done`**: deferred, an action still takes its `done` once the event has come and the work
  has done it, `pilot.py done` — in the wait's run where Pilot's own hands do it, and where a work
  item does it, by the job after that work's turn, the note standing until then, as a close-out's
  promotion's do (`/plan`'s An action of Pilot's done).

## A close-out's promotion

A close-out's promotion, auto pilot on or off, goes with the update that follows it, the store's
after a PilotApp promotion, and every action the close-out owes after the promotion — a
criterion's `Settle <id> after …`. Each is deferred to the running task, never claimed: each
through `pilot.py defer`, `--to` the run's own task, so that the close-out closes once its other
blocks are answered and the run's continuation goes on, and so that the promotion takes the fixes
of the run's continuation. It is the one deferral to the running task that waits on an event
(Deferral): the event it waits on is the end of the run's continuation, whose turn a job of
Pilot's follows.

They are due once that continuation has ended, the work item that continues the run done after a
turn that registered no document with a block in it; until then their notes stand. One work item
then does them all but a criterion owed after an act of Pilot's own (below), the promotion first,
its brief carrying `rules/promote.md` (`/plan`'s What is next); with auto pilot off, its
confirmation is asked then, and the work item starts on its Yes. Their notes stand through that
work, and the job after its turn writes the `done` of each action it did, then strikes them, so
that the record shows each owed action done. A run a person cancels has no
continuation: its promotion and what follows it are never started, and go to the operator as a
notice naming the promotion, the notes struck (`/plan`'s What is next).

A criterion the close-out owes after an act of Pilot's own in the store — a handbook line it
rewrites, a memory it removes — stays out of the promotion's work item, whose worker runs outside
the store and cannot see the act. It is deferred with that act, wherever the act is deferred, its
note naming both blocks. The job that meets that note does the act and then settles the criterion
in the same turn, its `done` written: after a promotion, the job after the promotion's work item's
turn, which reads the run task's notes; where the pass does the act at once, the pass settles it
(the operator, 2026-11-15: "Same job", to "The job that does the act settles the check in that
turn").

## The `Later` card

For a deferral to the project's end, when the project has an epic — the plan's ticket: a card in
the epic's tracker project, in the `Later` state and linked to the epic, its body the entry
verbatim and the note's words; the card's id goes into the note's content. It is a handle, not a
queue: it shows what the project still owes, nobody works from it, and the sweep before the
finish drains it. With no epic, the note on the plan is the one home.

## A delegated answer

When the operator delegates — "your call", "go with your recommendation", in the chat or in a
block's free words — with nothing offered, Pilot writes the chosen option with `by: agent` and the
operator's words as the note, so that the record shows who chose. After Pilot offered an answer in
the chat, its option and its note, any yes to it, those words included, is the person's ruling of
that option and no delegation, its note the one offered unless they give words of their own (the
operator, 2026-11-15: "Their ruling after an offer", to "A delegation only where nothing was
offered"). It is never restated as the operator's ruling: every
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
