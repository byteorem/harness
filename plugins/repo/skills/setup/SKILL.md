---
name: setup
description: Use when the user asks to set up, onboard or refresh a repo for agents. Audits it and generates the missing CLAUDE.md, run and verify skills, hooks and permissions.
disable-model-invocation: true
---

# Repo setup

Goal: after this, an agent opening the repo can understand it, start it, and check its own changes, with every piece living in the repo (never in the harness). Setup is idempotent: generate only what's missing, and leave existing files alone unless the user asks to change them.

Do it in one pass. Check what the repo already has for each piece below and whether it is still accurate, along with its formatter, linter, test and build commands; report that in a few lines and go straight on to generating the gaps. Creating a missing file needs no approval. A stale `CLAUDE.md` or skill gets its edits proposed as a diff, not regenerated. Ask only for what can't be discovered (e.g. which environment counts as safe to run against). If the user doesn't want agent config committed to this repo, use the `repo:local-only` skill for where each piece goes.

## Pieces

| Piece | Where it goes | How |
| --- | --- | --- |
| CLAUDE.md | `CLAUDE.md` | Short map; see the CLAUDE.md notes below |
| Run skill | `.claude/skills/run-<name>/` | Built in: `/run-skill-generator` launches the app, records what worked and writes the skill. Don't reimplement it. It is interactive, so if you can't run it, leave it to the user. Skip it when the repo has no runnable app (library, config repo) |
| Verification skill | `.claude/skills/verify/` | Use the `repo:verification-skill` skill. One per repo to start |
| Hooks | `.claude/settings.json` | Under `hooks`; see Judgment calls and Gotchas below |
| Permissions | `.claude/settings.json` | Under `permissions`; see Judgment calls below |

## CLAUDE.md

A map of under about 40 lines: what the repo is for, and what an agent would get wrong without being told. Leave out anything it can discover from the code, the README or the config, and point to the run and verify skills instead of inlining their procedures.

- If `AGENTS.md` exists, the content goes there and `CLAUDE.md` is the single line `See @AGENTS.md`.
- Gotchas come from evidence (failed runs, review comments, things the user corrected), not from guessing. None on day one is fine.
- Rules state intent ("keep X out of Y because Z"), not step lists.

## Judgment calls

- Hooks: add one only for a tool the repo already uses (its formatter, linter or type checker), running its fast, file-scoped command.
- Permissions: allow the safe, repeatable workflows the audit found (test, lint, build, read-only git). Keep anything that is hard to undo or visible outside the repo on ask or deny: push, publish, deploy, external sends, destructive git, secrets. Each repo draws its own line.
- Merge into an existing `.claude/settings.json`; never overwrite it. Show the user the resulting diff: it changes what the agent may do without asking.
- Project settings are shared with the team. Anything personal goes in `.claude/settings.local.json` instead.

## Gotchas

- `settings.json` is read at session start; hooks and permissions added now take effect in a new session (or after `/hooks` review).
- A hook's `matcher` picks the tool (`Edit|Write`). Its `if` narrows by file with a single permission-rule expression (`Edit(*.ts)`, `Edit(**/src/**)`); no `&&`/`||`, so use one hook entry per file type that needs a different tool.
- The hook receives the tool call as JSON on stdin, with the edited path at `tool_input.file_path`. File-scoped formatting therefore needs a small repo script that reads it; if the tool can't take a file, run it repo-wide only when it's fast.
- Call the repo's own script (whatever runner it uses) rather than a shell one-liner, so the hook works on Windows, macOS and Linux. A bare command runs under bash, or PowerShell on Windows without Git Bash; pin one with `"shell": "bash"` or `"shell": "powershell"`.
- Exit 2 shows stderr to the agent, after the edit has already happened; that is how a failing lint or type check gets the agent to fix it. `"onFailure": "block"` makes the other failures do the same: a hook that fails to start, times out, or exits with any other non-zero code.
- Quote `${CLAUDE_PROJECT_DIR}` when referencing a script in the repo.
- A hook that takes more than a few seconds on every edit belongs in the verification skill instead.

## Finish

Summarize what was created, what was already fine, and what's left for the user (the run skill if you couldn't generate it, committing the files).
