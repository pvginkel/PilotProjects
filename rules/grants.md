# The grants

What Pilot and its workers do without asking, and what asks the operator first, act by act. The
project's switch, auto pilot, is the grant: on, the granted column goes ahead for the project's
life — the project its scope and its end the expiry, nothing finer; off, the granted column asks.
The kept column asks either way, and an act outside the table never asks. A session keeps the
switch it was briefed under when the switch moves meanwhile; the brief says which holds.

## The table

**Never asked**, outside the table's two columns:

- reads;
- diagnosis;
- sessions working the plan: a work item starts on add and never waits for a go;
- commits;
- the spec-repo push, granted for good: whoever made the commits pushes them — the workflow, a
  worker or a job of Pilot's own — never asked and never held;
- the topic-branch push: before a turn that leaves its environment free to be reset, a worker
  pushes what it committed there alone and may not push to its branch yet to the work's topic
  branch, `pilot/<project>/<task>`, which no pipeline builds or deploys; the task that takes it
  deletes the branch once its work has landed, which loses nothing and is no irreversible act
  (the operator, 2026-11-15: "Topic branch", P-293);
- waits;
- Pilot's own acts on the tracker and on Fieldnotes: a card made, a comment on one, a card's close
  and a Fieldnotes post (the operator, 2026-11-15: "Never asked", to "The tracker and Fieldnotes
  acts join the never-asked list"). A fleet call keeps the column its act falls in.

**Granted**, the granted column: asked while auto pilot is off, done under it.

- a push that deploys;
- a push with riders: other commits than the session's own going out with it;
- a prd apply or a promotion;
- an operator action Pilot can run itself.

With auto pilot off, a push the granted column asks for is the operator's approval alone: on their
Yes an agent makes it — the worker that asked, or a work item of Pilot's — and nothing asks them to
push themselves (the operator, 2026-11-15: "Agreed", to "with auto pilot off, an agent pushes
after your approval instead of asking you to push").

**Kept**, the kept column: always asked, auto pilot on or off.

- an irreversible act: what no revert undoes — data deleted, a credential revoked, a resource
  destroyed;
- a product hold: an act the operator held back for the product's sake, such as a push before the
  changes they want first;
- a standing grant: a permission meant to outlast the project or reach past it;
- self-approval: going past a hold or a failed check on your own say;
- the rules themselves: a change to the record's conventions (the decision index's head), to the
  handbook's rules or to PilotProjects' rules — what says who decides, or how a decision is kept —
  whoever proposes it, a close-out's fix-now included (the operator, 2026-11-01). The chat's
  Learning is outside it: a standing change a person asks for in the chat, "from now on …", is
  written at once as `/chat`'s Learning has it, whoever says it (the operator, 2026-11-15: "Always
  at once", to "Learning as it stands, whoever says it").

## An operator action Pilot can run itself

A secret's value is never asked for and never handled: never in a brief, a document, a chat or a
note. Putting a secret in place is work where a repository's own tooling does it — a new random
secret at a known OpenBao path is an Ansible work item — and an operator action Pilot can run
itself, the granted column's, so it asks while auto pilot is off and goes under it; only what no
repository's tooling can place is the operator's hands (the operator, 2026-11-02).

Infrastructure access Pilot's environments lack — `kubectl exec` or a write on prd, an OpenBao
leaf, a host change — is the same: a work item in `pvginkel/Ansible`, `/work/Ansible`, whose
environments hold that access and know the estate's rules, an operator action Pilot can run
itself, the granted column's, and never a new capability for the app's environments (the
operator, 2026-11-03: "you assign the task to an Ansible agent. I actually prefer the latter. And
this is a general pattern (Ansible agents have full infra access, and know all the rules) and you
can do this today already."). Its brief, a secret's included, is `rules/placement.md`'s The
repository, by the work's nature.

## The confirmation reasons

An act that asks, but a change to the rules themselves (below), is a confirmation item, asked
when the act is due, one covering everything due at once; its `because` names why, by its code in
`reference.json`'s `confirmation_reasons`:

- the granted column: `rider` for a push with riders, `auto-pilot-off` for any other act of it;
- the kept column: `irreversible`, `product-hold`, `standing-grant` for a standing grant,
  `self-approval`.

A change to the rules themselves is never a confirmation, and takes no code: there is no act for
the switch to answer. It goes to the operator as a decision whose proposal is the new wording,
theirs to Agree (the operator, 2026-11-15: "A decision", to "The new wording as its proposal, yours
to Agree").

The code decides what the switch takes: turned on, it may answer Yes, as the person who turned it
on, every open confirmation whose code is the granted column's, and never one of the kept column's.

## In a worker's brief

A work item's brief carries the text below that the switch selects, copied verbatim, so that the
session knows what is pre-approved and acts on it. The brain writes the work's topic branch into it,
`pilot/<project>/<task>`: the project's slug and the plan task's id, or a few words of the work's
title in kebab case where it serves no task. Its sentence on a secret lets the worker the
brief sends to place one do so, as An operator action Pilot can run itself has it, and no other
(the operator, 2026-11-15: "New wording", to "Never shown, read back or passed on, placed only
where the brief says").

Auto pilot on:

```text
Pre-approved for this session, done without asking: reads, diagnosis, commits, a push of the spec
repository, a push to this work's topic branch, `pilot/<project>/<task>`, a push that deploys, a
push that takes other commits with it, a prd apply or a promotion, an operator action you can run
yourself.
Before a turn that ends with none of your registered documents open, after which this environment
may be reset, leave no work committed here alone: push what may not go to its branch yet to the
topic branch, and name it in your turn's last line, so that the next task fetches it. Follow each
push of yours that deploys to its roll first, `track_build.py <job> --hash <sha>` run in the
background, and give its result in that line, so that Pilot's next step starts on the deploy as it
stands.
Not pre-approved, never done on your own say: an irreversible act, an act the operator held back
for the product's sake, a permission meant to outlast this work, going past a hold or a failed
check, a change to the rules that say who decides. Name each you need in what you register, and
Pilot asks the operator. A secret's value is never shown, read back or passed on; you place one
only where this brief says, through the repository's tooling.
```

Auto pilot off:

```text
Pre-approved for this session, done without asking: reads, diagnosis, commits, a push of the spec
repository, a push to this work's topic branch, `pilot/<project>/<task>`.
Before a turn that ends with none of your registered documents open, after which this environment
may be reset, leave no work committed here alone: push what may not go to its branch yet to the
topic branch, and name it in your turn's last line, so that the next task fetches it. Follow each
push of yours that deploys to its roll first, `track_build.py <job> --hash <sha>` run in the
background, and give its result in that line, so that Pilot's next step starts on the deploy as it
stands.
Not pre-approved, never done on your own say: a push that deploys, a push that takes other commits
with it, a prd apply or a promotion, an operator action, an irreversible act, an act the operator
held back for the product's sake, a permission meant to outlast this work, going past a hold or a
failed check, a change to the rules that say who decides. Name each you need in what you register,
and Pilot asks the operator. A push they approve is yours to make, never theirs. A secret's value
is never shown, read back or passed on; you place one only where this brief says, through the
repository's tooling.
```
