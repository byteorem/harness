# repo

> Audits a repo for agent readiness and sets up what an agent needs to take a change from request to proof.

It judges a repo against an agent-readiness target, then writes what an agent needs into the target repo, not the harness, so it works for anyone who opens the repo, with or without this plugin. When the repo shouldn't carry agent config (someone else's repo, a team that doesn't use agents), the same pieces stay on your machine instead.

## Install

Install at user scope, so it's ready in any repo you open:

```sh
claude plugin install repo@harness --scope user
```

What audit writes works without the plugin, so repos and teammates don't need it installed. Outside a repo its skills don't trigger.

## Commands

| Command | What it does |
| --- | --- |
| `/repo:audit` | Judges the repo against the agent-readiness target, reports where each pillar stands, and fixes the agent-layer gaps. Safe to rerun. Only you run it |
| `/repo:verification-skill` | Creates a repo's verification skill, or maintains an existing one. Also used by the agent when a verification skill is missing or stale |
| `/repo:local-only` | Keeps a repo's agent config on your machine: excluded via `.git/info/exclude`, local-scope settings, plugins and MCP servers, and optionally no attribution in commits. Also used by the agent when you say not to commit agent stuff |

## Agent readiness

The target is what a repo has when an agent can take a change from request to proof on its own, with a person stepping in only at the boundaries. It is adapted from Factory's [agent readiness](https://docs.factory.com/agent-readiness/overview) model, without the scoring. Audit judges each pillar against the levels, reports what's missing for the next level, and skips pillars that don't apply.

| Level | What it means |
| --- | --- |
| 1. Functional | The code runs, but setup is manual and validation isn't automated |
| 2. Documented | Basic docs and processes exist, with some automation |
| 3. Standardized | Processes are defined, documented and enforced by automation |
| 4. Optimized | Feedback is fast, and improvement is measured |
| 5. Autonomous | The repo improves itself |

Pillars: Style & Validation, Build System, Testing, Documentation, Development Environment, Debugging & Observability, Security, Task Discovery, Product & Experimentation.

## What audit writes into a repo

| Piece | Where | Notes |
| --- | --- | --- |
| Map | `AGENTS.md`, `CLAUDE.md` | `AGENTS.md`, with `CLAUDE.md` as `See @AGENTS.md`. Short: what the repo is for, rules with their reason, commands the agent couldn't guess, pointers to skills. Nothing the agent can find in the code or config |
| Run skill | `.claude/skills/run-<name>/` | Made by Claude Code's built-in `/run-skill-generator`; audit points you to it rather than reimplementing it |
| Verification skill | `.claude/skills/verify/` | Named `verify` so Claude Code runs it before each commit, in place of its built-in `/verify`. One per repo to start. Split an area out only when it verifies differently (different launch, driver or evidence) |
| Hooks | `.claude/settings.json` | Format/lint on edit, only where the repo already has the tool |
| Permissions | `.claude/settings.json` | Allow rules for the repo's safe workflows |

Existing files are left alone: a stale map gets a proposed diff, and settings are merged, not overwritten, with the result shown to you.

## What audit only proposes

| Gap | Handling |
| --- | --- |
| Repo changes (tests, CI, env template, issue and PR templates, logging) | Listed with the concrete change each; made only when you pick them |
| Host settings (branch protection, secret scanning) | Reported; they're yours to change |


## Permissions

Allow the safe, repeatable workflows (tests, lint, build, read-only git) so the agent doesn't stop to ask. Boundaries stay on `ask` or `deny`: pushes, publishing, deploys, external sends, destructive git, and secret files. Each repo draws its own line. Personal rules go in `.claude/settings.local.json`, not the shared file.

## Verification and proof

A verification skill drives the project through its normal entry points and captures evidence that survives cleanup. Passing tests are the entry bar; the proof comes from the running product. The agent using it checks only the areas its change can reach and reports what ran, the evidence, and what wasn't proven.
