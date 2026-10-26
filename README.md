# PilotProjects

Pilot's store environment: the brain's scripts and skills, and no data — Pilot's record lives in
its database. The app is `pvginkel/PilotApp`.

## What it holds

- `CLAUDE.md`: the brain's map, what holds in every session Pilot runs here — who it is, where its
  project's files are, its tools and `pilot.py`'s verbs, the invariants, and how it writes.
- `.claude/skills/<name>/SKILL.md`: the four skills a brief opens with, `create`, `chat`,
  `pre-rule` and `plan`, each so far a frame: its frontmatter, its first step, the rule files it
  applies, and the brief's slot, `## The brief`, last.
- `rules/`: the rules the skills apply, each file the one home of its own — `grants.md` (what goes
  ahead and what asks the operator first), `routing.md` (where an open block goes),
  `placement.md` (a work item's repository, model and effort) and `stages.md` (the workflow's
  stages from Pilot).
- `.kubecoder/config.yaml`: the environment, with the `pilot-sync` service, which keeps
  `/work/Projects` in step with the record, and the catalog's `python` toolchain.
- `.claude/settings.json` and `.claude/hooks/pilot-sync-check.py`: the hook that asks `pilot-sync`
  what the record made of each `Edit` and `Write` under `/work/Projects/`.
- `tools/pilot.py`: the brain's editing scripts over one project's folder, each write checked by
  `pilot-sync` after it. `pilot.py --help` prints every verb's usage.
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
- `kc project test`: every test under `tests/`: `pilot.py`'s and the hook's, against invented
  project folders (`tests/fixtures/tree/`) and a stand-in for `pilot-sync`'s local check, and the
  map's (`tests/test_map.py`), which holds `CLAUDE.md`, the rule files and the skills to their
  shape: the skills named as their folders with the brief last, the format skill cited by its name,
  the paths they cite there, `CLAUDE.md`'s verb lines equal to `pilot.py`'s own, and the grants
  naming the confirmation reasons of the fixtures' `reference.json`.
