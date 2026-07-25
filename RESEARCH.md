# Rulesnap research record

Checked on 2026-07-26.

## Gap

GitHub rulesets protect branches, tags, and pushes. They may aggregate from parent organizations and their most restrictive settings apply. The GitHub CLI documents only `check`, `list`, and `view` commands for rulesets; it has no snapshot/export/diff command. GitHub's REST API returns detailed repository rulesets, while the ruleset-history endpoint requires Administration (write) access. A portable, normalized snapshot plus offline semantic diff supports review and CI while staying read-only.

## Scope decision

Rulesnap will call the authenticated `gh` CLI only for explicit capture. Diffing is entirely local. It will not create, update, delete, or apply GitHub configuration, and does not use an API key of its own.

## Sources

- GitHub CLI, `gh ruleset`: https://cli.github.com/manual/gh_ruleset
- GitHub REST API, repository rules: https://docs.github.com/en/rest/repos/rules
- GitHub Docs, ruleset behavior: https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/about-rulesets
- GitHub Docs, available rules: https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/available-rules-for-rulesets
