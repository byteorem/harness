# harness

A Claude Code plugin marketplace: plugins for working with coding agents. The root `README.md` states the design principles every plugin follows; read them before designing or reshaping a plugin.

## Layout

- `.claude-plugin/marketplace.json` lists every plugin. Each entry's `source` points at `./plugins/<name>`.
- `plugins/<name>/README.md` explains the plugin; the root `README.md` lists each plugin with its tagline and links there.
- `plugins/<name>/.claude-plugin/plugin.json` is the plugin manifest. Skills, agents, commands, and hooks go in `skills/`, `agents/`, `commands/`, and `hooks/` at the plugin root, not inside `.claude-plugin/`.

## Install scope

Each plugin starts at the narrowest scope that covers where it applies, and its README's Install section says which. A plugin meant for user scope loads in every session, so its skills trigger and its hooks act only where they apply, and stay silent elsewhere.

## Designing for capable agents

Assume the agent that runs a plugin is very capable, and design for that: state intent and the finish line, and leave out what it would do anyway. Before writing or reshaping anything a plugin's agent reads (a skill, agent definition, command, hook output, or tool description), load the `conventions:capable-agents` skill from this repo's `conventions` plugin.

## Hooks and scripts

Hooks and helper scripts are single-file Python, run as `uv run --script "${CLAUDE_PLUGIN_ROOT}/..."`. A hook's output lands in every session's context, so it prints nothing where it doesn't apply (no config, no store).

## Rules

- Plugin names are kebab-case.
- Keep `name` and `description` in a plugin's `plugin.json` and its marketplace entry in sync. When the description changes, update the plugin's tagline in the root README too.
- Leave plugin and marketplace versions alone: nothing is released yet.
- Run `claude plugin validate .` and `claude plugin validate plugins/<name>` before committing.
