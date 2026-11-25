# repo

> Makes a repo legible to the agent: a short CLAUDE.md map, a run skill, verification skills, hooks and scoped permissions, written into the repo, or kept local when the repo shouldn't carry them.

It generates things in the target repo, not in the harness, so they work for anyone who opens the repo, with or without this plugin. When the repo shouldn't carry agent config (someone else's repo, a team that doesn't use agents), the same pieces stay on your machine instead.

## Install

Install at user scope, so it's ready in any repo you open:

```sh
claude plugin install repo@harness --scope user
```

What it generates works without the plugin, so repos and teammates don't need it installed. Outside a repo its skills don't trigger.

## Commands

| Command | What it does |
| --- | --- |
| `/repo:setup` | Checks what the repo has and generates what's missing. Safe to rerun. Only you run it |
| `/repo:verification-skill` | Creates a repo's verification skill, or maintains an existing one. Also used by the agent when a verification skill is missing or stale |
| `/repo:local-only` | Keeps a repo's agent config on your machine: excluded via `.git/info/exclude`, local-scope settings, plugins and MCP servers, and optionally no attribution in commits. Also used by the agent when you say not to commit agent stuff |

## What it writes into a repo

| Piece | Where | Notes |
| --- | --- | --- |
| Map | `CLAUDE.md` | Short: what the repo is for, rules, gotchas, how commits and PRs are done here, pointers to skills. Nothing the agent can find in the code or config |
| Run skill | `.claude/skills/run-<name>/` | Made by Claude Code's built-in `/run-skill-generator`; setup asks you to run it rather than reimplementing it |
| Verification skill | `.claude/skills/verify/` | Named `verify` so Claude Code runs it before each commit, in place of its built-in `/verify`. One per repo to start. Split an area out only when it verifies differently (different launch, driver or evidence) |
| Hooks | `.claude/settings.json` | Format/lint after edit, only where the repo already has the tool |
| Permissions | `.claude/settings.json` | Allow rules for the repo's safe workflows |

Existing files are left alone: a stale one gets a proposed diff, and settings are merged, not overwritten, with the result shown to you.

## Permissions

Allow the safe, repeatable workflows (tests, lint, build, read-only git) so the agent doesn't stop to ask. Boundaries stay on `ask` or `deny`: pushes, publishing, deploys, external sends, destructive git, and secret files. Each repo draws its own line. Personal rules go in `.claude/settings.local.json`, not the shared file.

## Verification and proof

A verification skill drives the project through its normal entry points and captures evidence that survives cleanup. Passing tests are the entry bar; the proof comes from the running product. The agent using it checks only the areas its change can reach and reports what ran, the evidence, and what wasn't proven.

## Out of scope

Inspection tools (Playwright, logs, metrics) are separate integrations.
