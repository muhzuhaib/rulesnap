import json
from pathlib import Path

import pytest

from rulesnap.core import InputError, diff, load_snapshot, normalize_rulesets


def ruleset(**overrides: object) -> dict[str, object]:
    base: dict[str, object] = {
        "id": 7,
        "source": "octo/demo",
        "name": "main protection",
        "enforcement": "active",
        "conditions": {"ref_name": {"include": ["refs/heads/main"], "exclude": []}},
        "rules": [{"type": "pull_request", "parameters": {"required_approving_review_count": 1}}],
        "bypass_actors": [],
    }
    base.update(overrides)
    return base


def snapshot(*items: dict[str, object]) -> dict[str, object]:
    return normalize_rulesets("octo/demo", items)


def test_reports_enforcement_rule_target_and_bypass_regressions() -> None:
    old = snapshot(ruleset())
    new = snapshot(ruleset(
        enforcement="evaluate",
        conditions={"ref_name": {"include": ["~ALL"], "exclude": []}},
        rules=[],
        bypass_actors=[{"actor_id": 1, "actor_type": "User", "bypass_mode": "always"}],
    ))

    findings = diff(old, new)

    assert [finding["code"] for finding in findings] == ["RUL001", "RUL002", "RUL003", "RUL004"]


def test_reports_removed_active_ruleset() -> None:
    assert diff(snapshot(ruleset()), snapshot()) == [{
        "code": "RUL005", "severity": "error", "ruleset": "octo/demo#7", "message": "An active ruleset was removed.",
    }]


def test_ignores_metadata_and_normalizes_order() -> None:
    first = snapshot(ruleset(created_at="yesterday", rules=[{"type": "a"}, {"type": "b"}]))
    second = snapshot(ruleset(updated_at="today", rules=[{"type": "b"}, {"type": "a"}]))

    assert diff(first, second) == []


def test_rejects_invalid_snapshot(tmp_path: Path) -> None:
    path = tmp_path / "bad.json"
    path.write_text(json.dumps({"schema_version": 2, "repository": "octo/demo", "rulesets": []}), encoding="utf-8")

    with pytest.raises(InputError, match="schema_version 1"):
        load_snapshot(path)
