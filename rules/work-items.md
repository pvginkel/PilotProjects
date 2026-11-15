# A work item

What a work item is given when Pilot starts one, in the chat or in a job: the one home of its
`add_item` fields, its brief's shape and the close of one another replaces, which the skills that
start work cite.

## The fields

`add_item` with `kind` `work`, and:

- `title`, which its line on the timeline shows;
- `repo`, `owner/Name`, and `cwd`, its checkout under `/work` — the repository's own,
  `/work/<Name>`, or one its manifest checks out beside it — as `rules/placement.md` places it;
  the environment is Pilot's server's to make, one per work item;
- `model` and `reasoning_effort` as `rules/placement.md` says, `opus` and `xhigh`, Fable on a
  person's own word for that work alone;
- `step`, the plan's task it serves, where it serves one;
- `attachments`, what it needs from elsewhere;
- `brief`, below.

## The brief

Its first turn, your text, in this order:

1. The task in a line.
2. What to do and what to register: free-form work, which the session works out.
3. The grants text the switch selects — the brief's switch line — copied verbatim from
   `rules/grants.md`'s "In a worker's brief".
4. For a promotion to production, the text of `rules/promote.md`'s "In a promotion's brief",
   copied verbatim, step 2 naming the application, the commit to promote and what follows it.

What to do says one thing of how, whatever the work: the session hands its reading, its research
and whatever else stands apart to sub-agents, eagerly, each call naming the model and the effort
its job needs and never Fable, since a sub-agent called with no model runs on the session's own.

A stage of the workflow takes a brief of its own shape: its command and the slice's number as the
first line, then the task in a line, the ticket and the grants text, and nothing of what to do,
which its skill has (`rules/stages.md`).

Pilot appends the plan task it serves, the switch and the handbook: never paste the handbook.

## The answer

`state` says how the start went: `starting`, or `held` at the gate, with `held` saying why —
`paused`, held while the project is paused; `slot`, held until a slot is free;
`controller_unreachable`, held until Pilot reaches KubeCoder's controller again. A held start is a
line of its own, never told as running and never a reason to start less. A refused add — its
start refused, a field missing, a fault in its text — added nothing: fix the call, or say why it
was refused.

## A work item replaced

A work item another takes the place of — the same work started anew, on a brief a correction or a
ruling changed — is closed for good in the turn that adds the other: `stop_work` with `item` its
id and `reason`, a line saying what replaced it and why, which its done line carries. It is
stopped where it was not, one stopped earlier included, and done as cancelled, yours: it waits on
nobody and takes no Resume and no undo, its effect line "Closed · <title>". The documents its run
put to a person stay open and theirs, and answering them continues nothing. Without `reason`,
`stop_work` only stops, "Stopped · <title>": that is for work a person may resume, never for one
replaced, which would wait on them with a Resume that runs the outdated brief. One that failed is
refused, "it has failed, and keeps its Resume": it stays open, the person's.
