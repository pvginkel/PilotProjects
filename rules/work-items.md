# A work item

What a work item is given when Pilot starts one, in the chat or in a job: the one home of its
`add_item` fields and its brief's shape, which the skills that start work cite.

## The fields

`add_item` with `kind` `work`, and:

- `title`, which its line on the timeline shows;
- `repo`, `owner/Name`, and `cwd`, its checkout under `/work` — the repository's own,
  `/work/<Name>`, or one its manifest checks out beside it — as `rules/placement.md` places it;
  the environment is Pilot's server's to make, one per work item;
- `model` as `rules/placement.md` says, `opus` unless the work says otherwise, and
  `reasoning_effort` only where the work names one;
- `step`, the plan's task it serves, where it serves one;
- `attachments`, what it needs from elsewhere;
- `brief`, below.

## The brief

Its first turn, your text, in this order:

1. The task in a line.
2. What to do and what to register: free-form work, which the session works out, and never a
   stage's command (`rules/stages.md`).
3. The grants text the switch selects — the brief's switch line — copied verbatim from
   `rules/grants.md`'s "In a worker's brief".

Pilot appends the plan task it serves, the switch and the handbook: never paste the handbook.

## The answer

`state` says how the start went: `starting`, or `held` at the gate, with `held` saying why —
`paused`, held while the project is paused; `slot`, held until a slot is free;
`controller_unreachable`, held until Pilot reaches KubeCoder's controller again. A held start is a
line of its own, never told as running and never a reason to start less. A refused add — its
start refused, a field missing, a fault in its text — added nothing: fix the call, or say why it
was refused.
