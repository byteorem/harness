# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Intake ledger: an append-only JSONL record of processed messages.

Usage:
  uv run --script scripts/ledger.py [--ledger PATH] seen --channel email
  ... | uv run --script scripts/ledger.py dedupe --channel email
  ... | uv run --script scripts/ledger.py append

Gotchas:
- Default ledger is <cwd>/intake/ledger.jsonl; a missing file counts as empty.
- Input on stdin is a JSON array or JSONL (one object per line).
- Identity is (channel, msg_id). `append` skips entries already in the ledger or
  earlier in the same input, so reruns are safe.
- `append` validates every entry before writing anything, and only appends.
- `target` must be present but may be null (skip and reply-needed entries).
"""
import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

REQUIRED = ["channel", "msg_id", "thread_id", "received", "from", "subject", "action", "target"]
ACTIONS = ["new", "update", "gate", "reply-needed", "skip"]


def fail(msg):
    print(f"Error: {msg}", file=sys.stderr)
    sys.exit(1)


def read_items(label):
    """Parse stdin as a JSON array or JSONL; return [(where, obj)]."""
    text = sys.stdin.read()
    if not text.strip():
        fail(f"no input on stdin. Pipe in a JSON array or JSONL of {label}.")
    if text.lstrip().startswith("["):
        try:
            arr = json.loads(text)
        except json.JSONDecodeError as e:
            fail(f"invalid JSON array: {e}")
        items = [(f"array index {i}", o) for i, o in enumerate(arr)]
    else:
        items = []
        for n, line in enumerate(text.splitlines(), 1):
            if not line.strip():
                continue
            try:
                items.append((f"line {n}", json.loads(line)))
            except json.JSONDecodeError as e:
                fail(f"line {n}: invalid JSON: {e}")
    for where, o in items:
        if not isinstance(o, dict):
            fail(f"{where}: expected a JSON object")
    return items


def load_ledger(path):
    """Return [entry] from the ledger; a missing file is empty."""
    p = Path(path)
    if not p.is_file():
        return []
    out = []
    for n, line in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError as e:
            fail(f"{p} line {n}: invalid JSON: {e}")
    return out


def need_str(where, o, field):
    v = o.get(field)
    if v is None or isinstance(v, (dict, list)) or str(v).strip() == "":
        fail(f"{where}: field '{field}' is missing or empty")
    return str(v)


def cmd_seen(a):
    for e in load_ledger(a.ledger):
        if e.get("channel") == a.channel and "msg_id" in e:
            print(e["msg_id"])


def cmd_dedupe(a):
    seen = {str(e.get("msg_id")) for e in load_ledger(a.ledger) if e.get("channel") == a.channel}
    items = read_items("messages, each with msg_id")
    for where, o in items:
        need_str(where, o, "msg_id")
    for _, o in items:
        if str(o["msg_id"]) not in seen:
            print(json.dumps(o, ensure_ascii=False))


def cmd_append(a):
    existing = {(str(e.get("channel")), str(e.get("msg_id"))) for e in load_ledger(a.ledger)}
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    items = read_items("entries")
    for where, o in items:
        for f in REQUIRED:
            if f == "target" and f in o and o[f] is None:
                continue  # null target is how skip and reply-needed entries are written
            need_str(where, o, f)
        if o["action"] not in ACTIONS:
            fail(f"{where}: field 'action' is '{o['action']}'; expected one of {'|'.join(ACTIONS)}")
    new, skipped = [], 0
    for _, o in items:
        key = (str(o["channel"]), str(o["msg_id"]))
        if key in existing:
            skipped += 1
            continue
        existing.add(key)
        if not o.get("processed"):
            o["processed"] = now
        new.append(o)
    if new:
        p = Path(a.ledger)
        p.parent.mkdir(parents=True, exist_ok=True)
        needs_nl = p.is_file() and p.stat().st_size > 0 and not p.read_bytes().endswith(b"\n")
        with p.open("a", encoding="utf-8", newline="\n") as f:
            if needs_nl:
                f.write("\n")
            for o in new:
                f.write(json.dumps(o, ensure_ascii=False) + "\n")
    print(f"appended {len(new)}, skipped {skipped}")


def main():
    ap = argparse.ArgumentParser(
        description="Append-only ledger of processed intake messages (JSONL). Never prompts.")
    ap.add_argument("--ledger", default=str(Path.cwd() / "intake" / "ledger.jsonl"),
                    help="ledger path (default: ./intake/ledger.jsonl)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("seen", help="print known msg_ids for a channel, one per line")
    s.add_argument("--channel", required=True)
    s.set_defaults(fn=cmd_seen)
    d = sub.add_parser("dedupe",
                       help="read messages (JSON array or JSONL with msg_id) on stdin; print unseen ones as JSONL")
    d.add_argument("--channel", required=True)
    d.set_defaults(fn=cmd_dedupe)
    p = sub.add_parser("append",
                       help="read entries (JSON array or JSONL) on stdin; validate, then append new ones. "
                            "Required: " + ", ".join(REQUIRED) + ". action: " + "|".join(ACTIONS)
                            + ". processed defaults to now (UTC).")
    p.set_defaults(fn=cmd_append)
    a = ap.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
