---
name: skills
description: The user's house conventions for writing agent skills. Use alongside the agent's built-in skill-creation skill or workflow whenever creating, editing, or reviewing a skill (a SKILL.md and its directory). Adds conventions; does not replace that workflow.
---

Load these conventions alongside the agent's own skill-creation workflow, not instead of it. That workflow covers the process and the format; these add the house rules, and where the two conflict, these win. If two of these conventions pull against each other for the task at hand, tell the user rather than quietly picking one, so the conflict gets fixed here.

## Every skill

- **Scope it to one job.** Scope a skill like a function: one coherent unit of work that composes well with other skills. Too narrow, and a single task needs several skills loaded at once, adding overhead and conflicting instructions. Too broad, and the description can't say precisely when to use it. Querying a database and formatting the results is one job; adding database administration makes it two.
- **Don't state the obvious.** The agent already knows how to code and can read the codebase. A skill that restates what it would do by default costs context and adds nothing. The best skills encode opinions, knowledge, and practices particular to the user, their team, or their product: house taste, local decisions, and knowledge the agent could not infer. Test each instruction by asking whether the agent would get it wrong without it; if not, cut it.
- **Keep the root clean.** `SKILL.md` is the only file at the skill's root. Everything else goes in a subdirectory: `scripts/`, `references/`, `assets/`, or another named for what it holds.
- **Start small, and add structure when a run calls for it.** A new skill is a description and the few lines the agent would get wrong without them. Gotchas, templates, scripts, reference splits and saved config each answer a need: one a real run exposed (the agent tripped, drifted from a required shape, rebuilt the same logic, or the file outgrew one read), or one the task makes plain from the start, such as a destructive batch operation. Don't write them ahead of that need; a guessed gotcha is noise the agent still reads on every run.

## When to read more

Read a file when its row applies to the skill as it stands, not to what it might need later.

| When | Read |
|---|---|
| Writing or reviewing a description | `references/descriptions.md` |
| Deciding whether the agent or only the user can invoke the skill | `references/invocation.md` |
| Writing or reviewing the skill's instructions | `references/calibrate-control.md` |
| The agent tripped on something while using the skill | `references/gotchas.md` |
| Output must match a required shape, the agent skips steps that gate each other, or the skill does batch or destructive operations | `references/instruction-patterns.md` |
| `SKILL.md` has grown long, has several workflows, or carries material only some runs need | `references/progressive-disclosure.md` |
| The skill needs config from the user or keeps state between runs | `references/setup-and-state.md` |
| The skill runs commands, ships scripts, or the agent keeps rebuilding the same logic | `references/scripts.md` |
