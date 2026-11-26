# Writing hooks

Facts about hooks in `.claude/settings.json` that the repo's files won't show.

- `settings.json` is read at session start; hooks and permissions added now take effect in a new session (or after `/hooks` review).
- A hook's `matcher` picks the tool (`Edit|Write`). Its `if` narrows by file with a single permission-rule expression (`Edit(*.ts)`, `Edit(**/src/**)`); no `&&`/`||`, so use one hook entry per file type that needs a different tool.
- The hook receives the tool call as JSON on stdin, with the edited path at `tool_input.file_path`. File-scoped formatting therefore needs a small repo script that reads it; if the tool can't take a file, run it repo-wide only when it's fast.
- Call the repo's own script (whatever runner it uses) rather than a shell one-liner, so the hook works on Windows, macOS and Linux. A bare command runs under bash, or PowerShell on Windows without Git Bash; pin one with `"shell": "bash"` or `"shell": "powershell"`.
- Exit 2 shows stderr to the agent, after the edit has already happened; that is how a failing lint or type check gets the agent to fix it. `"onFailure": "block"` makes the other failures do the same: a hook that fails to start, times out, or exits with any other non-zero code.
- Quote `${CLAUDE_PROJECT_DIR}` when referencing a script in the repo.
- A hook that takes more than a few seconds on every edit belongs in the verification skill instead.
