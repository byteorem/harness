---
name: verification-skill
description: Use when creating a repo's verification skill (`.claude/skills/verify/`), or when an existing one is stale or misled an agent.
---

# Verification skill

Goal: a skill, at `.claude/skills/verify/` in the repo, that lets a fresh agent check a change works the way a user would see it, without asking anyone, and report what ran, the evidence, and what wasn't proven. The name is fixed: Claude Code runs a project skill named `verify` before each commit and uses it in place of its built-in `/verify`. Its description is a trigger every session in the repo reads: name the real areas and entry point, scoped to changes in behavior. When a skill already exists, including one the built-in `/verify` recorded, the same goal applies: keep it true to the repo as it is now, whether it failed during real work, the project changed, or it is just due a check.

## What it contains

Work out the repo from its code, config and run skill; ask the user only for what you can't find. If the checkout doesn't build or start, fix that or tell the user before writing a skill around it.

- How far a check goes. The skill runs before each commit, so it tells the agent to check only the areas the change can reach, and that a change no user could notice needs no check.
- The user-facing surface. When something has to be running: how to start it (reuse the repo's run skill), how to tell it's ready, and how to stop it.
- How to drive it through the normal entry points (CLI, UI, API), not internals. Passing tests are the entry bar; the proof comes from the running product. Describe the goal and the checks, not a keystroke script.
- What evidence shows success, and what would look right but be wrong. Evidence is output, status codes, screenshots, file contents or log lines, saved to a temp or ignored path that survives cleanup; in the repo tree it gets committed by accident.
- What can't be verified here (stand-in environment, missing credentials, unreachable system), so the report can say so.
- Whether two instances can run at once, and the shared state (ports, databases, files) involved: parallel agents collide on a fixed port or a shared database.
- Side effects to check or avoid. No pushes, publishes, external sends or writes to real shared systems while verifying; use local or disposable stand-ins.
- Gotchas under their own heading, each one a failure you have seen.

Script what every run repeats (starting, waiting for ready, seeding data, stopping) so the agent spends the run on the check. Write the scripts in the repo's own scripting language, working on every OS its contributors use, and list each in SKILL.md with its command.

Keep SKILL.md a router. When there are several areas, list each with the code it covers, including couplings a diff doesn't show (a shared module that reaches every area), and put the per-area detail in `features/<area>.md` files. Cover the areas users reach most and name the rest as unmapped.

## One skill or several

Start with `verify` alone; a repo whose only verification skill has another name gets it renamed. Split an area into its own `verify-<area>` skill only when it verifies differently: a different way to start it, a different driver (browser vs terminal vs HTTP), different evidence, or different setup data. Areas that differ only by screen or command stay as feature files, and a skill being long is not a reason to split. After a split, point `verify` at the new skill.

## Keeping it true

Edit only the skill's own directory. Re-check each claim against the repo as it is now: commands, paths, ports, files and flags. Drop what no longer exists, add new entry points users reach, and remove gotchas that no longer occur and steps the agent would do anyway; a smaller accurate skill beats a long stale one. When fixing a skill that misled an agent, start with that failure as evidence.

Triage what a run turns up:

- The doc was wrong: fix the skill.
- The skill lacked something it needed (a readiness wait, seed data, a gotcha): add it.
- The product is broken: report it to the user; don't fix it here and leave it out of the skill.

## Prove it

Run the skill end to end once on one real feature (for upkeep, each mapped area at least once): launch, drive, capture evidence, clean up. Starting the app locally, running its tests and writing evidence to a temp path need no approval. Afterwards the evidence is still there and nothing of yours is left running. Fix the skill where the run showed it was wrong, and leave anything you could only check in a stand-in environment marked unverified.

Finish by telling the user what changed or was created and which area was proven. If you couldn't finish, say what blocked it (no credentials, the app won't start).

## Gotchas

- Stopping by process name kills the user's and other agents' processes too. The skill says how to stop what it started, by PID or handle.
