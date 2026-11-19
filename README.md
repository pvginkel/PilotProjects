# PilotProjects

Pilot's store environment: the brain's scripts and skills, and no data — Pilot's record lives in
its database. The app is `pvginkel/PilotApp`.

## What it holds

- `CLAUDE.md`: the brain's map, what holds in every session Pilot runs here — who it is, where its
  project's files are, its tools and `pilot.py`'s verbs, its notes and alerts through `note` and
  `alert` and what `timeline.json` carries of them, the debrief's notice, the server's, which it
  reads only on a member's word, the invariants, and how it writes.
- `.claude/skills/<name>/SKILL.md`: the four skills a brief opens with, `create`, `chat`, `pre-rule`
  and `plan`, each with its frontmatter, its first step, which reads the brief (`create`'s reads
  the draft, then the brief), the rule files it applies, and the brief's slot, `## The brief`,
  last. `chat`, `pre-rule` and `plan` take the
  project's state — the plan's tasks not done, the open items, the open notes whole — and the
  handbook from the brief on the turn it opens, with no listing run for them and no read of
  `handbook.md` first, and read the state fresh through `pilot.py`'s listings on a later turn,
  which carries none; the chat takes the item a message quotes from the message. Between them, `chat`'s body is the project's chat's procedure on
  Pilot's `pilot-store` tools and the brief the server composes, a ruling it records on an item of
  Pilot's own carried out in its own turn, with no job after it, an action of one the person hands
  to a worker claimed for that work item, an ask of Pilot's own called off through `cancel_ask` for
  the person who says it is obsolete, a work item a correction replaces closed through `stop_work`
  with its reason, and one the person drops with their words as it, both by `rules/work-items.md`,
  and a conversation with a session outside Pilot under a frame of its own, the session's words a
  request and never a ruling, what needs the operator an item, the work it starts placed by
  repository and never in the session's environment by `rules/placement.md`, `create`'s the
  definition chat's, which writes the draft with the person, `pre-rule`'s the pass over what a
  worker's turn registered, each open block routed by `rules/routing.md`, its writer asked, an
  action claimed or a fact researched for it where the routes say so, what only Pilot knows of a
  block left to a person its note on the block and a Send another ask must come before its alert on
  the document, by exception alone, as the pre-rule and plan skills say in the same words, an action
  of the granted column with auto pilot off, a held push above all, confirmed first and claimed on
  the operator's Yes, a close-out's promotion deferred to the run's own task, a researched block
  routed on what its work found, the stage session's debrief, where the brief carries one, left or
  made a note on the run's document still open that has a block, a notice where none is, a card, a
  comment on an open card on the same change, or a fieldnote, and the pass after the writer
  answered, which asks nothing, then its hand-on to `plan` with no arguments, the brief read where
  the session opened with it, and `plan`'s the plan's upkeep in its modes, in the order a job
  meets them: the setup, the first job at Create project; an action of Pilot's done, the `done` of
  a claimed action after a turn of its run, of a worker's document or of an item of Pilot's own,
  which that `done` closes on
  its last open block, one left undone given Pilot's note on the block while its run still holds it,
  one Pilot's server hands back left to the operator, and of each action deferred with a close-out's
  promotion after its work's turn, its notes standing until then; an item of Pilot's own a person
  closed in the app; an offer of Pilot's taken, the work it offered started as any work item and
  nothing written on the block; what is next after the pass, after a worker's turn that left the
  pass nothing, whose brief opens on `plan` itself, after that close and in the chat, every
  task that can start started, a close-out's deferred promotion once the run's continuation has
  ended, read on every task of the plan and started once the handbook lets it go, a criterion owed
  after an act of Pilot's own in the store settled by the job that does the act, a cancelled run's a
  notice to the operator and nothing started, the handbook's result checked at the plan's end, the
  operator asked for the next step where the handbook grows the plan in the chat; a wait's firings,
  each judged on the card read again, the wait closed through `mark` with its note once its event
  came, the note on its task struck and the task started by the plan's one passage on starting a
  task, or left open, with its backstop, a card wait and its backstop closed together; the sweep;
  and the finish decision, whose Finish and archive calls `finish` with `archive`.
