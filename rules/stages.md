# The workflow's stages

The workflow is AIWorkflow's `dev` plugin, installed in every environment. Two of its stages run
from Pilot, each a work item of its own: the planning of a slice, `/dev:plan-slice`, and its run,
`/dev:run-slice`. A slice is one change request to a repository onboarded to the workflow, one
whose root has a `.aiworkflowrc`: its record is a folder in the spec repository that file names,
and the stage's session works from the repository's checkout. Triage is no stage: what it does for
a slice is the definition chat's (`/create`), and the slice's folder is filed by a free-form work
item (Filing a slice). Every other work item is free-form, its brief your own text
(`rules/work-items.md`).

## The order

- A slice is filed, planned, then run: a task each, in that order, the next started once the one
  before is done.
- Planning is done when its work item's last line gives the plan's path and its phases. The run
  is done when its close-out is answered and carried out, or at once where it had nothing to ask,
  its last line saying so.
- One stage of a slice at a time: its loop holds the slice while it lives, and a second is
  refused. Two slices go at once, each in a work item and an environment of its own, unless one
  must follow the other: a slice is planned only once every slice its record `needs:` is done,
  which the stage's preflight holds to.
- A stage waits on its loop inside its turn, and a turn lasts as long as the loop, hours for a
  run. A long turn is not a stalled one: its line says where the loop stands.

## Filing a slice

The first work of a slice: a free-form work item in the slice's repository, its brief as
`rules/work-items.md` has it, the task "File slice <title> in <the spec repository>", and what to
do:

1. File it as `/dev:triage` files a run born of a conversation that already decided, its steps 6
   to 8, with no message to put: the folder and its slice.md, the slice card parented to the
   brief's ticket, the cards the slice absorbs closed, the README's Pending line, the commit and
   the spec repository's push. Notify nobody, register nothing, and end the turn with one line
   naming the slice's folder and its card.
2. The conversation it files from, verbatim: the opening's words and `project.md` as the setup
   read it, the answers in its blocks included, and which of its asks this slice takes where the
   plan has more than one slice; for a slice asked later in the project's chat, the person's
   messages that asked it, the cards they named as youtrack reads them and the answers to its
   asks. The words travel as they stand, since the slice's record quotes them.
3. `Ticket: <id>` on a line of its own, the plan's ticket, where the plan has one.

Its last line gives the slice's number, which the planning's brief opens with.

## The brief

A stage's brief has a shape of its own:

1. `/dev:plan-slice <NNN>` or `/dev:run-slice <NNN>`, the slice's number, as its first line, so
   that the skill loads with the rest as its arguments.
2. The task in a line, then `Ticket: <id>` on a line of its own, the plan's ticket: every card
   the stage files is parented to it. A plan with no ticket gives none, and the stage files its
   cards without a parent and says so.
3. The grants text the switch selects, as `rules/work-items.md` has it.

Nothing else of yours: no instructions, no context, no list of what to register. The stage's
skill has them, and the slice's folder holds the rest. The work item's `repo` is the slice's
repository, its `cwd` that repository's checkout, `/work/<Name>`, and its `step` the slice's
task, which every document it registers carries.

## What a stage registers

Every ask of a stage is a document it registers in its turn, which then ends. Its continuation,
once every document the turn registered is closed, is Pilot's server's: a work item titled as the
stage's. `/pre-rule` passes over each document as over any worker's, by `rules/routing.md`:

- **A preflight failure**, either stage's: an `action`, its heading the fix, its `check` that
  preflight passes. It is an environment's fact, a dirty tree or a missing clone, of which the
  stage fixes nothing; its Done runs the step that raised it again.
- **The requirements**, planning's first document, its title ending `: requirements`: the slice's
  product choices, each a `decision` with its recommendation, the slice's record and its grounding
  attached. Routed as any choice outside the grants table (D103): ruled where you can rule it
  safely, the operator's words of 2026-10-31 — "If it can rule safely, let it." — and left to them
  where it is theirs, as routing's last row has it.
- **The plan loop's questions and its review's findings**, planning's, the plan and the review
  attached: routed the same way. The writer's fix pass applies the answers, and no review follows
  it.
- **A bail's decision**, either stage's: retry, change the plan or stop here, as the diagnosis
  leaves them live, with its recommendation. Stop here leaves the stage stopped where it stood,
  and a later work item of the same command takes it up.
- **The run's pushes**, the run's first document while the switch is off and a push of its
  repositories deploys: one `decision`, whose Agree lets the run push as it goes. It is the granted
  column's, the operator's while auto pilot is off. Any other answer holds the pushes, and the
  close-out carries each held push as an action.
- **The run's question**, mid-run: a block the run waits on, the plan attached, routed as any
  block.
- **The close-out**, the run's last document: what the run hands over beyond its scope, a section
  each. An `action` is one only a person's hands do, a `decision` a product choice, and every
  other finding a `decision` whose proposal is its fate (below). The run's record, the plan and
  its verification are attached. A run with nothing to ask registers none and is done.

## A fate in a stage's document

A finding's proposal names its fate: `Agree` takes it, and your own words name another. The
stage's continuation carries each out, never you: you make no card and fold nothing, or it is done
twice.

- **card**, in the project the proposal names, else the slice's own: one card per finding,
  parented to the brief's ticket, its text the section as the document showed it.
- **fold into <NNN>**: the finding added as an ask to that slice's record, a slice not yet
  planned; one planned or running refuses it.
- **fix now**: made by the continuation where the repository's own `CLAUDE.md` classes the change
  as ad hoc work; where it does not, the stage puts the alternatives in a new document.
- **close**: nothing done; the note is the reason, kept in the record.
- **deferred**, your deferral with its `to`, as routing's Deferral has it: final for the stage,
  which closes the finding as Pilot's and keeps nothing to bring it back. The plan note is its one
  way back.

## How the stage reads your answers

- An answer `by: agent` is marked as chosen by Pilot on everything it produces, the note its
  reason. The operator's words travel verbatim.
- A ruling the stage cannot carry out as given, such as a fold into a running slice or a fix now
  no rule allows, comes back as a new document, its alternatives a decision.
- A question to the writer, through `ask_writer`, reaches the stage's own conversation: a
  sub-agent answers it from the slice's folder, and the reply shows beside its block.

## The stage's, not yours

- The slice card's moves: planned at planning's end, in progress at the run's start, delivered
  once merged, and done once the close-out's answers are carried out.
- The slice's folder and the spec repository: the stage commits and pushes them.
- The halt: Pilot's halt file stops a stage's loop at its next safe point, and the nudge after it
  carries the stage on.
