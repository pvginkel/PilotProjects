# The grants

What Pilot and its workers do without asking, and what asks the operator first, act by act. The
project's switch, auto pilot, is the grant: on, the granted column goes ahead for the project's
life — the project its scope and its end the expiry, nothing finer; off, the granted column asks.
The kept column asks either way, and an act outside the table never asks. A session keeps the
switch it was briefed under when the switch moves meanwhile; the brief says which holds.

## The table

**Outside the table: never asked.**

- reads;
- diagnosis;
- sessions working the plan: a work item starts on add and never waits for a go;
- commits;
- the spec-repo push, a standing grant: whoever made the commits pushes them — the workflow, a
  worker or a job of Pilot's own — never asked and never held;
- waits.

**The granted column: asked while auto pilot is off, done under it.**

- a push that deploys;
- a push with riders: other commits than the session's own going out with it;
- a prd apply or a promotion;
- an operator action Pilot can run itself.

With auto pilot off, a push the granted column asks for is the operator's approval alone: on their
Yes an agent makes it — the worker that asked, or a work item of Pilot's — and nothing asks them to
push themselves (the operator, 2026-11-15: "Agreed", to "with auto pilot off, an agent pushes
after your approval instead of asking you to push").

**The kept column: always asked, auto pilot on or off.**

- an irreversible act: what no revert undoes — data deleted, a credential revoked, a resource
  destroyed;
- a product hold: an act the operator held back for the product's sake, such as a push before the
  changes they want first;
- a standing grant: a permission meant to outlast the project or reach past it;
- self-approval: going past a hold or a failed check on your own say;
- the rules themselves: a change to the record's conventions (the decision index's head), to the
  handbook's rules or to PilotProjects' rules — what says who decides, or how a decision is kept —
  whoever proposes it, a close-out's fix-now included (the operator, 2026-11-01).

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
can do this today already."). Its brief gives the exact command and says not to work around a
failure; what needs another environment checked, Pilot checks itself, since an Ansible
environment reads no other. For a secret, the brief names its OpenBao path and key,
`kv/eso/<stage>/<app>/<stage>/<leaf>`, and the agent mints the value and writes it on stdin,
`bao kv put -mount=kv <leaf> <key>=-`. The Ansible runbooks' "every OpenBao write is the
operator's keystroke" is their convention for a person at a terminal: for Pilot's work this
ruling stands.

## The confirmation reasons

An act that asks is a confirmation item, asked when the act is due, one covering everything due
at once; its `because` names why, by its code in `reference.json`'s `confirmation_reasons`:

- the granted column: `rider` for a push with riders, `auto-pilot-off` for any other act of it;
- the kept column: `irreversible`, `product-hold`, `standing-grant` for a standing grant,
  `self-approval`.

The code decides what the switch takes: turned on, it may answer Yes, as the person who turned it
on, every open confirmation whose code is the granted column's, and never one of the kept column's.

## In a worker's brief

A work item's brief carries the text below that the switch selects, copied verbatim, so that the
session knows what is pre-approved and acts on it.

Auto pilot on:

```text
Pre-approved for this session, done without asking: reads, diagnosis, commits, a push of the spec
repository, a push that deploys, a push that takes other commits with it, a prd apply or a
promotion, an operator action you can run yourself.
Not pre-approved, never done on your own say: an irreversible act, an act the operator held back
for the product's sake, a permission meant to outlast this work, going past a hold or a failed
check, a change to the rules that say who decides. Name each you need in what you register, and
Pilot asks the operator. A secret's value is never yours to handle: name the step, never the
value; placing one is work where a repository's tooling does it, Pilot's to start.
```

Auto pilot off:

```text
Pre-approved for this session, done without asking: reads, diagnosis, commits, a push of the spec
repository.
Not pre-approved, never done on your own say: a push that deploys, a push that takes other commits
with it, a prd apply or a promotion, an operator action, an irreversible act, an act the operator
held back for the product's sake, a permission meant to outlast this work, going past a hold or a
failed check, a change to the rules that say who decides. Name each you need in what you register,
and Pilot asks the operator. A push they approve is yours to make, never theirs. A secret's value
is never yours to handle: name the step, never the value; placing one is work where a repository's
tooling does it, Pilot's to start.
```
