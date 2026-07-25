# Rulesnap

Rulesnap makes GitHub repository ruleset changes reviewable. It captures a normalized, portable snapshot through your authenticated GitHub CLI, then compares snapshots locally and flags security- or governance-relevant changes.

It is deliberately read-only: Rulesnap never creates, updates, deletes, or applies a ruleset.

## What v0.1 detects

- an active ruleset changed to `evaluate` or disabled (`RUL001`);
- a rule removed from an active ruleset (`RUL002`);
- broadened branch/tag targets (`RUL003`);
- a new bypass actor or changed bypass mode (`RUL004`);
- an active ruleset removed entirely (`RUL005`).

## Quick start

```powershell
python -m pip install -e ".[dev]"
rulesnap capture OWNER/REPO --output .github/ruleset-snapshot.json
rulesnap diff .github/ruleset-snapshot.json candidate-ruleset-snapshot.json
```

`capture` uses the authenticated `gh` CLI, so sign in first with `gh auth login`. `diff` is fully offline and returns exit status 1 when it finds a risk-classified change. Use `--format json` for CI.

Try the included example:

```powershell
rulesnap diff examples/before.json examples/after.json --format json
```

## Snapshot format

Snapshots contain schema version 1, the repository name, and normalized detailed rulesets. Volatile metadata such as URLs and timestamps is removed so harmless API changes do not create noise. Rulesets are identified by their GitHub source and ID.

## Why this exists

GitHub rulesets can protect branches, tags, and pushes, including policies inherited from an organization. The GitHub CLI can list and view those rulesets, but does not export or compare a configuration snapshot. Rulesnap fills that review/CI gap without becoming another configuration writer.

- [GitHub ruleset CLI](https://cli.github.com/manual/gh_ruleset)
- [GitHub REST API for repository rules](https://docs.github.com/en/rest/repos/rules)
- [About GitHub rulesets](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/about-rulesets)

## Development

```powershell
python -m pip install -e ".[dev]"
python -m pytest
python -m build
```
