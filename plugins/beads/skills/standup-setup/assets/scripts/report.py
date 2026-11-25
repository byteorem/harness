# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Standup report across the repos listed in repos.md. Read-only.

Run from the standup repo: uv run --script scripts/report.py [--repo NAME] [--json]

Gotchas:
- repos.md: each `### <name>` heading starts a repo; its `- **Path:** `<path>``
  line gives the path. <!-- comments --> (also multi-line) are ignored.
- A store is a .beads dir holding metadata.json or config.yaml; a bare .beads
  dir (bd keeps a machine id in ~/.beads) does not count.
- Gates are hidden from `bd list`; `bd gate list` returns them.
- A gate on a parent also blocks its children, so a child can show a non-gate
  blocker (the parent).
- Only read-only bd commands run here: list, ready, gate list, blocked.
"""
import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

CAP = 10


def strip_comments(text):
    return re.sub(r"<!--.*?-->", "", text, flags=re.S)


def parse_repos(path):
    """Return [{'name', 'path'}] from repos.md; path is None when absent."""
    repos, cur = [], None
    for line in strip_comments(path.read_text(encoding="utf-8")).splitlines():
        m = re.match(r"^###\s+(.+?)\s*$", line)
        if m:
            cur = {"name": m.group(1), "path": None}
            repos.append(cur)
            continue
        m = re.match(r"^\s*-\s+\*\*Path:\*\*\s*`([^`]+)`", line)
        if m and cur is not None and cur["path"] is None:
            cur["path"] = str(Path(m.group(1).strip()).expanduser())
    return repos


def has_store(d):
    b = Path(d) / ".beads"
    return (b / "metadata.json").is_file() or (b / "config.yaml").is_file()


class BdError(Exception):
    pass


def bd(bd_path, cwd_dir, *args):
    """Run `bd -C <dir> <args> --json`; return parsed list (empty on null/empty)."""
    cmd = [bd_path, "-C", str(cwd_dir), *args, "--json"]
    try:
        p = subprocess.run(cmd, capture_output=True, encoding="utf-8",
                           errors="replace", timeout=60)
    except (OSError, subprocess.TimeoutExpired) as e:
        raise BdError(f"bd {' '.join(args)}: {e}")
    if p.returncode != 0:
        msg = (p.stderr or p.stdout or "").strip().splitlines()
        raise BdError(f"bd {' '.join(args)} failed: {msg[0] if msg else p.returncode}")
    out = p.stdout.strip()
    if not out:
        return []
    try:
        data = json.loads(out)
    except json.JSONDecodeError:
        raise BdError(f"bd {' '.join(args)}: output was not JSON")
    if data is None:
        return []
    if isinstance(data, dict):
        data = [data]
    if not isinstance(data, list):
        raise BdError(f"bd {' '.join(args)}: unexpected JSON shape")
    return [x for x in data if isinstance(x, dict)]


def brief(i):
    return {"id": i.get("id", "?"), "title": i.get("title", "")}


def gate_reason(g):
    for line in (g.get("description") or "").splitlines():
        if line.startswith("Reason:"):
            r = line[len("Reason:"):].strip()
            if r:
                return r
    return g.get("title") or "gate"


def day(ts):
    return (ts or "")[:10]


def collect_repo(bd_path, path):
    prog = bd(bd_path, path, "list", "--status", "in_progress", "-n", "0")
    ready = bd(bd_path, path, "ready", "-n", "0")
    gates = {g.get("id"): g for g in bd(bd_path, path, "gate", "list", "-n", "0")}
    blocked = bd(bd_path, path, "blocked")
    prog_ids = {i.get("id") for i in prog}
    titles = {i.get("id"): i.get("title", "") for i in prog + ready + blocked}
    waiting = []
    for b in blocked:
        entry = brief(b)
        by = []
        for bid in b.get("blocked_by") or []:
            g = gates.get(bid)
            if g:
                by.append({"id": bid, "gate": True, "reason": gate_reason(g),
                           "since": day(g.get("created_at"))})
            else:
                by.append({"id": bid, "gate": False, "title": titles.get(bid, "")})
        entry["blocked_by"] = by
        waiting.append(entry)
    return {
        "in_progress": [brief(i) for i in prog],
        "waiting": waiting,
        "ready": [brief(i) for i in ready if i.get("id") not in prog_ids],
    }


def run(root, only, bd_path):
    repos_md = root / "repos.md"
    if not repos_md.is_file():
        sys.exit(f"Error: {repos_md} not found. Use --root <standup dir> or run setup first.")
    repos = parse_repos(repos_md)
    if only:
        repos = [r for r in repos if r["name"] == only]
        if not repos:
            names = ", ".join(r["name"] for r in parse_repos(repos_md)) or "(none)"
            sys.exit(f"Error: unknown repo '{only}'. Known repos: {names}.")
    result = []
    for r in repos:
        entry = {"name": r["name"], "path": r["path"]}
        try:
            if not r["path"]:
                raise BdError("no Path line in repos.md")
            if not Path(r["path"]).is_dir():
                raise BdError(f"path not found: {r['path']}")
            if not has_store(r["path"]):
                raise BdError(f"no beads store at {r['path']} (run bd init there)")
            if not bd_path:
                raise BdError("bd not found on PATH")
            entry.update(collect_repo(bd_path, r["path"]))
        except BdError as e:
            entry["error"] = str(e)
        result.append(entry)
    inbox = None
    if not only:
        try:
            if not has_store(root):
                raise BdError(f"no beads store at {root}")
            if not bd_path:
                raise BdError("bd not found on PATH")
            inbox = [brief(i) for i in bd(bd_path, root, "list", "--status", "open", "-n", "0")]
        except BdError as e:
            inbox = {"error": str(e)}
    return {"repos": result, "inbox": inbox}


def section(label, items, fmt):
    lines = []
    for n, it in enumerate(items[:CAP]):
        prefix = f"  {label:<13}" if n == 0 else " " * 15
        lines.append(prefix + fmt(it))
    if len(items) > CAP:
        lines.append(" " * 15 + f"+{len(items) - CAP} more")
    return lines


def fmt_wait(w):
    on = []
    for b in w["blocked_by"]:
        if b["gate"]:
            on.append(f"{b['reason']} (since {b['since']})" if b["since"] else b["reason"])
        else:
            on.append(f"{b['id']} {b['title']}".strip())
    s = f"{w['id']} {w['title']}"
    return f"{s}, on {'; '.join(on)}" if on else s


def render(data):
    out = []
    plain = lambda i: f"{i['id']} {i['title']}"
    for r in data["repos"]:
        lines = []
        if "error" in r:
            lines.append(f"  ! {r['error']}")
        else:
            lines += section("In progress:", r["in_progress"], plain)
            lines += section("Waiting:", r["waiting"], fmt_wait)
            lines += section("Ready next:", r["ready"], plain)
        if lines:
            out.append(r["name"])
            out += lines
    inbox = data["inbox"]
    if isinstance(inbox, dict):
        out.append(f"Inbox: ! {inbox['error']}")
    elif inbox:
        out.append(f"Inbox: {len(inbox)} unrouted")
        for it in inbox[:CAP]:
            out.append(f"  {plain(it)}")
        if len(inbox) > CAP:
            out.append(f"  +{len(inbox) - CAP} more")
    return "\n".join(out) if out else "Nothing in flight."


def main():
    ap = argparse.ArgumentParser(
        description="Standup report across the repos in repos.md, plus the standup repo's inbox. "
                    "Read-only; never writes to any store.")
    ap.add_argument("--repo", help="report only this repo (name from repos.md)")
    ap.add_argument("--json", action="store_true", help="print structured JSON instead of text")
    ap.add_argument("--root", type=Path,
                    help="standup repo root (default: the parent of this script's directory)")
    a = ap.parse_args()
    root = (a.root or Path(__file__).resolve().parent.parent).resolve()
    bd_path = shutil.which("bd")
    data = run(root, a.repo, bd_path)
    if a.json:
        print(json.dumps(data, indent=2))
    else:
        print(render(data))


if __name__ == "__main__":
    main()
