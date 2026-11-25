# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""List Claude Code session transcripts for a project, newest first.

Transcripts live in ~/.claude/projects/<encoded-dir>/<session-id>.jsonl (or under
$CLAUDE_CONFIG_DIR when set), where the
folder name is the working directory with every non-alphanumeric character replaced
by '-'. Each worktree is its own working directory, so one project's sessions are
spread over its own folder, its Claude Code worktrees (<dir>/.claude/worktrees/*)
and any other git worktrees.

Gotcha: folder names are not a safe prefix match. G--dev-harness-eng is a different
project from G--dev-harness, so only exact encodings are matched.
"""

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

PROJECTS = Path(os.environ.get("CLAUDE_CONFIG_DIR") or Path.home() / ".claude") / "projects"


def encode(path: Path | str) -> str:
    """Lowercased, so drive-letter and path case differences on Windows/macOS still match."""
    return re.sub(r"[^A-Za-z0-9]", "-", str(path)).lower()


def worktree_dirs(cwd: Path) -> list[Path]:
    try:
        out = subprocess.run(
            ["git", "-C", str(cwd), "worktree", "list", "--porcelain"],
            capture_output=True, text=True, check=True,
        ).stdout
    except (OSError, subprocess.CalledProcessError):
        return []
    return [Path(line[len("worktree "):]) for line in out.splitlines() if line.startswith("worktree ")]


def project_folders(cwd: Path) -> list[Path]:
    """Folders for cwd as given and as resolved (symlinks such as macOS /tmp -> /private/tmp), plus its worktrees."""
    roots = {cwd.absolute(), cwd.resolve()}
    names = {encode(r) for r in roots} | {encode(p) for w in worktree_dirs(cwd) for p in (w, w.resolve())}
    prefixes = tuple(encode(r / ".claude" / "worktrees") + "-" for r in roots)
    return [d for d in PROJECTS.iterdir() if d.is_dir() and (d.name.lower() in names or d.name.lower().startswith(prefixes))]


def first_prompt(path: Path, width: int = 80) -> str:
    """First user text that isn't a command or system wrapper. Best effort: the line format is internal."""
    try:
        with path.open(encoding="utf-8", errors="replace") as f:
            for line in f:
                try:
                    event = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if event.get("type") != "user" or event.get("isSidechain"):
                    continue
                content = (event.get("message") or {}).get("content")
                if isinstance(content, list):
                    content = " ".join(c.get("text", "") for c in content if isinstance(c, dict) and c.get("type") == "text")
                if isinstance(content, str) and content.strip() and not content.lstrip().startswith("<"):
                    text = " ".join(content.split())
                    return text[: width - 1] + "…" if len(text) > width else text
    except OSError:
        pass
    return ""


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--cwd", default=".", help="project directory (default: current)")
    parser.add_argument("--limit", type=int, default=20, help="max sessions to list (default 20)")
    parser.add_argument("--json", action="store_true", help="print [{path, bytes, modified, prompt}]")
    args = parser.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")

    cwd = Path(args.cwd).absolute()
    if not PROJECTS.is_dir():
        raise SystemExit(f"Error: no transcripts folder at {PROJECTS}.")
    files = [f for d in project_folders(cwd) for f in d.glob("*.jsonl")]
    if not files:
        raise SystemExit(f"Error: no sessions found for {cwd} (looked for {encode(cwd)} in {PROJECTS}). Pass --cwd for another project.")
    files.sort(key=lambda f: f.stat().st_mtime, reverse=True)

    rows = [
        {
            "path": str(f),
            "bytes": f.stat().st_size,
            "modified": datetime.fromtimestamp(f.stat().st_mtime).strftime("%Y-%m-%d %H:%M"),
            "prompt": first_prompt(f),
        }
        for f in files[: args.limit]
    ]
    if args.json:
        print(json.dumps(rows, ensure_ascii=False, indent=1))
    else:
        for r in rows:
            print(f"{r['modified']}  {r['bytes'] // 1024:>6} KB  {r['path']}\n    {r['prompt']}")
    if len(files) > args.limit:
        print(f"({len(files) - args.limit} older sessions not shown; raise --limit)", file=sys.stderr)


if __name__ == "__main__":
    main()
