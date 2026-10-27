---
name: create
description: Pilot's definition chat on a draft project — the conversation that writes the draft, project.md, with the person who started it, until the operator creates the project. Run it when Pilot's brief opens with /create.
---

# Create

The definition chat: what the project is for, what result establishes it and who works on it,
agreed with the person who started it and written into the draft, `project.md`, until the
operator creates the project. A draft has no handbook, no plan and no items: the chat writes the
draft, records the answers given in the chat to its asks and attaches the material it needs.

1. Read `project.md`, the draft, and what the brief says was attached to it — `timeline.json`'s
   `attachments` lists each file. The draft is empty from the plus; one that is not was written by
   an earlier definition chat, the draft archived and brought back, and `chat.md` holds that chat.
2. Read the brief, below: who started the draft and whether they are a member, the attachments
   so far, and the message. It has no switch, no notes and no handbook: a draft has none, and
   its grants start at Create project.
3. Read what the message points at (Reading), then answer it: write what it settles into the
   draft (The draft), record the answers it gives (Recording), attach what it points at
   (Attaching), and reply with what the person needs to decide or do next (The reply).
4. End your turn. Each later message is a turn of its own, answered from step 3: the person's
   words verbatim, after the line "The message, from <handle> (member|not a member):" when the
   chat's message before was another person's. A message without that line is from the person the
   latest such line named, the brief's included, and with none so far from the person who
   started the draft.

The rules it applies: `rules/routing.md`. The writing — the draft, its front matter and its
blocks — is `/dev:document-format`'s.

## Reading

- **A quote** travels inside the words as a tag, the closing tag repeating the attribute, the
  title as it stood between the tags, a reading aid: an ask of the draft is
  `<quoted_block id="project.md/<local id>">…</quoted_block id="project.md/<local id>">`, the
  block of that local id in `project.md`; a file is
  `<quoted_path path="<path>">…</quoted_path path="<path>">`, `project.md` or
  `attachments/<batch>/<filename>`, read from the draft's folder. A tag naming any other path is
  no quote.
- **`chat.md`** holds the draft's earlier definition chat, if any: read it when the message
  refers back to what that chat settled and the draft does not hold.

## The draft

- **The one place the agreement lives**: what the chat decides goes into `project.md`, not
  retold in the chat. Write and rewrite it freely as the chat goes, the whole of it, not section
  by section: plain Markdown, the lead first.
- **What the chat reaches**, a question at a time where the person has not said it: what the
  project is for; the result that establishes it, its material constraints and the evidence that
  will show it; the repositories it touches; who works on it, each of whom joins the project
  from its menu, "Join the project". Then the sections the setup reads at Create:
  - `## The plan`: the tasks as the chat agrees them, in their order, each with what it waits on
    where it waits; the repository it works in and the ticket the work is tracked on, where the
    project has them; what the setup starts — work in a repository, an action for someone's
    hands, or nothing yet — agreed here, which nothing in the app fixes.
  - `## Rules`: the rules the chat agrees on for the project — how its work goes, what is asked
    first, what is never done. The handbook is not the draft's: the setup copies this section
    into `handbook.md`.
  - `## Context`: what a session working the project needs to know — its repositories, its
    environments, its people, where its material is. The setup copies it into `handbook.md` too.
- **The front matter**: `title`, the project's name in the list and the head; `slug`, the
  project's folder once it is created — Pilot's choice, as the format skill has it. Give both
  once the project has a name. The check after the save reports a slug that is no valid one, and
  Create project stays disabled until it is.
- **An ask** — a closed question the person answers — is a block in the draft, never a question
  in the chat. In the draft, and only there, a block may be changed or deleted as the project
  moves, answered or not, a deleted block taking its answers with it; a person's answer lines
  stay the record's, a save that changes them getting them back.
- **A link** goes to attached material alone, `[words](attachments/<batch>/<filename>)`,
  relative to the draft's folder, its path as `timeline.json`'s `attachments` lists it, which the
  Draft tab opens in the overlay. A ticket id, a repository, an environment or any other link is
  drawn as plain words: write it as words.
- **The check** after every save says what the record made of it, in the tool's result: clean,
  or the faults of a save it holds until you fix them. Fix a held save in the same turn.

## Recording

- **An answer the person gives in the chat** to an ask of the draft, quoting it or not, is
  theirs, recorded on their behalf rather than left open in the Draft tab: `answer` with
  `block` `project.md/<local id>`, the id a quoted ask's tag carries; `value` (an option's
  label, `Agree`, `Yes`, `No`, or their own words); `for` their handle, as step 4 names them; and
  `note` their words as they gave them. Answering it again replaces it; it has no undo.
- **A delegation** — "your call", "go with your recommendation" — is no answer of theirs: the
  option you choose is yours, `by: agent`, their words the note,
  `pilot.py answer <file> <block id> --value <option> --note <their words>` on `project.md`.
  Cite it as `rules/routing.md`'s "A delegated answer" says, never as their ruling.
- **No deferral**: the draft has no plan, and no plan note names a block of it. An ask the
  person leaves for later stays open.
- Each call answers its effect line — "Answered · D1 · <title>" — which the chat shows where
  the call ran; a refused call changes nothing and answers why. Say a thing is recorded only once
  its call answered so.

## Attaching

- **Material the person points at** — a design record, a handover, a file in an environment of
  the fleet — is copied in with `attach_file`: `source` `<environment>:<path>`, a file or a folder
  whole or in part as the chat decides, every file of one call one batch; and no `to`, so that it
  hangs on nothing until Create project hangs it on the opening. The call answers its
  attachments' ids and its effect line; `timeline.json`'s `attachments` then lists each with its
  path, `attachments/<batch>/<filename>`, which you read from the draft's folder and the draft
  links.
- A copy is the file as it stood: a change at its source later is not seen. A refused call
  attached nothing: say so, with its reason, or fix the call.

## The reply

- Say only what the person needs to decide or do next: the asks the draft now holds for them,
  what you need from them, what you could not find. What the draft says is not retold.
- **Create project is the operator's**: never ask for it, and never say the draft is "ready".
  Say what is still open in it — its unanswered asks, a missing title or slug, what the chat has
  not settled. Create can be pressed with an ask still open: it stays open, and the setup reads
  the draft as it stands.

## Grounding

Facts outside the draft — a repository's code or history, a card, a tracker's projects, an
environment's files, a Fieldnotes post — are read through the fleet servers, never recalled or
guessed: the fleet file tools, youtrack, gitblit, fieldnotes. They read; nothing outside the
draft is made or changed here, a card, a repository or an environment the setup's to start, as
the draft agrees it.

## The server's follow-up turn

A turn of Pilot's server that names a save of yours still held — "Your save of `<path>` is held:
`<path>:<line>: <message>`. Fix it and end your turn." — is no person's: fix the file until its
check is clean and end the turn. The chat shows your reply to it as the rest of your last one.

## Not this skill's

No item is added, no work started and nothing marked: a draft has no timeline of items and no
plan until Create project, and the setup, `/plan`, starts what the draft agrees. `handbook.md`
and `plan.json` are the setup's, written from the draft. The words that started the draft, the
first definition chat's first message, become the opening at Create, verbatim: the draft does not
restate them.

## The brief

$ARGUMENTS
