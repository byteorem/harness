---
name: local-only
description: Use when the user wants agent config in a repo (CLAUDE.md, AGENTS.md, skills, hooks, settings, MCP servers) kept on their machine and out of commits, such as a repo they don't own, a team that doesn't use agents, or upstream code, or says not to commit agent stuff.
---

# Local-only agent config

Goal: the agent gets the full setup it would have in an agent-friendly repo (map, skills, hooks, permissions, MCP servers), and nothing agent-related reaches the repo's history, its tracked files, or a pushed branch. The test at the end: `git status` shows nothing agent-related, and every agent file is excluded through `.git/info/exclude` (or the global excludes file), so the repo's own files, `.gitignore` included, are unchanged.

Making the changes below needs no approval; they touch only untracked, per-clone state. Ask before editing or untracking a file the repo already tracks.

## Where each piece goes

| Piece | Local-only home |
| --- | --- |
| Map | `CLAUDE.md` (and `AGENTS.md` for other agents) at the root, excluded. If the repo already tracks one, put additions in `CLAUDE.local.md`, excluded, which loads alongside it |
| Skills, agents, commands | `.claude/skills/` and the rest under `.claude/`, excluded |
| Hooks, permissions, env | `.claude/settings.local.json`, never `.claude/settings.json` |
| Plugins | `claude plugin install <plugin> --scope local`, which records it in `settings.local.json`. Project scope writes the shared `settings.json` |
| MCP servers | `claude mcp add --scope local` (the default), stored in the user's `~/.claude.json` for this path. Project scope writes `.mcp.json` |
| Helper scripts | Under `.claude/` with the rest, so one exclude covers them |

## Excluding without touching the repo

Exclude with `.git/info/exclude`, which works like `.gitignore` but is never committed. Don't add entries to `.gitignore`: it is tracked, so the edit itself is agent stuff in the diff. Exclude the whole `.claude/` directory only if the repo tracks nothing under it; otherwise list the local paths one by one.

When the user wants this in every repo they touch, the global excludes file (`git config --global core.excludesFile`) is the place instead; ask before changing global git config.

Confirm with `git check-ignore -v <path>` that each file is excluded and that the matching rule comes from `info/exclude` or the global file, not a `.gitignore`.

## Commits and PRs

The agent's commits and PR bodies are agent stuff too: Claude Code adds a `Co-Authored-By` trailer and a "Generated with Claude Code" line by default. If the user wants no trace, set `"attribution": false` in `settings.local.json` (older Claude Code versions need `"attribution": {"commit": "", "pr": ""}`). Ask, since some users want attribution even when the config stays private.

Stage by path or with `git add -A`; never `git add -f` an excluded path.

## Gotchas

- Exclude rules don't apply to files git already tracks. A tracked `CLAUDE.md` or `.claude/settings.json` stays tracked; edit it only if the user wants that change committed, and put private additions in the `.local` variants.
- Nothing excludes `CLAUDE.local.md` for you, despite the name; exclude it like the rest. Claude Code does exclude `.claude/settings.local.json` when it writes it, via the global git excludes file, but not when the file is created by hand.
- A `CLAUDE.local.md` stops `AGENTS.md` from loading by default. If the repo relies on a tracked `AGENTS.md`, set "Project instructions" to `claude-md-and-agents-md` in `/config`.
- Untracked files don't follow into new worktrees, so an agent in a fresh worktree starts with no map or skills. `.git/info/exclude` is shared across worktrees, but the files aren't. List them in a `.worktreeinclude` at the repo root (excluded too) so Claude Code copies them into worktrees it creates; other worktrees need them copied by hand.
- A fresh clone loses everything here. If the user works across machines, keep the config somewhere they back up and copy or link it in.

## Finish

Tell the user what went where, that `git status` is clean of agent files, and anything that couldn't stay local (an already-tracked agent file they chose to keep editing).
