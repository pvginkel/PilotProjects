#!/usr/bin/env python3
"""Pilot's check of a file of the record's tree, after the agent's Edit or Write.

The PostToolUse hook of .claude/settings.json (design 1 §5.6). It reads the tool's
`file_path` from stdin and, for a file under /work/Projects/, asks pilot-sync's local
check what the record made of it: `GET /check?path=` on 127.0.0.1, the port the
sidecar's PILOT_SYNC_LOCAL_PORT names, 3510 when unset. A non-empty answer goes before
the agent as `hookSpecificOutput.additionalContext`; plain stdout never reaches the
model. A path outside the tree is not asked about, and a sidecar that is down, answers
an error or is past the cap adds nothing. It exits 0 on every answer, so it never stops
the turn; settings.json's timeout of 5 s bounds it above the cap.
"""

import json
import os
import sys
import urllib.parse
import urllib.request

TREE = "/work/Projects/"
CAP_SECONDS = 3


def main() -> None:
    path = json.load(sys.stdin)["tool_input"]["file_path"]
    if not path.startswith(TREE):
        return
    port = os.environ.get("PILOT_SYNC_LOCAL_PORT", "3510")
    query = urllib.parse.urlencode({"path": path})
    try:
        with urllib.request.urlopen(
            f"http://127.0.0.1:{port}/check?{query}", timeout=CAP_SECONDS
        ) as response:
            answer = response.read().decode()
    except OSError:
        return
    if answer:
        json.dump(
            {
                "hookSpecificOutput": {
                    "hookEventName": "PostToolUse",
                    "additionalContext": answer,
                }
            },
            sys.stdout,
        )


main()
