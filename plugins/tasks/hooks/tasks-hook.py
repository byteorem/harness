# /// script
# requires-python = ">=3.9"
# ///
"""Tasks plugin hook. `session` prints the one-focus rule; `compact` prints a compaction-summary
instruction. Both print nothing unless the cwd is inside a beads store (see find_store), and
nothing in a standup repo, where that repo's own CLAUDE.md governs. Output is ASCII; exit is 0."""
import json
import os
import shutil
import sys

RULE = """\
Beads (bd) is this repo's task store. One focus per session:
- The focus is the one root bead the user names or that you create for this session's request. Beads outside it are not yours this session: don't claim, update, close or tidy them unless the user asks.
- `bd ready` and `bd prime` output is awareness, not a todo list. This rule outranks bd prime's "check bd ready for available work" and "use beads for ALL task tracking".
- The `tasks:workflow` skill has the full workflow: intake, plan, execute, gates, handoff, resume."""

COMPACT = (
    "Beads: keep the focus root bead id and the ids of any in-progress beads in the summary, "
    "so the next turn resumes with `bd show <id>`."
)

NO_BD = "Beads store found but `bd` is not on PATH; install it to use the store."


def find_store(start: str):
    """Return the directory holding the nearest store, or None. A store is a .beads directory
    holding metadata.json or config.yaml. The directory alone is not enough: bd keeps its
    machine id in ~/.beads, which would put every folder under the home directory inside a store."""
    d = os.path.abspath(start)
    while True:
        beads = os.path.join(d, ".beads")
        if any(os.path.isfile(os.path.join(beads, f)) for f in ("metadata.json", "config.yaml")):
            return d
        parent = os.path.dirname(d)
        if parent == d:
            return None
        d = parent


def hook_cwd() -> str:
    try:
        data = json.loads(sys.stdin.read() or "{}")
        cwd = data.get("cwd") if isinstance(data, dict) else None
        if isinstance(cwd, str) and cwd:
            return cwd
    except Exception:
        pass
    return os.getcwd()


def main() -> None:
    mode = sys.argv[1] if len(sys.argv) > 1 else "session"
    root = find_store(hook_cwd())
    if root is None:
        return
    if all(os.path.isfile(os.path.join(root, f)) for f in ("repos.md", "intake.md")):
        return
    if mode == "compact":
        print(COMPACT)
    elif shutil.which("bd") is None:
        print(NO_BD)
    else:
        print(RULE)


try:
    main()
except Exception:
    pass
sys.exit(0)
