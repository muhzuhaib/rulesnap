from __future__ import annotations

import json
import subprocess
from collections.abc import Iterable, Mapping
from pathlib import Path
from typing import Any


class InputError(ValueError):
    """Raised when a snapshot or capture cannot be safely processed."""


_IGNORED_KEYS = {"_links", "created_at", "updated_at", "node_id", "url", "html_url"}
_ACTIVE = {"active", "enabled"}


def _canonical(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {str(key): _canonical(item) for key, item in sorted(value.items()) if key not in _IGNORED_KEYS}
    if isinstance(value, list):
        normalized = [_canonical(item) for item in value]
        return sorted(normalized, key=lambda item: json.dumps(item, sort_keys=True, separators=(",", ":")))
    return value


def _identity(ruleset: Mapping[str, Any]) -> str:
    source = ruleset.get("source", "")
    identifier = ruleset.get("id")
    if not isinstance(source, str) or not source or not isinstance(identifier, int):
        raise InputError("Each ruleset needs a non-empty string 'source' and integer 'id'.")
    return f"{source}#{identifier}"


def normalize_rulesets(repository: str, rulesets: Iterable[Mapping[str, Any]]) -> dict[str, Any]:
    if not repository or "/" not in repository:
        raise InputError("Repository must be in OWNER/REPO form.")
    normalized = []
    for raw in rulesets:
        item = _canonical(raw)
        if not isinstance(item, dict):
            raise InputError("Ruleset response must be an object.")
        _identity(item)
        normalized.append(item)
    return {"schema_version": 1, "repository": repository, "rulesets": sorted(normalized, key=_identity)}


def load_snapshot(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise InputError(f"Cannot read snapshot {path}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise InputError(f"Invalid JSON in snapshot {path}: {exc.msg}") from exc
    if not isinstance(data, dict) or data.get("schema_version") != 1 or not isinstance(data.get("repository"), str):
        raise InputError("Snapshot must contain schema_version 1 and a repository string.")
    rulesets = data.get("rulesets")
    if not isinstance(rulesets, list):
        raise InputError("Snapshot field 'rulesets' must be a list.")
    return normalize_rulesets(data["repository"], rulesets)


def capture(repository: str) -> dict[str, Any]:
    """Read rulesets with gh; capture is the sole networked operation."""
    if not repository or "/" not in repository:
        raise InputError("Repository must be in OWNER/REPO form.")
    try:
        listed = subprocess.run(
            ["gh", "api", "--paginate", "--slurp", f"repos/{repository}/rulesets?includes_parents=true&per_page=100"],
            check=True, capture_output=True, text=True,
        )
        pages = json.loads(listed.stdout)
        summaries = [summary for page in pages for summary in page] if isinstance(pages, list) and all(isinstance(page, list) for page in pages) else pages
        if not isinstance(summaries, list):
            raise InputError("GitHub returned an invalid ruleset list.")
        detailed: list[Mapping[str, Any]] = []
        for summary in summaries:
            if not isinstance(summary, Mapping) or not isinstance(summary.get("id"), int):
                raise InputError("GitHub returned a ruleset without an integer id.")
            response = subprocess.run(
                ["gh", "api", f"repos/{repository}/rulesets/{summary['id']}?includes_parents=true"],
                check=True, capture_output=True, text=True,
            )
            detail = json.loads(response.stdout)
            if not isinstance(detail, Mapping):
                raise InputError("GitHub returned an invalid ruleset detail.")
            detailed.append(detail)
    except FileNotFoundError as exc:
        raise InputError("'gh' was not found. Install and authenticate GitHub CLI before capture.") from exc
    except subprocess.CalledProcessError as exc:
        detail = (exc.stderr or exc.stdout or "GitHub CLI failed").strip()
        raise InputError(f"Could not capture rulesets: {detail}") from exc
    except json.JSONDecodeError as exc:
        raise InputError("GitHub CLI returned invalid JSON.") from exc
    return normalize_rulesets(repository, detailed)


def _rules(ruleset: Mapping[str, Any]) -> set[str]:
    raw = ruleset.get("rules", [])
    if not isinstance(raw, list):
        return set()
    return {json.dumps(rule, sort_keys=True, separators=(",", ":")) for rule in raw}


def _ref_names(ruleset: Mapping[str, Any]) -> tuple[set[str], set[str]]:
    conditions = ruleset.get("conditions", {})
    ref_name = conditions.get("ref_name", {}) if isinstance(conditions, Mapping) else {}
    if not isinstance(ref_name, Mapping):
        return set(), set()
    include = ref_name.get("include", [])
    exclude = ref_name.get("exclude", [])
    return ({item for item in include if isinstance(item, str)}, {item for item in exclude if isinstance(item, str)})


def _bypasses(ruleset: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    raw = ruleset.get("bypass_actors", [])
    if not isinstance(raw, list):
        return {}
    output = {}
    for actor in raw:
        if isinstance(actor, Mapping) and isinstance(actor.get("actor_id"), int) and isinstance(actor.get("actor_type"), str):
            output[f"{actor['actor_type']}#{actor['actor_id']}"] = actor
    return output


def _finding(code: str, severity: str, ruleset: Mapping[str, Any], message: str) -> dict[str, str]:
    return {"code": code, "severity": severity, "ruleset": _identity(ruleset), "message": message}


def diff(old: Mapping[str, Any], new: Mapping[str, Any]) -> list[dict[str, str]]:
    old_sets = {_identity(item): item for item in old["rulesets"]}
    new_sets = {_identity(item): item for item in new["rulesets"]}
    findings: list[dict[str, str]] = []
    for key in sorted(old_sets):
        before = old_sets[key]
        after = new_sets.get(key)
        old_active = str(before.get("enforcement", "")).lower() in _ACTIVE
        if after is None:
            if old_active:
                findings.append(_finding("RUL005", "error", before, "An active ruleset was removed."))
            continue
        new_active = str(after.get("enforcement", "")).lower() in _ACTIVE
        if old_active and not new_active:
            findings.append(_finding("RUL001", "error", after, "Ruleset enforcement changed from active to non-active."))
        removed_rules = _rules(before) - _rules(after)
        if old_active and removed_rules:
            findings.append(_finding("RUL002", "warning", after, f"{len(removed_rules)} rule(s) were removed from an active ruleset."))
        old_include, old_exclude = _ref_names(before)
        new_include, new_exclude = _ref_names(after)
        broadened = ("~ALL" in new_include and "~ALL" not in old_include) or bool(new_include - old_include) or bool(old_exclude - new_exclude)
        if broadened:
            findings.append(_finding("RUL003", "warning", after, "The ruleset's target refs were broadened."))
        old_bypass, new_bypass = _bypasses(before), _bypasses(after)
        added = set(new_bypass) - set(old_bypass)
        weakened = {key for key in set(old_bypass) & set(new_bypass) if old_bypass[key].get("bypass_mode") != new_bypass[key].get("bypass_mode")}
        if added or weakened:
            findings.append(_finding("RUL004", "warning", after, "A bypass actor was added or its bypass mode changed."))
    return findings
