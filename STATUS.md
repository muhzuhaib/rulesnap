# Rulesnap status

- Status: published.
- Purpose: create reviewable GitHub ruleset snapshots and classify meaningful configuration changes offline.
- Current version: `v0.1.0`.
- Repository: https://github.com/muhzuhaib/rulesnap
- Release: https://github.com/muhzuhaib/rulesnap/releases/tag/v0.1.0
- Scope: explicit read-only capture through `gh api`, plus offline semantic diffs of normalized snapshots.
- Verification: 6 automated tests passed on Python 3.14.4; source and wheel distributions built and inspected; a read-only live capture of `muhzuhaib/checklock` completed successfully (0 rulesets). The public release contains both artifacts, and its initial CI runs passed: https://github.com/muhzuhaib/rulesnap/actions/runs/30174759593
- Local Git: `v0.1.0` points to `4ac121c` and matches the public tag.
- Next: maintain issues and release follow-up fixes as needed.
