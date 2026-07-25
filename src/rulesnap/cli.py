from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence

from .core import InputError, capture, diff, load_snapshot


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="rulesnap", description="Capture and semantically diff GitHub repository rulesets.")
    commands = parser.add_subparsers(dest="command", required=True)
    capture_parser = commands.add_parser("capture", help="write a normalized, read-only ruleset snapshot")
    capture_parser.add_argument("repository", help="GitHub repository in OWNER/REPO form")
    capture_parser.add_argument("--output", type=Path, required=True, help="snapshot JSON path")
    diff_parser = commands.add_parser("diff", help="compare two ruleset snapshots")
    diff_parser.add_argument("old", type=Path)
    diff_parser.add_argument("new", type=Path)
    diff_parser.add_argument("--format", choices=("human", "json"), default="human")
    return parser


def _human(findings: list[dict[str, str]]) -> str:
    if not findings:
        return "No risk-classified ruleset changes found."
    return "\n".join(f"{item['severity'].upper()} {item['code']} {item['ruleset']} — {item['message']}" for item in findings)


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        if args.command == "capture":
            snapshot = capture(args.repository)
            args.output.write_text(json.dumps(snapshot, indent=2) + "\n", encoding="utf-8")
            print(f"Wrote {len(snapshot['rulesets'])} ruleset(s) to {args.output}.")
            return 0
        findings = diff(load_snapshot(args.old), load_snapshot(args.new))
    except InputError as exc:
        print(f"rulesnap: error: {exc}")
        return 2
    print(json.dumps(findings, indent=2) if args.format == "json" else _human(findings))
    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
