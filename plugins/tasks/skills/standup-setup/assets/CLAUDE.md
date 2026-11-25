# Standup repo

This repo is a control room. It holds no application code. From here you:

1. **Report** what's in flight across every tracked repo's beads store.
2. **Triage**: turn the user's asks into beads in the right repo, to be picked up later in that repo.
3. **Intake**: pull new messages from email and other channels, match them to repos and beads, and route them. See `intake.md`.

The work itself never happens here. It happens in a session opened inside the target repo, which follows that repo's beads workflow.

## Files

- `repos.md`: the registry of tracked repos (name, path, what lives there, routing hints). It's the only source for which repos exist and where tasks go.
- `intake.md`, `channels.md`, `intake/ledger.jsonl`: the intake workflow, its channel config and its record of processed messages.
- `scripts/report.py`, `scripts/ledger.py`: the report and the ledger helpers. Run them with `uv run --script`.
- `.beads/`: this repo's own store, used as the **inbox** for tasks that don't belong to a tracked repo yet, or aren't repo work at all.

`CLAUDE.md`, `intake.md` and `scripts/` are rewritten when the user reruns the plugin's standup setup; keep your own notes in `repos.md` and `channels.md`.

## Hard rules

- **Never edit files in a tracked repo.** You can read code there to route or describe a task, but you don't change it.
- **What you may do in a tracked repo's store:**
  - Create beads.
  - Update, close or resolve gates only when the user explicitly asks, naming the bead, or approves it in a triage or intake table.
  - Never claim (`--claim`) or work a bead from here.
- **Read-only outside the repos.** Email, Slack and GitHub are for reading only. Never send, reply, react or comment.
- Always target a repo with `bd -C <path>` (`-C` is a global flag) using the path from `repos.md`. Never guess a path.

## 1. Report: "what are we working on?"

```bash
uv run --script scripts/report.py
```

For each repo in `repos.md` it runs the commands below against that repo's store, then this repo's own inbox, and prints the answer in the shape that follows. It only reads, caps each section and says "+N more", and reports a missing path or store inline for that repo. Use `--repo <name>` for one repo and `--json` for structured output.

```bash
bd -C <path> list --status in_progress --json
bd -C <path> ready --json
bd -C <path> gate list --json
bd -C <path> blocked --json
bd list --status open --json            # this repo's inbox
```

The report keeps it terse and skips empty sections:

```
<repo-name>
  In progress: <id> <title>
  Waiting:     <id> <title>, on <gate reason> (since <date>)
  Ready next:  <id> <title>
Inbox: <n> unrouted
```

- Lead with anything that changed or needs the user: a gate that looks cleared, or something waiting a long time.
- If the user asks about one repo or one task, run only the commands for that.
- `bd list` hides gates unless you pass `--include-gates` or `--type gate`.
- A gate on a parent or epic blocks all its children, so a long "Waiting" list under one epic usually means one gate.

### "Check my waits"

Only when the user asks:

1. For each repo, run `bd -C <path> gate check --dry-run` to report GitHub gates that would close.
2. For gates labeled `wait:email`, `wait:slack` or `wait:teams`, read that channel through its MCP, read-only. Look for replies from the gate's `to` metadata in its `subject` or thread since `sent`.
3. For every other open bead with a `thread_id` (`bd -C <path> list --has-metadata-key thread_id -n 0 --json`), read that thread, read-only, and look for messages newer than the last one noted on the bead.
4. Report what you found.
5. Resolve a gate (`bd -C <path> gate resolve <id>`) or add a note to a bead only after the user confirms.

## 2. Triage: "I've got some tasks"

The user may give tasks as a list, a ramble, or a pointer to an email or message to read.

1. **Split** the input into distinct tasks.
2. **Route** each task to a repo using `repos.md`. If more than one repo fits or none clearly fits, ask. Don't guess.
3. **Dedupe.** Check the target store with `bd -C <path> list -n 0 --json` (every bead that isn't closed). If a matching bead exists, propose adding a note to it instead of creating a new one.
4. **Confirm** by showing the user the plan in one table with the columns #, Task, Repo, Type, Priority and Notes, and wait for an OK. If the user corrects a route, also propose an edit to that repo's **Route here** or **Not here** line in `repos.md`, and make it only after the user approves.
5. **Create** each bead with the command below.
   - Add `--acceptance` only if the user said what "done" looks like.
   - If it's already blocked on something external, add the gate now (see Gates below).
6. **Report** one line per task: `created <id> in <repo>`.

```bash
bd -C <path> create "<title>" -t <bug|feature|task|chore> -p <0-4> \
  --description "<what and why, in plain terms>" \
  --external-ref "<ticket # / email subject / requester>" \
  -l triaged --json
```

### Gates

Model each external wait as its own gate on the new bead, with `bd -C <path> gate create --type=human --blocks <id> --title "<what is awaited, from whom>" --reason "<what + any ticket #>"`.

- Always pass `--title`: the reason goes into the gate's description as `Reason: ...`, and the title defaults to `Gate: human`, which makes gate lists unreadable.
- `bd gate create` has no `--repo` flag, and `gh:run` / `gh:pr` gates only check the current repo. For another repo's run or PR, use a human gate that names it.
- When waiting on a reply, label the gate `wait:email`, `wait:slack` or `wait:teams`, and set metadata so the reply can be found: `bd -C <path> update <gate-id> --add-label wait:email --set-metadata to="<who>" --set-metadata subject="<subject>" --set-metadata sent="<YYYY-MM-DD>" --set-metadata thread_id="<id, when known>"` (`--set-metadata` repeats).

### Triage scope

- Create **one root bead per task**. Don't break it into subtasks here. Planning happens in the repo session, where the agent can read the code.
- Capture everything the user said and any source material, so the repo session doesn't have to re-ask.
- Use the **inbox** for tasks with no repo yet, or that aren't repo work (an access request, a meeting follow-up). Create them in this repo's store. When the user later says where an inbox task goes, create the bead in that repo, then close the inbox bead with `--reason "moved to <repo>:<id>"`.

## Adding a repo

When the user says "track `<repo>`":

1. Confirm the path exists and has `.beads/`. If it doesn't, tell the user to run `bd init` there. Don't run it yourself.
2. Ask what lives in it, so routing hints are useful.
3. Add the entry to `repos.md`.
