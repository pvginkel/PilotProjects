#!/usr/bin/env python3
"""The project's write lock around a brain session's writing tool call, and the check that
is its release (PilotApp's docs/sync.md).

The hook of .claude/settings.json, on the events its stdin's `hook_event_name` names. Each
posts to pilot-sync's local endpoint on 127.0.0.1, at the port PILOT_SYNC_LOCAL_PORT names in
the hook's own environment, 3510 when unset. The store's dev container does not set it, so
live the hook calls 3510, the port both stages' catalog entries give the sidecar: a sidecar
moved to another port needs this default moved with it. The body is JSON, `{"project":
$PILOT_PROJECT, "session": $PILOT_SESSION}` and the session's Claude process:

- PreToolUse, before an Edit, Write, MultiEdit or Bash call: `/lock` with the process's pid.
  The call runs on a 200 alone; on any other answer, or none within LOCK_CAP_SECONDS, it is
  denied, the reason saying why.
- PostToolUse and PostToolUseFailure, after the call ran or failed: `/release` with the pid.
  pilot-sync sends up what is unsent of the project's folder, asks the server's check of the
  folder and gives the hold back; its answer, or that none came, goes before the agent as
  `hookSpecificOutput.additionalContext`, plain stdout never reaching the model.
- Stop, at the turn's end: `/release` with `"all": true`, which gives back every hold of the
  session, so that none outlives its turn. Its check deletes the resets it reads, so a
  non-empty answer goes before the agent, which goes on with it; not when the stop follows
  one that a stop hook kept going, where the same answer would keep the turn going forever.

A session without PILOT_PROJECT, none that Pilot's server created, takes no lock and posts
nothing. Claude Code lets a call run when its hook fails or passes its timeout, so the lock's
failures are denials, and settings.json's timeouts sit above the caps here, which sit above
pilot-sync's own bounds: the lock's 60 s wait, the release's 5 s flush and 5 s check.
"""

import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

LOCK_CAP_SECONDS = 70
RELEASE_CAP_SECONDS = 15
NOT_YET_CHECKED = "not yet checked: "
# The interpreters Claude Code may run a command hook through ($SHELL, or /bin/sh).
SHELLS = frozenset({"sh", "bash", "dash", "zsh"})


def claude_pid() -> int:
    """The session's Claude process: Claude Code runs a command hook directly or through a
    shell, so it is the hook's nearest ancestor that is no shell."""
    pid = os.getppid()
    while Path(f"/proc/{pid}/comm").read_text().strip() in SHELLS:
        stat = Path(f"/proc/{pid}/stat").read_text()
        pid = int(stat.rpartition(")")[2].split()[1])
    return pid


def post(route: str, call: dict, cap: float) -> tuple[int, str]:
    """pilot-sync's answer to the call, its status and its text; an OSError when none came
    within the cap. 127.0.0.1 is asked directly, never through a proxy the environment
    names."""
    port = os.environ.get("PILOT_SYNC_LOCAL_PORT", "3510")
    request = urllib.request.Request(
        f"http://127.0.0.1:{port}{route}",
        data=json.dumps(call).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    try:
        with opener.open(request, timeout=cap) as response:
            return response.status, response.read().decode()
    except urllib.error.HTTPError as error:
        return error.code, error.read().decode()


def lock(call: dict) -> dict | None:
    """The PreToolUse's output: none once the hold is taken, else the call's denial."""
    try:
        status, text = post("/lock", {**call, "pid": claude_pid()}, LOCK_CAP_SECONDS)
    except OSError as error:
        reason = f"not run without the project's write lock: pilot-sync did not answer: {error}"
    else:
        if status == 200:
            return None
        reason = (
            text.strip()
            if status == 409
            else f"not run without the project's write lock: pilot-sync answered {status}:"
            f" {text.strip()}"
        )
    return {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
        }
    }


def release(event: str, call: dict, folder: str) -> dict | None:
    """The output of a release hook: its answer before the agent, none when it is empty."""
    try:
        status, text = post("/release", call, RELEASE_CAP_SECONDS)
    except OSError as error:
        text = f"{NOT_YET_CHECKED}{folder}/ (pilot-sync did not answer: {error})\n"
    else:
        if status != 200:
            text = f"{NOT_YET_CHECKED}{folder}/ (pilot-sync answered {status}: {text.strip()})\n"
    if not text:
        return None
    return {"hookSpecificOutput": {"hookEventName": event, "additionalContext": text}}


def main() -> None:
    hook = json.load(sys.stdin)
    project = os.environ.get("PILOT_PROJECT")
    if not project:
        return
    call = {"project": project, "session": os.environ.get("PILOT_SESSION", "")}
    folder = os.path.basename(os.path.normpath(project))
    event = hook["hook_event_name"]
    if event == "PreToolUse":
        output = lock(call)
    elif event == "Stop":
        output = release(event, {**call, "all": True}, folder)
        if hook["stop_hook_active"]:
            output = None
    else:
        output = release(event, {**call, "pid": claude_pid()}, folder)
    if output is not None:
        json.dump(output, sys.stdout)


if __name__ == "__main__":
    main()
