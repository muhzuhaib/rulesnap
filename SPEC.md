# Rulesnap v0.1 specification

## Goal

Make GitHub repository ruleset changes reviewable without modifying GitHub configuration.

## Commands

1. `rulesnap capture OWNER/REPO --output rules.json`: read repository rulesets through `gh api`, normalize them, and write a snapshot.
2. `rulesnap diff OLD.json NEW.json`: compare normalized snapshots and emit findings in text or JSON.

## Findings

| Code | Meaning | Severity |
| --- | --- | --- |
| `RUL001` | A ruleset changed from active to evaluate/disabled. | error |
| `RUL002` | A rule was removed from an active ruleset. | warning |
| `RUL003` | The target refs broadened. | warning |
| `RUL004` | A bypass actor was added or its bypass mode weakened. | warning |
| `RUL005` | An active ruleset was removed. | error |

## Non-goals

- Creating, modifying, or deleting rulesets.
- Applying a snapshot to GitHub.
- Accessing GitHub directly without an explicit `capture` command.
- Replacing organization policy management or infrastructure-as-code.

## Exit codes

- `0`: no findings.
- `1`: one or more findings.
- `2`: invalid command input, snapshot, or `gh` capture failure.
