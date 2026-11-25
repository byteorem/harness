# Intake workflow

Triggered when the user says "run intake" (optionally naming a channel, e.g. "run intake on email").

Intake pulls new messages from the channels in `channels.md` and decides what each one means for the tracked repos. It proposes actions in one batch, and acts only after the user approves.

## Files

- `channels.md`: which channels to pull, which folders or conversations, and what to ignore.
- `intake/ledger.jsonl`: one line per processed message, in the format below. It's how intake knows what it has already seen. Append only, through `scripts/ledger.py`.

```json
{"channel":"email","msg_id":"...","thread_id":"...","received":"2026-11-24T14:02:00Z","from":"...","subject":"...","action":"new|update|gate|reply-needed|skip","target":"<repo>:<bead-id>|inbox:<id>|null","processed":"2026-11-24T15:10:00Z"}
```

## The ledger script

All ledger reads and writes go through the script. The default ledger is `intake/ledger.jsonl`; `--ledger <path>` overrides it.

- `uv run --script scripts/ledger.py seen --channel <c>` prints the known `msg_id`s for a channel.
- `uv run --script scripts/ledger.py dedupe --channel <c>` reads messages (a JSON array or JSONL, each with `msg_id`) on stdin and prints the ones not yet in the ledger.
- `uv run --script scripts/ledger.py append` reads entries (a JSON array or JSONL) on stdin. Each entry has `channel`, `msg_id`, `thread_id`, `received`, `from`, `subject`, `action` (one of `new|update|gate|reply-needed|skip`) and `target`. `processed` is optional and defaults to now (UTC). It skips `(channel, msg_id)` pairs already in the ledger, so reruns are safe.

## Rules

- **Read-only on every channel.** Never send, reply, forward, flag, categorize, move, or mark read.
- Follow the standup rules in `CLAUDE.md`: never edit code in tracked repos, never claim beads.
- Nothing is written to any beads store until the user approves the batch.

## 1. Pull

For each channel in `channels.md`, or only the one the user named:

1. Set the window: the channel's `lookback` from `channels.md` (7 days unless set otherwise).
2. Fetch messages received inside the window, from the configured folders or conversations only, through that channel's MCP.
3. Drop messages already in the ledger (pipe the fetched messages through `ledger.py dedupe --channel <c>`) and messages matching the channel's ignore rules.
4. Group the rest by thread. Treat a thread as one item, judged by its latest message, but read the whole thread for context.

## 2. Match

For each thread, look for an existing bead before treating it as new. Go in this order and stop at the first hit:

1. **Thread already known:** a bead or gate in any tracked repo, or in the inbox, has metadata `thread_id` equal to this thread. Check with `bd -C <path> list --all --include-gates --metadata-field thread_id=<id> -n 0 --json` (for the inbox, drop `-C <path>`). Without `--include-gates` the lookup misses gates, and without `--all` it misses closed beads. Ignore beads closed more than 30 days ago (`closed_at`).
2. **Wait gate match:** an open gate with `wait:email` whose `to` and `subject` match this sender and thread. List gates with `bd -C <path> gate list --json`.
3. **Reference match:** a ticket number, PR number, bead ID or subject line in the message matches a bead's `external-ref`, title or description.
4. **Possible wait match:** none of the above, but the content looks like an answer to an open wait gate, for example the same request answered by a different person or in a new thread. Propose it as `gate` marked `?`, naming the gate. Never resolve on this alone. If the user confirms, also set `thread_id` on the gate so later replies match directly.
5. **Repo match only:** no bead matches, but the content routes to a repo using `repos.md`.
6. **No match.**

## 3. Classify

| Action | When | What gets proposed |
| --- | --- | --- |
| `gate` | The message answers a wait gate (approval granted, confirmation, "done on our side") | Resolve that gate, and add a note to the blocked bead with the summary |
| `update` | New info about an existing bead (new details, changed priority, "any update?", a related error) | `--append-notes` on that bead. Also propose a priority bump if the message signals urgency |
| `new` | A new ask, bug report or request for work | A new root bead in the matched repo (same create command as triage), or in the inbox if no repo fits |
| `reply-needed` | Someone is waiting on the user personally and it isn't repo work (a question, a meeting ask) | Nothing written. It's listed for the user |
| `skip` | FYI, newsletters, automated notices with nothing to act on | Nothing written. It's logged to the ledger |

When unsure between two actions, or two repos or beads, mark the item `?` and ask. Don't guess.

## 4. Propose

Show one table and wait for approval:

| # | From / subject | Action | Target | What I'll do |
| --- | --- | --- | --- | --- |
| 1 | J. Smith / "Access request REQ-1234" | gate | billing-api:ba-12 (gate ba-12.g1) | Resolve gate; note "approved 11/24" |
| 2 | Ops / "Nightly export failing again" | update | reports:rp-7 | Append note with new error + timestamp |
| 3 | M. Lee / "Can we add a CSV download?" | new | reports | Create feature bead, p2 |
| 4 | Team lead / "Sync Thursday?" | reply-needed | — | — |
| 5 | 3 automated notices | skip | — | — |

The user may approve all, approve by number, or edit (e.g. "3 goes to billing-api, p1").

If the user corrects a route, also propose an edit to that repo's **Route here** or **Not here** line in `repos.md`, and make it only after the user approves.

## 5. Act

For each approved item:

- **gate**:
  1. `bd -C <path> gate resolve <gate-id>`
  2. `bd -C <path> update <blocked-id> --append-notes "<date> via email from <sender>: <one-line summary>"`
- **update**:
  - `bd -C <path> update <id> --append-notes "<date> via email from <sender>: <summary>"`
- **new**:
  1. `bd -C <path> create ... -l triaged,from:email --external-ref "<sender>: <subject>" --json`
  2. `bd -C <path> update <new-id> --set-metadata thread_id=<thread_id> --set-metadata source=email`

Tagging the bead with the thread lets later replies in the same thread match it directly.

Then append every processed message to the ledger with `ledger.py append`, including `skip` and `reply-needed` items and items the user rejected (with `"action":"skip"`). Don't append messages the user deferred ("leave 4 for now"). They stay inside the lookback window, so they come up again every run until the user handles them or they age out of the window.

## 6. Report

```
Intake (email, 23 msgs → 9 threads)
  Gates cleared: 1   Updated: 2   Created: 1   Inbox: 0
  Reply needed:
    - Team lead: "Sync Thursday?"
```
