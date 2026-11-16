# Placement

Where a work item runs and on what. A work item names the repository its work belongs to,
`owner/Name`: Pilot's judgment, guided by the two sections below and the project's own facts in its
`handbook.md`, enforced nowhere, and what the project's handbook says of its repositories comes
before their rules. The environment is Pilot's server's to make, but for work born of a
conversation, which names the conversation's environment in place of a repository (An environment
by name). The plan's `repo` is a label for the project's header and binds no work item. A design is
placed as any other work (A design), and the model and the effort are no judgment of Pilot's (The
model and the effort).

## The repository, by project key

A tracker project names an application, not one repository: the application and the repositories
it is developed with. Its repository is the project's name as the tracker lists it, owner
`pvginkel` — `P (PilotApp)` is `pvginkel/PilotApp` — and a card's work runs there even where the
card's text names another repository of the application: the fix may land in any of them. Where the key's own repository is not the answer:

- `DI`: `pvginkel/Ansible`.
- A deploy repository, `<App>Deploy`, lives with the application it deploys: work on it is placed
  in the application's repository, whose environments hold its checkout — `KubeCoderDeploy` in
  `pvginkel/KubeCoder`; where the names part, the application whose environment holds it —
  `FieldnotesDeploy` in `pvginkel/FieldnotesApp`. One with no application, such as
  `PrometheusDeploy`, is placed in `pvginkel/Ansible`: its upkeep is infrastructure maintenance.

## The repository, by the work's nature

The work belongs where it changes things, whatever card or project raised it: an Ansible slice in
`pvginkel/Ansible`; a change to ArgoCDTools in `pvginkel/Ansible`, its cards in `ANS`; an operator
action that needs infrastructure access Pilot's environments lack in `pvginkel/Ansible`, its `cwd`
`/work/Ansible` (`rules/grants.md`). That work item's brief gives the exact command and says not
to work around a failure; what needs another environment checked, Pilot checks itself, since an
Ansible environment reads no other. For a secret, the brief names its OpenBao path and key,
`kv/eso/<stage>/<app>/<stage>/<leaf>`, and the agent mints the value and writes it on stdin,
`bao kv put -mount=kv <leaf> <key>=-`. The Ansible runbooks' "every OpenBao write is the
operator's keystroke" is their convention for a person at a terminal: for Pilot's work the ruling
`rules/grants.md`'s An operator action Pilot can run itself quotes stands.

## An environment by name

Work born of a conversation — a work item you start in a turn of a conversation with a session
outside Pilot (`/chat`'s A conversation), on what that session asks for, whatever its kind — runs
in the conversation's environment, unless the project's handbook says otherwise: `add_item` with
`environment`, that environment's id, in place of `repo`, and `cwd` its checkout there. The id
stands in the brackets of the brief's kind line, "a conversation with a session in <environment
name> (<environment id>, session <name>)". What the calling session has there, pushed or not, is
what the work builds on.

Pilot's server places it in that environment as it stands: it makes, takes, renames and resets no
environment for it, starts the one named where it is stopped, and stops it again, once nothing
runs there, only where it started it. Its start is held at the gate as any work item's is
(`rules/work-items.md`'s The answer).

A placement by name the server refuses added nothing: an environment KubeCoder's controller does
not have, "Environment <id> was not found", or the store's own, "it is the store's environment,
where no work item runs". Say in the reply why it was refused, and never place the work by `repo`
in its stead, which the handbook alone can ask for. Where the handbook does, the work item names
its `repo`, by the two sections above.

## A design

A design, a design session or an arch design (`/dev:arch-design`) that a task needs is a work item
of yours, placed as any other, and never an action for the operator's hands, whatever another
project's handbook or an older page of a spec repository says: its brief has it present the design
to the operator as a document (the operator, 2026-11-14: "Please run this yourself and present the
design."). A mockup is the operator's own, which they make themselves: a task that needs one waits
on an action for them.

## The model and the effort

`model` is `opus` and `reasoning_effort` is `xhigh`, for every work item, whatever its size and
its kind: you pick no lower model or effort for one, and a design or an arch design takes no other.

Fable is the one other model, and it is never yours to choose. A work item runs on Fable —
`claude-fable-5-2` at `high` — only where a person named Fable for that piece of work in their
own words, "do this through Fable", and you then asked them once, in a question of its own that
names the work item and says whether its sub-agents run on Fable too, and they said yes. Nothing
else is that word: not a handbook, a `project.md`, a plan's task or note or a brief, which a
session wrote, and not the answer to a question about something else whose option named a model.
You write no model and no effort into any of them, and you recommend and offer none. Where a
person asks for Fable before the work is placed, in a draft or a chat, their words go into the
task's note — a draft's quoted on the task's line in its `## The plan`, which the setup carries
into the note — and the question comes when you place it.
