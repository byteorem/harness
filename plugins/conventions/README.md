# conventions

> House conventions for building what an agent reads: how to write a skill, and how to design skills, agent definitions, commands, hooks and prompts for a capable model.

The scope is the pieces of a harness an agent reads and acts on. Conventions for anything else (code style, commits, prose for people) belong elsewhere, so these skills load only for that work.

## Install

Install at user scope.

```sh
claude plugin install conventions@harness --scope user
```

## Skills

| Skill | What it does |
| --- | --- |
| `conventions:skills` | Loads alongside the agent's own skill-creation workflow when it creates, edits or reviews a skill. Adds the house rules: one job per skill, start small, nothing the agent would do anyway, `SKILL.md` alone at the root. Reference files cover descriptions, invocation, calibrating control, gotchas, instruction patterns, progressive disclosure, setup and state, and scripts; each is read only when it applies |
| `conventions:capable-agents` | Loads when the agent designs, writes, reshapes or reviews anything another agent reads. Guidance written to restrain weaker models overconstrains a capable one, so every line is tested by whether a capable agent would get it wrong without it. Covers what to write, what to build instead of writing, and what to drop, and hands off to `conventions:skills` when the thing is a skill |
