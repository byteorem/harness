# Tracked repos

The standup agent reads this file to know which repos exist and where tasks go. Keep the routing hints specific: name the systems, features, teams and kinds of request that belong in each repo.

Format: one `### <repo-name>` heading per repo, followed by a `- **Path:**` line with the repo's path in backticks (`~` is expanded). The report script reads only those two lines; the rest are notes for the agent. Anything inside an HTML comment is ignored, so the example below lists no repo.

<!--
### <repo-name>

- **Path:** `~/code/<repo-name>`
- **What it is:** <one line: the app or service and who uses it>
- **Route here:** <features, components, error names, requesters, kinds of ask>
- **Not here:** <things people confuse with it and where they actually go>
-->
