# tasks

> A task workflow for coding agents, on beads (bd): one focus per session with plans, gates and handoffs in each repo, plus a standup repo that reports across repos, triages asks and routes email into tasks.

Two halves. In each repo with a [Beads](https://github.com/gastownhall/beads) (`bd`) store, the agent works one focus per session: a request becomes a root bead with a plan, external waits become gates, and a pause or end leaves a handoff that the next session picks up. A separate standup repo, with its own store, reports what is in progress, ready and waiting across your repos, triages asks into beads and routes email into them.

## Install

Install at user scope. Everything is silent outside a beads store, so it costs nothing in other folders:

```sh
claude plugin install tasks@harness --scope user
```

## Requirements

[`bd`](https://github.com/gastownhall/beads) (tested with 1.3.2) on PATH, and [`uv`](https://docs.astral.sh/uv/) for the hook and the standup scripts.

## What's in it

| Piece | What it does |
| --- | --- |
| `workflow` skill | The repo workflow: how a request becomes a focus with a plan, how work is claimed and executed, how waits become gates, and how a session is paused, ended and resumed. Loads when a request becomes tracked work in a repo with a bd store |
| `/tasks:standup-setup [path]` | Creates or refreshes a standup repo in the current folder or `path`. Only you run it |
| SessionStart hook | Prints the core rule: one focus per session, beads outside the focus aren't yours, and `bd ready` and `bd prime` are awareness, not a todo list. Prints one line if a store exists but `bd` is missing |
| PreCompact hook | Asks the summary to keep the focus root bead id and any in-progress bead ids |
| `skills/standup-setup/scripts/install.py` | Run by `standup-setup`: writes the standup repo's files. Needs an existing store there; it tells you to run `bd init` and never runs it |
| `scripts/report.py`, `scripts/ledger.py` | Standup scripts, copied into the standup repo (see below) |

Both hooks print nothing outside a store, and nothing in a standup repo, where its own `CLAUDE.md` governs.

## The standup repo

Run `bd init` in a folder, then `/tasks:standup-setup`. The repo holds its own bead store as an inbox, and runs everything from its own copy of the scripts:

| File | Setup |
| --- | --- |
| `CLAUDE.md` | Rewritten every run. A `CLAUDE.md` that isn't ours is refused unless you pass `--force` |
| `intake.md` | Rewritten every run |
| `scripts/report.py` | Rewritten every run. `uv run --script scripts/report.py [--repo <name>] [--json]` reports in progress, ready, gates and blocked for each tracked repo, then the inbox. Read-only |
| `scripts/ledger.py` | Rewritten every run. `uv run --script scripts/ledger.py seen\|dedupe\|append` keeps the record of processed messages so reruns don't repeat |
| `repos.md` | Created if missing, never touched afterwards: your tracked repos |
| `channels.md` | Created if missing, never touched afterwards: your intake channels |
| `intake/ledger.jsonl` | Created if missing, only ever appended to by `ledger.py` |

Rerun setup after updating the plugin to refresh the rewritten files. Your `repos.md`, `channels.md` and ledger stay as they are.

## Permissions

Allow the safe bd read and write commands the workflow and the standup use, and the two standup scripts, so the agent doesn't stop to ask. The same rules apply to the Bash and PowerShell tools. Put them in `~/.claude/settings.json`, or in the standup repo's `.claude/settings.local.json` for the scripts:

```json
{
  "permissions": {
    "allow": [
      "Bash(bd show:*)", "Bash(bd list:*)", "Bash(bd ready:*)", "Bash(bd blocked:*)",
      "Bash(bd prime:*)", "Bash(bd dep tree:*)", "Bash(bd dep add:*)",
      "Bash(bd create:*)", "Bash(bd update:*)", "Bash(bd close:*)", "Bash(bd defer:*)",
      "Bash(bd gate list:*)", "Bash(bd gate check:*)", "Bash(bd gate create:*)", "Bash(bd gate resolve:*)",
      "Bash(uv run --script scripts/report.py:*)", "Bash(uv run --script scripts/ledger.py:*)",
      "PowerShell(bd show:*)", "PowerShell(bd list:*)", "PowerShell(bd ready:*)", "PowerShell(bd blocked:*)",
      "PowerShell(bd prime:*)", "PowerShell(bd dep tree:*)", "PowerShell(bd dep add:*)",
      "PowerShell(bd create:*)", "PowerShell(bd update:*)", "PowerShell(bd close:*)", "PowerShell(bd defer:*)",
      "PowerShell(bd gate list:*)", "PowerShell(bd gate check:*)", "PowerShell(bd gate create:*)", "PowerShell(bd gate resolve:*)",
      "PowerShell(uv run --script scripts/report.py:*)", "PowerShell(uv run --script scripts/ledger.py:*)"
    ]
  }
}
```

Leave `bd init`, `bd delete`, anything touching `bd dolt` (including `bd dolt push`) and anything that publishes or sends to prompt.

## Design notes

- The core rule is a hook, not only a skill, because a skill loads too late to outrank `bd prime`'s "check `bd ready` for available work" and "use beads for ALL task tracking". The hook states the rule at session start, and the skill carries the full workflow.
- The standup scripts are copied into the standup repo, so it works without the plugin installed and its `CLAUDE.md` never refers to a plugin path.
- The hook script is Python run with `uv`, stdlib only. It walks up from the cwd looking for a `.beads` directory that holds a store's `metadata.json` or `config.yaml`; that is the whole cost outside a store. The directory alone doesn't count, because bd keeps its machine id in `~/.beads`.
- PreCompact stdout steers the compaction summary rather than loading context, and SessionStart fires again after compaction, so the core rule lives only on SessionStart.

## Later

Scheduled intake that only produces the proposal table.
