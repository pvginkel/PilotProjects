# PilotProjects

Pilot's store environment: the brain's scripts and skills, and no data — Pilot's record lives in
its database. The app is `pvginkel/PilotApp`.

## What it holds

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

## Running it

The dev image has no uv, so everything runs in the `python` tool container, from the repo's root:

- `kc project setup`: `uv sync --locked`, which pod start runs too.
- `cexec python uv run tools/pilot.py <verb> …`: the script, on the folder `$PILOT_PROJECT` names,
  or `--project <folder>`.
- `kc project test`: every test under `tests/`, `pilot.py`'s and the hook's, against invented
  project folders (`tests/fixtures/tree/`) and a stand-in for `pilot-sync`'s local check.
