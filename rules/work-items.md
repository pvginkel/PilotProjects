# A work item

What a work item is given when Pilot starts one, in the chat or in a job: the one home of its
`add_item` fields, its brief's shape, the close of its own card and its close for good, replaced
or dropped, which the skills that start work cite.

## The fields

`add_item` with `kind` `work`, and:

- `title`, which its line on the timeline shows;
- `repo`, `owner/Name`, as `rules/placement.md` places it, and `cwd`, its checkout under `/work`
  — the repository's own, `/work/<Name>`, or one its manifest checks out beside it: the
  environment is Pilot's server's to make, one per work item, and never `environment`, an
  environment's id, work born of a conversation included (`rules/placement.md`'s Work born of a
  conversation);
- `model` and `reasoning_effort` as `rules/placement.md` says, `opus` and `xhigh`, Fable on a
  person's own word for that work alone;
- `step`, the plan's task it serves, where it serves one;
- `claims`, the open actions it does that Pilot claims for it, and `researches`, the blocks Pilot
  left open on a fact it finds, as `rules/routing.md`'s The claim and Due diligence have them;
- `attachments`, what it needs from elsewhere;
- `brief`, below.

## The brief

Its first turn, your text, in this order:

1. The task in a line.
2. What to do and what to register: free-form work, which the session works out.
3. For a promotion to production, the text of `rules/promote.md`'s "In a promotion's brief",
   copied verbatim, step 2 naming the application, its commit, the application's alone, never the
   deploy repository's, which the promotion takes from the build, and what follows it.

What to do says one thing of how, whatever the work: the session hands its reading, its research
and whatever else stands apart to sub-agents, eagerly, each call naming the model and the effort
its job needs and never Fable, since a sub-agent called with no model runs on the session's own.

A task whose input is work an earlier task left on its topic branch, which that task's turn's last
line names, has its brief name the branch, `pilot/<project>/<task>` of the earlier task, to fetch,
and to delete once the work has landed on the branch it was meant for (`rules/grants.md`'s
never-asked list).

A stage of the workflow takes a brief of its own shape: its command and the slice's number as the
first line, then the task in a line and the ticket, and nothing of what to do, which its skill has
(`rules/stages.md`).

Pilot's server appends the rest to every work item's brief, a stage's and a promotion's included:
the plan task it serves, the switch with the grants text it selects, read from `rules/grants.md`'s
In a worker's brief, the work's topic branch written into it, and the handbook. The brief you write
is the work's own part alone: never copy the grants text or write the work's topic branch into it,
and never paste the handbook.

What a brief says by its work's kind has its home beside that kind's rules:

- a design, a design session or an arch design: `rules/placement.md`'s A design;
- an operator action that needs infrastructure access, a secret's included: `rules/placement.md`'s
  The repository, by the work's nature;
- a research: `rules/routing.md`'s Due diligence, step 4;
- a promotion: item 3 above, `rules/promote.md`;
- a slice's filing: `rules/stages.md`'s Filing a slice.

## The answer

`state` says how the start went: `starting`, or `held` at the gate, with `held` saying why —
`paused`, held while the project is paused; `slot`, held until a slot is free;
`controller_unreachable`, held until Pilot reaches KubeCoder's controller again. A held start is a
line of its own, never told as running and never a reason to start less. A refused add — its
start refused, a field missing, a fault in its text — added nothing: fix the call, or say why it
was refused.

## Its own card

A free-form work item's own card, the card it was started to work, is closed by the job after the
work item's last turn, once the card's done-when is met and no document of its run is open: Done,
through youtrack, with a comment saying what the work did and how the done-when was met. A stage's
cards are the workflow's own (`rules/stages.md`).

## A work item closed for good

A work item is closed for good, never left stopped, in two cases:

- **Replaced**: another takes its place — the same work started anew, on a brief a correction or
  a ruling changed — and it is closed in the turn that adds the other, its `reason` a line saying
  what replaced it and why.
- **Dropped**: a person drops it in the chat, its work no longer wanted with nothing in its place
  — "drop that, we no longer need it" — and it is closed for good on their word: `stop_work` with
  `reason` their words, never left stopped for them to close. Only on their word that it is
  dropped for good: a stop they may resume takes no `reason`.

Either is `stop_work` with `item` its id and `reason`, which its done line carries. It is stopped
where it was not, one stopped earlier included, and done as cancelled: it waits on nobody and
takes no Resume and no undo, its effect line "Closed · <title>"; one replaced is yours. The
documents its run put to a person stay open and theirs, and answering them continues nothing.
Without `reason`, `stop_work` only stops, "Stopped · <title>": that is for work a person may
resume, never for one replaced, which would wait on them with a Resume that runs the outdated
brief, or for one dropped, left for them to close. One that failed is refused, "it has failed, and
keeps its Resume": it stays open, the person's.
