# feedback-loop

> Reviews past sessions for where the agent struggled, was corrected or needed things handed to it, and proposes the environment fix for each.

The feedback loop of the harness: read what happened in sessions, find what the agent lacked (context, a capability, permission or proof), and fix it in the environment so the next session starts better equipped. A mechanical rule becomes a check or script, not another line of prose.

## Install

Install at user scope.

```sh
claude plugin install feedback-loop@harness --scope user
```

## Skill

`/feedback-loop:reflect [which sessions]` reviews this session or named past ones. It reports each lesson with its evidence and the proposed fix (a check, hook, script, skill or CLAUDE.md change, or removing a stale line), then applies the ones you pick. Only you can run it.

It chooses fixes as `references/choosing-the-fix.md` says: a check or script over prose, at the earliest point that could have prevented the failure.

For past sessions, reflect writes a throwaway counter for struggle signals per model (error rates, process kills, writes outside the project, retries, rejections, interrupts, corrections) against the transcripts as they are, then reads only the flagged slices. `scripts/sessions.py` finds the project's sessions, worktrees included.

For a periodic deep audit, run it once from a different model too: each catches things the others miss.
