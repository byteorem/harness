---
name: capable-agents
description: Use when designing, writing, or reshaping anything an agent reads and acts on, such as a skill, agent definition, command, hook output, tool description, CLAUDE.md, or prompt, and when reviewing one for over-constraint.
---

# Designing for capable agents

Assume the agent that reads what you write is very capable: it has good judgment, reads its environment, and checks its own work. Guidance written to restrain weaker models overconstrains it. It narrows what the agent explores, makes it stop or test where it didn't need to, and spends context on things it already knew. Anthropic cut over 80% of Claude Code's system prompt with no measurable loss on its coding evals.

So the question for every line is whether a capable agent would get this wrong without it. If not, cut it.

## What to write

- **Goal, constraints, finish line.** State what the agent is achieving, what it must not break, and what done means. It works out the steps. Keep a fixed sequence only where the order matters and a wrong move is costly, and there be exact.
- **What it couldn't infer.** Gotchas taken from real failures are the highest-signal content a skill has; add one each time the agent trips. After that, opinions, knowledge, and practices specific to the user, their team, or the project. Leave out anything it knows already or can see in the files.
- **The judgment, not a rule.** "Match the surrounding code's comment density" does better than "write no comments": a blanket rule is wrong in the cases it didn't foresee. Say each thing once, where it's used, with no repetition or emphasis for effect.
- **Full scope and standing permission.** A capable agent leans cautious. It stops at a first pass or asks before a safe action unless told the scope runs further. Say which actions are safe to take without asking and how far the work goes.

## What to build instead of writing

- **Interfaces over examples.** An expressive parameter, an enum, or a script's arguments carry the behavior. Examples narrow the agent to what they show, so use one only when the shape can't be expressed another way.
- **Code over prose.** Ship scripts and helpers the agent composes instead of rebuilding, with the data gotchas in their docstrings. Give references as code, tests, or mockups; they're higher fidelity than a description of the same thing.
- **Hooks only when invoked, where they're heavy.** A guardrail too opinionated to run in every session can register from a skill and last for that session.

## When it's a skill

Load `conventions:skills` as well. It covers what is particular to a skill: scope, the description as a trigger, who can invoke it, progressive disclosure, and scripts.

## What to drop

These helped older models and now cost more than they return:

- Step-by-step recipes for work that tolerates variation.
- Prompts to run tests, verify, or double-check.
- "Ask first" boundaries that restrain the agent, not protect something. Keep the ones guarding hard-to-reverse actions.
- Stops for review mid-task that aren't a decision the user needs to make.
- The same instruction in two places.

When reshaping something that exists, audit what's already there against this list before adding anything.

## Sources

Read one when a decision here is open and the summary above doesn't settle it.

- [Lessons from building Claude Code: how we use skills](https://claude.dev/blog/lessons-from-building-claude-code-how-we-use-skills/): skill categories, gotchas, on-demand hooks, storing state and scripts.
- [The new rules of context engineering for Claude 5 generation models](https://claude.dev/blog/the-new-rules-of-context-engineering-for-claude-5-generation-models/): the old rule and its replacement, layer by layer.
- [Rethinking skills and prompts for GPT-6 Astra](https://developers.openai.com/blog/rethinking-skills-and-prompts-for-gpt-6-astra): descriptions, decision boundaries, and persistence.
