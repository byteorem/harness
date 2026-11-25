# Intake channels

Intake pulls only from the channels listed here, read-only, through each channel's MCP. To add a channel later (Slack, Teams), copy a block and fill it in. The `slack` block is commented out until that channel is added.

### email

- **MCP:** <name of the Outlook MCP server>
- **Pull from:** Inbox<, other folders>
- **Lookback:** 7 days
- **Ignore:**
  - Senders: <no-reply@..., newsletters, HR blasts>
  - Subjects containing: <"[Automated]", "Out of Office">
- **Always surface:** <key people or teams whose mail should never be skipped>

<!--
### slack
- **MCP:** <name>
- **Pull from:** <channels / DMs>
- **Lookback:** 3 days
- **Ignore:** <bots, channels>
-->
