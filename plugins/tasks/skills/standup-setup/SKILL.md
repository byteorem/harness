---
name: standup-setup
description: Create or refresh a beads standup repo (report, triage and intake across repos) in the current directory or a given path.
argument-hint: "[path]"
disable-model-invocation: true
---

# Standup setup

Goal: the target directory is a working standup repo: the plugin's `CLAUDE.md` and `intake.md`, the report and ledger scripts, and starter `repos.md` and `channels.md` that setup never overwrites. The directory is `$ARGUMENTS`, or the current one if that's empty.

Run it, then report the script's summary (written, kept, skipped) in a few lines:

```bash
uv run --script scripts/install.py --target <dir>
```

- The target needs its own beads store. If the script says there is none, tell the user to run `bd init` there and stop. Never run `bd init` yourself.
- If the script refuses because `CLAUDE.md` exists and isn't a standup `CLAUDE.md`, relay that. Offer `--force` only if the user wants it replaced.
- Re-running after a plugin update refreshes the plugin's text and leaves the user's `repos.md`, `channels.md` and ledger alone.
- Finish by telling the user what is theirs to fill in: `repos.md` (one entry per tracked repo) and `channels.md` (the email MCP name and ignore rules).

## Scripts

- `uv run --script scripts/install.py --target <dir> [--force]`: installs or refreshes the standup repo files from `assets/`
