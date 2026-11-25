# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""Install or refresh a beads standup repo.

Always rewritten (the plugin's text): CLAUDE.md, intake.md, scripts/report.py,
scripts/ledger.py. Created only when missing (the user's data): repos.md,
channels.md, intake/ledger.jsonl. Never runs bd.

An existing CLAUDE.md whose first heading is not '# Standup repo' is left alone
and the script exits 1, unless --force is given.
"""
import argparse
import sys
from pathlib import Path

ASSETS = Path(__file__).resolve().parent.parent / "assets"
HEADING = "# Standup repo"
ALWAYS = ["CLAUDE.md", "intake.md", "scripts/report.py", "scripts/ledger.py"]
IF_MISSING = ["repos.md", "channels.md"]
LEDGER = "intake/ledger.jsonl"


def has_store(target: Path) -> bool:
    beads = target / ".beads"
    return (beads / "metadata.json").is_file() or (beads / "config.yaml").is_file()


def first_heading(path: Path) -> str | None:
    in_fence = False
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
        elif not in_fence and line.startswith("#"):
            return line.strip()
    return None


def main() -> int:
    ap = argparse.ArgumentParser(description="Install or refresh a beads standup repo.")
    ap.add_argument("--target", required=True, help="the standup repo directory (needs its own .beads store)")
    ap.add_argument("--force", action="store_true", help="overwrite an existing CLAUDE.md that isn't a standup CLAUDE.md")
    args = ap.parse_args()

    target = Path(args.target).expanduser().resolve()
    if not target.is_dir():
        print(f"Error: {target} is not a directory. Create it, run `bd init` in it, then rerun.", file=sys.stderr)
        return 2
    if not has_store(target):
        print(f"Error: no beads store in {target} (.beads/ with metadata.json or config.yaml). "
              f"Run `bd init` in {target}, then rerun.", file=sys.stderr)
        return 2
    missing = [n for n in ALWAYS + IF_MISSING if not (ASSETS / n).is_file()]
    if missing:
        print(f"Error: plugin assets missing under {ASSETS}: {', '.join(missing)}. Reinstall the beads plugin.", file=sys.stderr)
        return 2

    written, kept, skipped = [], [], []

    for name in ALWAYS:
        dest = target / name
        if name == "CLAUDE.md" and dest.exists() and not args.force:
            head = first_heading(dest)
            if head != HEADING:
                skipped.append(f"CLAUDE.md (existing first heading is {head!r}, not {HEADING!r}; use --force to replace)")
                continue
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes((ASSETS / name).read_bytes())
        written.append(name)

    for name in IF_MISSING:
        dest = target / name
        if dest.exists():
            kept.append(name)
        else:
            dest.write_bytes((ASSETS / name).read_bytes())
            written.append(name)

    ledger = target / LEDGER
    if ledger.exists():
        kept.append(LEDGER)
    else:
        ledger.parent.mkdir(parents=True, exist_ok=True)
        ledger.write_bytes(b"")
        written.append(LEDGER)

    print(f"Standup repo: {target}")
    print("Written: " + (", ".join(written) or "none"))
    print("Kept (yours, untouched): " + (", ".join(kept) or "none"))
    if skipped:
        print("Skipped: " + "; ".join(skipped))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