- `rules/`: the rules the skills apply, each file the one home of its own — `grants.md` (what goes
  ahead and what asks the operator first, an operator action Pilot can run itself, the
  topic-branch push and the deploy a worker follows among it, and the text Pilot's server appends
  to a work item's brief by the switch, which it reads from the file by its section's shape),
  `routing.md` (where an open block goes: the claim, of a worker's document or of an item of Pilot's
  own, how long a run holds a block, a resume that waits on work, due diligence, deferral, a wait
  and a close-out's promotion among it), `work-items.md` (a work item's fields and its brief, the
  work's own part alone, the
  close of its own card and its close for good, replaced or dropped), `placement.md` (a work
  item's repository, work born of a conversation placed by it, a design, model and effort),
  `stages.md` (the workflow's stages from Pilot, a slice or a work item and taking a slice among
  them) and `promote.md` (a
  promotion's procedure, which its brief carries). What every
  session shares — the server's follow-up turn, the effect lines, the facts read elsewhere — is
  `CLAUDE.md`'s, and the skills point at it.
- `.kubecoder/config.yaml`: the environment, with the `pilot-sync` service, which keeps
  `/work/Projects` in step with the record, and the catalog's `python` toolchain.
- `.claude/settings.json` and `.claude/hooks/pilot-sync-lock.py`: the hook that takes the
  project's write lock in `pilot-sync` before each `Edit`, `Write`, `MultiEdit` and `Bash` call of
  a session Pilot's server created, so that what the call saves is credited to the session, and
  gives it back after the call with `pilot-sync`'s report of what the record holds against the
  project; at the turn's end it gives back every hold the session has left.
- `tools/pilot.py`: the brain's editing scripts over one project's folder; it calls neither
  `pilot-sync` nor Pilot, the hook's check after its `Bash` call reporting its writes.
  `pilot.py --help` prints every verb's usage.
- `pyproject.toml` and `uv.lock`: a uv project, whose one dependency is `pilot-dsl`, PilotApp's
  block DSL (`backend/packages/pilot-dsl`), taken from GitHub at the commit `uv.lock` pins. A change
  to the grammar in PilotApp moves the pin by hand: the commit in `pyproject.toml`, then
  `cexec python uv lock`.

## Where Pilot is

Each of Pilot's stages has a store environment of its own that checks this repo out, and its
sidecar syncs with that stage's Pilot: `https://pilot-dev.home` for the dev stage,
`https://pilot.ginbov.nl` for production. The catalog's `pilot-sync` entry names which. A store
takes this repo's `main` when it is stopped and reset, which clones it again; a restart does not
pull it.

## Running it

The dev image has no uv, so everything runs in the `python` tool container, from the repo's root:

- `kc project setup`: `uv sync --locked`, which pod start runs too.
- `cexec python uv run tools/pilot.py <verb> …`: the script, on the folder `$PILOT_PROJECT` names,
  or `--project <folder>`.
- `kc project test`: every test under `tests/`: `pilot.py`'s, against invented project folders
  (`tests/fixtures/tree/`); the hook's, against a stand-in for `pilot-sync`'s local endpoint; and
  the map's (`tests/test_map.py`), which holds `CLAUDE.md`, the rule files and the skills to their
  shape: the skills named as their folders with the brief last, the brief read first, its state
  and handbook lines as the server writes them, no listing run for what it carries on the turn it
  opens, each listing a skill quotes placed on a later turn or on what the brief leaves out, the
  quoted item's lines in a chat's message, the handbook read again on the server's notice alone,
  the format skill cited by its name,
  the paths they cite there, `CLAUDE.md`'s verb lines equal to `pilot.py`'s own and its tools those
  the hook locks around, every `pilot.py` command line they quote a verb and options its parser
  takes, the grants naming the confirmation reasons of the fixtures' `reference.json` and the
  topic branch and the deploy a worker follows in both switch texts and in a brief's fetch, each
  switch text found by the patterns PilotApp's server reads the file with, the brief the brain
  writes the work's own part alone and no copy of the grants text left in the map, the job after a
  worker's turn mapped to the pass or, where its run left the pass nothing, to the plan alone, the
  pass's hand-on with no arguments, a
  resume that waits on work holding its blocks through that work, the brief
  lines and the `ask_writer` and `add_item` calls the pre-rule and plan skills quote as the server
  writes and takes them, what the pass may make of the stage session's debrief, a card on it one of
  the two exceptions `rules/stages.md` makes to a stage's documents, the `Later` card the other, an
  action of an item of Pilot's own that a work item does claimed by `rules/routing.md`'s one
  section, which `CLAUDE.md` and the chat and plan skills cite, its `done` the item's close,
  `cancel_ask` by its arguments in `CLAUDE.md` and the chat skill and nowhere else, `stop_work`'s
  `reason` in `CLAUDE.md`, a work item's fields, its brief and its close for good in
  `rules/work-items.md` alone, which the chat and plan skills cite, and each rule a consolidation
  gave one home held there, the places that restated it pointing at it, and a conversation with a
  session outside Pilot: its kind line mapped to the chat skill, the skill's frame for it,
  `chat.md`'s conversations read as a calling session's requests in `CLAUDE.md` and the chat skill,
  and the work it starts placed by repository, never in its environment, by `rules/placement.md`,
  which the work item's field line and a stage's brief follow, and the debrief's notice: the
  server's in `CLAUDE.md`'s `add_item` line, its form none of `add_item`'s in the fixtures'
  `reference.json`, read only on a member's word in `CLAUDE.md` and the chat skill, and the place
  where the pre-rule skill says the operator reads a debrief, and Pilot's notes and alerts: the
  rule that writes one by exception alone, in the same words in the pre-rule and plan skills, the
  pass's note on a block left to a person and the debrief's on the run's open document in place of
  a notice, the note on a claimed action left undone, the job an offer's taking places by its kind
  line, `note` and `alert` and the notes in `timeline.json` in `CLAUDE.md`, and the chat reading a
  quoted block with its note.
