# Rulesnap status

- Status: release-ready, awaiting public-upload approval.
- Purpose: create reviewable GitHub ruleset snapshots and classify meaningful configuration changes offline.
- Planned version: `v0.1.0`.
- Scope: explicit read-only capture through `gh api`, plus offline semantic diffs of normalized snapshots.
- Verification: 6 automated tests passed on Python 3.14.4; source and wheel distributions built and inspected; a read-only live capture of `muhzuhaib/checklock` completed successfully (0 rulesets).
- Local Git: initial release committed and tagged `v0.1.0`.
- Next: publish the public `muhzuhaib/rulesnap` repository and attach the verified release artifacts once explicit upload approval is provided.
