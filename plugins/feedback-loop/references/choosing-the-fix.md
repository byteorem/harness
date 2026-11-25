# Choosing the fix

A correction usually carries a principle. Name it and check whether other places break the same way, so the fix covers the class, not just the line the user pointed at.

Put the fix at the earliest point that could have prevented the failure, in the strongest owner that fits:

- **A check or tool**: when the rule is mechanical, a lint, test, hook or permission rule that blocks it, or a script that makes the right way the easy way. Then don't also write it as prose.
- **The skill in use**: a gotcha at the point it matters, or a sharper description when the skill failed to load.
- **A CLAUDE.md line**: last, for what every session in that scope needs.

A fix that has to be prose quotes the real failure from the transcript as its bad example, next to the good one. Pick the narrowest scope it applies to: project, user, or a plugin.

Read the target before proposing the fix, not only before editing it, so the proposal extends what is there. A rule already written there that didn't hold needs a stronger owner, not a second copy. When a line looks stale, settle it from the project and state which is true; don't hand the question to the user.

When a new check makes a line redundant, or the session showed a line is stale, propose removing it.

Installed plugins live in `~/.claude/plugins/cache/` and are overwritten on update. Fix a plugin's skill in its source repo; if you can't find it, say so instead of editing the cache.
