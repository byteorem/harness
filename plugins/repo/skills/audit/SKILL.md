---
name: audit
description: Use when the user asks to audit, set up, onboard or refresh a repo for agents. Judges the repo against an agent-readiness target, fixes the agent-layer gaps and proposes the rest.
disable-model-invocation: true
---

# Repo audit

Goal: an agent opening the repo can understand it, start it, and check its own changes, with every piece living in the repo (never in the harness). The audit is done when each pillar below is judged, the agent-layer gaps are fixed, and the repo-side gaps are listed for the user.

## The target

What a repo has when an agent can take a change from request to proof on its own, with a person stepping in only at the boundaries. Built on Factory's [agent readiness](https://docs.factory.com/agent-readiness/overview) model, without the scoring. Judge each pillar against the levels, report what's missing, and treat the next level up as that pillar's goal. Skip what doesn't apply to the repo.

### Levels

| Level | What it means | Example criteria |
| --- | --- | --- |
| 1. Functional | The code runs, but setup is manual and validation isn't automated | README, linter, type checker, unit tests |
| 2. Documented | Basic docs and processes exist, with some automation | AGENTS.md, env template or devcontainer, pre-commit or edit hooks, agent permissions, branch protection |
| 3. Standardized | Processes are defined, documented and enforced by automation | Integration tests, run and verify skills, CI enforcing checks, secret scanning, tracing and metrics |
| 4. Optimized | Feedback is fast, and improvement is measured | Fast CI, frequent deploys, flaky test detection, preview environments |
| 5. Autonomous | The repo improves itself | The agent's struggles become fixes in the repo as they surface |

### Pillars

| Pillar | What it gives the agent | Examples |
| --- | --- | --- |
| Style & Validation | Mistakes caught before a person sees them | Linter, type checker, formatter, hooks that run them on change |
| Build System | A build it can run before committing, with the same result every time | Documented build command, pinned dependencies, the host's CLI (`gh`) |
| Testing | A tight loop, then proof | Unit and integration tests, runnable locally and one file at a time, a verify skill |
| Documentation | What it can't see in the code | README, an `AGENTS.md` map (see The map), kept current |
| Development Environment | A fresh clone that reaches a running app without a person | Env template, pinned toolchain, local services, a run skill |
| Debugging & Observability | A way to see why something failed at runtime | Logs it can read, structured logging, tracing, metrics |
| Security | Guardrails against leaked secrets, unsafe actions and bypassed review | Agent permissions, branch protection, secret scanning, CODEOWNERS |
| Task Discovery | Work that arrives scoped and leaves in the accepted shape | Issue templates, labels, PR template |
| Product & Experimentation | A measure of a change's effect on users | Analytics, feature flags, experiments. Skip for libraries and tools |

### The map

Where we depart from Factory's AGENTS.md guidance: the map stays short and carries only what the code and config don't show, because anything discoverable costs context on every run and goes stale.

- `AGENTS.md` holds it; `CLAUDE.md` is the single line `See @AGENTS.md`. Under about 40 lines.
- In: purpose, rules with their reason, commands the agent couldn't guess, directories it would misread, generated files and the source to edit instead, actions that need approval. Pointers to the run and verify skills instead of their procedures.
- Out: full command lists, directory inventories, setup guides, style rules a linter enforces. Human onboarding stays in the README.

### Fixing gaps

- **Agent layer:** files only agents read: the map, skills, hooks, `.claude/settings.json`. Cheap and reversible, so create what's missing.
- **Repo:** changes to the project itself or its host. A project decision, so propose the change and make it only when the user picks it. Host settings are the user's to change.

## How a run goes

The audit is idempotent and safe to rerun: create only what's missing, and leave existing files alone unless the user asks. Ask only for what can't be discovered (for example which environment counts as safe to run against).

1. **Judge.** Check each pillar against the levels. Report per pillar, in a line or two, where it stands and what it is missing for the next level. No score.
2. **Fix the agent layer** directly:
   - Map: write it per The map. If `AGENTS.md` exists or gets created, `CLAUDE.md` is `See @AGENTS.md`. A stale existing map gets edits proposed as a diff, not regenerated.
   - Verification skill: create it with the `repo:verification-skill` skill.
   - Run skill: point the user to Claude Code's built-in `/run-skill-generator`, which is interactive and writes `.claude/skills/run-<name>/`. Skip it when the repo has no runnable app.
   - Hooks and permissions in `.claude/settings.json`:
     - Hooks: only for a tool the repo already uses (formatter, linter, type checker), running its fast, file-scoped command. Read [references/hooks.md](references/hooks.md) before writing one.
     - Permissions: allow the safe, repeatable workflows found (test, lint, build, read-only git). Keep push, publish, deploy, external sends, destructive git and secrets on ask or deny.
     - Merge into existing settings, never overwrite, and show the user the resulting diff: it changes what the agent may do without asking.
     - Project settings are shared with the team; personal rules go in `.claude/settings.local.json`.
3. **List the repo-side gaps**, each with the concrete change it needs. Make only the ones the user picks. Host settings such as branch protection and secret scanning are reported, never changed.
4. **Local only.** If the user doesn't want agent config committed, use the `repo:local-only` skill for where each piece goes.

Finish by summarizing what was created, what was already fine, and what is proposed or left for the user.
