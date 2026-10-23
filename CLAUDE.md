# PilotProjects

This is the repo of **Pilot's store environment**. Pilot is the project manager that owns
multi-step work across the KubeCoder fleet; its application is `pvginkel/PilotApp`. Pilot's
brain, a headless Claude Code session, runs here, in this repo's directory.

## No data here

The store holds no data. Pilot's record, in Pilot's database, is the one truth about every
project. `/work/Projects` is a projection of that record: a folder per syncing project (its
slug, or `draft-<number>` for a draft) and `reference.json`. The `pilot-sync` sidecar keeps it in
step both ways: it writes what the record renders, and sends an edited file back to Pilot as a
save, which the record takes, reverts or holds. A file the record never made is a stray, never
synced. What `/work/Projects` holds is the record's, and this repo carries none of it.

After every `Edit` and `Write` of a file under `/work/Projects/`, the hook in
`.claude/settings.json` asks the sidecar what the record made of it; what Pilot has to say
comes back with the tool's result.

## Where Pilot is

Each of Pilot's stages has a store environment of its own that checks this repo out, and its
sidecar syncs with that stage's Pilot: `https://pilot-dev.home` for the dev stage,
`https://pilot.ginbov.nl` for production. The catalog's `pilot-sync` entry names which.

## This repo

- `.kubecoder/config.yaml`: the environment, with the `pilot-sync` service.
- `.claude/settings.json` and `.claude/hooks/pilot-sync-check.py`: the hook.
- `tests/`: the hook's test, run by `kc project test`.
