---
name: workflow
description: Use in a repo with a beads (bd) store when a request becomes tracked work: starting a request, planning it, executing it, waiting on something external (a CI run, a PR, a reply, an approval), pausing or ending a session, or resuming earlier work ("pick back up the X fix"). Also before acting on `bd prime` or `bd ready` output that suggests picking up work.
---

# Beads workflow

Beads (`bd`) is the task store for this repo. Use it as memory for work across sessions. It is not a queue to drain.

## Core rule: one focus per session

- A session works on the **focus**: the one root bead the user names or that you create for this session's request.
- Open, ready or blocked beads that aren't part of the focus are **not yours this session**. Don't claim, update, close or "tidy" them unless the user asks.
- `bd ready` and `bd prime` are for awareness. They are not a todo list for you. When those tools suggest picking up ready work, this skill takes precedence.

## 1. Intake (start of a request)

1. Look for an existing bead for this request: `bd list -n 0 --json` (every bead that isn't closed), then compare titles and descriptions.
   - If one matches, confirm with the user before resuming it, then `bd show <id>` and read its notes.
   - If none matches, create a new root bead.
2. Gather context as needed by asking the user, reading code or reading the linked email or ticket. Order doesn't matter, but record what you learn on the bead instead of only in chat:
   - `--description`: the problem, in plain terms
   - `--acceptance`: how we know it's done
   - `--external-ref`: ticket number, email subject or incident ID if there is one

```bash
bd create "Fix: <short title>" -t bug -p 2 \
  --description "..." --acceptance "..." --json
```

## 2. Plan: single bead or graph

- **Single bead** if it's one coherent change that fits in one session.
- **Epic with children** if it has distinct steps, more than one session of work, or any external wait. Turn the root into an epic and add children with `--parent <root>`. Order the children with `bd dep add <later> <earlier>`.
- Model each external wait as a gate (section 4), not as a vague "blocked" note.
- Show the user the graph (`bd dep tree <root> --direction=both`) before starting a large plan.

## 3. Execute

Loop until the focus is done or every remaining step is waiting:

1. Pick the next ready bead inside the focus's tree: `bd ready --parent <root>`. Ignore ready beads outside it.
2. `bd update <id> --claim`
3. Do the work.
4. `bd close <id> --reason "<what changed / commit / PR>"`
5. If you find unrelated or out-of-scope work, file it and don't do it: `bd create "..." --deps discovered-from:<id>`. Mention it to the user in one line.

**Permissions:** local and read-only work is free. Always ask before you open a PR, merge or deploy.

## 4. Waiting on something

Every external wait is a gate. Pick the kind by what you're waiting on. Always pass `--title "<what is awaited, from whom>"`, and gate the specific child step that waits, not the focus root.

### GitHub (read-only, beads checks these itself)

```bash
bd gate create --type=gh:run --blocks <id> --await-id=<run-id> --title "<run, what it proves>"   # Actions run
bd gate create --type=gh:pr  --blocks <id> --await-id=<pr#>    --title "<PR, who merges>"        # PR merge
```

- `bd gate check` calls `gh run view` / `gh pr view`. It never writes to GitHub.
- Find the run ID with `gh run list`.
- `bd gate create` has no `--repo` flag, so gh:run and gh:pr gates only check the current repo. For another repo's run or PR, use a human gate that names it (see below).
- A failed run doesn't close the gate. When you check, look at the run, and if it failed, tell the user.

### Waiting on a reply (email, Slack, Teams)

Use a `human` gate, then tag it so you know where to look for the reply:

```bash
bd gate create --type=human --blocks <id> \
  --title "<who> to confirm <what>" \
  --reason "Waiting on <who> to confirm <what>"
bd update <gate-id> --add-label wait:email \
  --set-metadata to="<person or team>" \
  --set-metadata subject="<subject line or thread link>" \
  --set-metadata sent="<YYYY-MM-DD>" \
  --set-metadata thread_id="<thread id, when known>"
```

- Use the label `wait:email`, `wait:slack` or `wait:teams`.
- To check: read that channel through its MCP, read-only. Find the thread by `thread_id` when set, otherwise by `subject`, and look for replies from `to` since `sent`.
- If you find a reply, summarize it for the user and ask before resolving. Never send, reply or react in the channel.
- If the channel has no MCP connected, ask the user.

### Anything else (a decision from the user, an approval with no channel to check, another repo's run or PR)

```bash
bd gate create --type=human --blocks <id> \
  --title "<what is awaited, from whom>" --reason "<what + any ticket # or owner/repo run or PR>"
```

### Rules

- Create one gate per thing you're waiting on. A gate is its own bead, so a task can have several, and it becomes ready only when all of them are closed.
- Only close a human gate with `bd gate resolve <gate-id>`, and only after the user confirms.
- For "not now" with no specific blocker, use `bd defer <id> --until "<date>" --reason "..."`.
- If every remaining step in the focus is gated, go to section 5. Don't wander to other beads.

## 5. Pause / end of session

Before you stop, whether done, blocked or out of time:

1. Append a handoff note to the root bead: `bd update <root> --append-notes "<date>: done X; next is Y; waiting on Z (gate <id>); key files: ..."`
2. Make sure every open child has a status that matches reality. Nothing should be left `in_progress` that isn't being worked on.
3. Sync per this repo's setup (`bd dolt push` if a remote is configured).
4. Tell the user in two or three lines: what's done, what's waiting and on what.

## 6. Resuming later

When the user says "pick back up the `<x>` fix":

1. `bd show <root>` and read the notes.
2. Run `bd gate check --type=gh` to close any GitHub gates that are met.
3. For the focus's open `wait:*` gates, check their channel as described in section 4.
4. Ask the user about the rest of the open gates.
5. Run `bd dep tree <root> --direction=both`.
6. Continue at section 3.

If the user starts an unrelated request instead, it's a new focus. Leave the old one exactly as it is.

## Gotchas

- A gate's `--reason` lands in its description as `Reason: ...`, and its title defaults to `Gate: human`. Without `--title`, every gate in `bd gate list` and `bd blocked` reads the same.
- A gate or any blocker on a parent or epic also blocks all its children; they show in `bd blocked` with `blocked_by` the parent. Gate the specific child step, not the focus root.
- `bd create --parent <root> --deps discovered-from:<root>` fails: the parent-child dependency already exists. Use one or the other.
- `bd list` hides gates unless you pass `--include-gates` or `--type gate`; `--has-metadata-key` hides them too. `bd list --all --include-gates --metadata-field thread_id=<id> -n 0 --json` returns gates and closed beads.
- `bd list -n 0` with no `--status` returns open, in_progress, blocked and deferred beads, not closed ones. Without `-n 0` the limit is 50. Add `--all` to include closed beads.
- `bd ready` leaves out in_progress beads. After a restart or compaction, look for claimed work in `bd list --status in_progress` first.
- In `bd dep add <id> <blocked-by>` the first id is the one that waits. It disappears from `bd ready` until the blocker closes, with no notice.
- A claimed bead stays in_progress behind a gate, so a restart takes it for work under way. `bd unclaim <id>` when you gate it.
- `bd search` matches titles only. Put a ticket number in `--external-ref`, and find it with `bd list --all --external-ref <ref>`; without `--all` a closed bead is missed and gets filed again.
- A `--parent` link groups only; the parent still shows in `bd ready` while children are open. Close it yourself once the children are closed and the whole is proven.
