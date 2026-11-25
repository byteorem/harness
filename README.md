# harness

Claude Code plugins for getting more out of coding agents. Each one comes from a pattern that held up in practice, and the set keeps changing as new ones prove out.

## Design principles

The patterns every plugin here follows.

| Principle | In short |
| --- | --- |
| Fix the environment, not the prompt | When the agent struggles, add the missing context, tool or check instead of re-prompting or doing it by hand |
| Narrowest scope | Capabilities, permissions and boundaries live only where they're needed |
| Assume capable models | State intent and the finish line, then let the agent use judgment |
| Context is scarce | Load only what's needed, when it's needed |
| Composable capabilities | Each capability can be added, swapped or removed on its own. Plugins depend on contracts, never on each other |
| Less hand-holding | Having to hand-hold the agent means it's missing a capability. Add it, so you only step in at boundaries |
| Quiet where it doesn't apply | A plugin installed everywhere triggers and acts only where it applies, and stays silent elsewhere |

## Plugins

Each plugin is installed where it's needed and can be added, swapped or removed on its own.

| Plugin | What it does |
| --- | --- |
| [feedback-loop](plugins/feedback-loop/README.md) | Reviews past sessions for where the agent struggled, was corrected or needed things handed to it, and proposes the environment fix for each: a check, script, skill or CLAUDE.md change. Runs only when you invoke it |
| [conventions](plugins/conventions/README.md) | House conventions for building what an agent reads: how to write a skill, and how to design skills, agent definitions, commands, hooks and prompts for a capable model |
| [repo](plugins/repo/README.md) | Makes a repo legible: generates a short CLAUDE.md, run and verification skills, hooks and permission guidance, in the repo or kept local |

## Install

```sh
claude plugin marketplace add byteorem/harness
claude plugin install feedback-loop@harness --scope user
claude plugin install conventions@harness --scope user
claude plugin install repo@harness --scope user
```

## Layout

```
.claude-plugin/
  marketplace.json
plugins/
  feedback-loop/
  conventions/
  repo/
CLAUDE.md
```

## License

MIT
