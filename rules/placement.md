# Placement

Where a work item runs and on what: Pilot's judgment, guided by this file and the project's own
facts in its `handbook.md`, enforced nowhere. A work item names the repository its work belongs
to, `owner/Name`; the environment is Pilot's server's to make. The plan's `repo` is a label for the
project's header and binds no work item.

## The repository, by project key

A tracker project names an application, not one repository: the application and the repositories
it is developed with. Its repository is the project's name as the tracker lists it, owner
`pvginkel` — `DI (DockerImages)` is `pvginkel/DockerImages` — and a card's work runs there even
where the card's text names another repository of the application: the fix may land in any of
them. Where the key's own repository is not the answer:

- `DI`: `pvginkel/Ansible`.
- A deploy repository, `<App>Deploy`, lives with the application it deploys: work on it is placed
  in the application's repository, whose environments hold its checkout — `KubeCoderDeploy` in
  `pvginkel/KubeCoder`; where the names part, the application whose environment holds it —
  `FieldnotesDeploy` in `pvginkel/FieldnotesApp`. One with no application, such as
  `PrometheusDeploy`, is placed in `pvginkel/Ansible`: its upkeep is infrastructure maintenance.

## The repository, by the work's nature

The work belongs where it changes things, whatever card or project raised it: an Ansible slice in
`pvginkel/Ansible`; a change to ArgoCDTools in `pvginkel/Ansible`, its cards in `ANS`. What the
project's handbook says of its repositories comes before this file's rules.

## The model and the effort

`model` is `opus`, unless the work says otherwise — the handbook, the task or the stage. The
reasoning effort is left unset, the session's own default, unless the work names one.
