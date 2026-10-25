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

**The kept column: always asked, auto pilot on or off.**

- an irreversible act: what no revert undoes — data deleted, a credential revoked, a resource
  destroyed;
- a product hold: an act the operator held back for the product's sake, such as a push before the
  changes they want first;
- a standing grant: a permission meant to outlast the project or reach past it;
- self-approval: going past a hold or a failed check on your own say.

A secret is never asked for and never handled: it is an action, the operator's hands.

## The confirmation reasons

An act that asks is a confirmation item, asked when the act is due, one covering everything due
at once; its `because` names why, by its code in `reference.json`'s `confirmation_reasons`:

- the granted column: `rider` for a push with riders, `auto-pilot-off` for any other act of it;
- the kept column: `irreversible`, `product-hold`, `self-approval`.

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
check. Name each you need in what you register, and Pilot asks the operator. A secret is always
the operator's hands: name the step, never handle the secret.
```

Auto pilot off:

```text
Pre-approved for this session, done without asking: reads, diagnosis, commits, a push of the spec
repository.
Not pre-approved, never done on your own say: a push that deploys, a push that takes other commits
with it, a prd apply or a promotion, an operator action, an irreversible act, an act the operator
held back for the product's sake, a permission meant to outlast this work, going past a hold or a
failed check. Name each you need in what you register, and Pilot asks the operator. A secret is
always the operator's hands: name the step, never handle the secret.
```
