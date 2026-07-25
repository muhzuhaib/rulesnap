import json
from pathlib import Path

from rulesnap.cli import main
from rulesnap.core import normalize_rulesets


def test_diff_json_output_and_exit_status(tmp_path: Path, capsys: object) -> None:
    old = normalize_rulesets("octo/demo", [{"id": 1, "source": "octo/demo", "enforcement": "active", "rules": []}])
    new = normalize_rulesets("octo/demo", [])
    old_path, new_path = tmp_path / "old.json", tmp_path / "new.json"
    old_path.write_text(json.dumps(old), encoding="utf-8")
    new_path.write_text(json.dumps(new), encoding="utf-8")

    assert main(["diff", str(old_path), str(new_path), "--format", "json"]) == 1
    assert json.loads(capsys.readouterr().out)[0]["code"] == "RUL005"


def test_diff_rejects_bad_input(tmp_path: Path, capsys: object) -> None:
    path = tmp_path / "bad.json"
    path.write_text("[]", encoding="utf-8")

    assert main(["diff", str(path), str(path)]) == 2
    assert "rulesnap: error:" in capsys.readouterr().out
