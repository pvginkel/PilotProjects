---
name: plan
description: Pilot's upkeep of a project's plan and its work — the setup from the draft, what is next after a worker's turn or an item of Pilot's done, a wait's firings, placement, the confirmations, the sweep and the finish decision. Run it when Pilot's brief opens with /plan, or when /pre-rule hands on to it.
---

# Plan

The plan's upkeep and the work: the setup from the draft, what is next, an item of Pilot's done, a
wait's firings, the sweep before the finish and the finish decision, in the mode the brief names.

1. Read `handbook.md` before anything the brief asks; at the setup it is empty.
2. Read the brief, below: its kind line, `Pilot's brief · <the kind> · …`, names the mode —
   the setup's is `Pilot's brief · the setup · …` (The setup) — and its switch line the grants
   that hold for this session.
3. Do the mode's work, then end your turn with one line saying what it did. A job never waits
   and never asks in its own transcript: a question to a person is an item.

The rules it applies: `rules/grants.md`, `rules/placement.md`, `rules/routing.md`,
`rules/stages.md`. The writing — an item, a note — is `/dev:document-format`'s.

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
   the draft — what will be demonstrated and the evidence that will show it; then the draft's
   `## Rules` and `## Context`, copied. The check in the tool's result says the write landed.
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

## A work item

`add_item` with `kind` `work`; `title`, which its line on the timeline shows; `repo`
(`owner/Name`), `cwd`, `model` and `reasoning_effort` as `rules/placement.md` places it; `step`,
the task's id; and `brief`: the task in a line, what to do and what to register
(`rules/stages.md`), then the grants text the switch selects, verbatim, from `rules/grants.md`'s
"In a worker's brief". Pilot appends the plan task, the switch and the handbook: never paste the
handbook. The answer says how the start went, `state` `starting`, or `held` at the gate with
`held` saying why; a held start is a line of its own, never a reason to start less. A refused
add — its start refused, a field missing, a fault in its text — added nothing: fix the call, or
say so in the turn's last line, with its reason.

## The server's follow-up turn

A turn of Pilot's server that names a save of yours still held — "Your save of `<path>` is held:
`<path>:<line>: <message>`. Fix it and end your turn." — is no person's: fix the file until its
check is clean and end the turn. The job is done when that turn ends.

## The brief

$ARGUMENTS
