from __future__ import annotations

import argparse
import sys
import xml.etree.ElementTree as ET
from pathlib import Path


def parse_junit(path: Path) -> dict[str, int]:
    if not path.exists():
        return {"tests": 0, "failures": 0, "errors": 0, "skipped": 0}

    root = ET.parse(path).getroot()
    if root.tag == "testsuite":
        suites = [root]
    else:
        suites = list(root.iter("testsuite"))

    totals = {"tests": 0, "failures": 0, "errors": 0, "skipped": 0}
    for suite in suites:
        for key in totals:
            totals[key] += int(suite.attrib.get(key, 0))
    return totals


def line(label: str, totals: dict[str, int]) -> str:
    passed = totals["tests"] - totals["failures"] - totals["errors"] - totals["skipped"]
    return (
        f"| {label} | {totals['tests']} | {passed} | {totals['failures']} | "
        f"{totals['errors']} | {totals['skipped']} |"
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--functional", default="reports/pytest-junit.xml")
    parser.add_argument("--release-gate", default="reports/release-gate-junit.xml")
    parser.add_argument("--known-bugs", default="reports/known-bugs-junit.xml")
    parser.add_argument("--output", default="reports/quality-summary.md")
    args = parser.parse_args()

    functional = parse_junit(Path(args.functional))
    release_gate = parse_junit(Path(args.release_gate))
    known_bugs = parse_junit(Path(args.known_bugs))

    content = "\n".join(
        [
            "# Quality Summary",
            "",
            "| Suite | Tests | Passed | Failures | Errors | Skipped |",
            "|---|---:|---:|---:|---:|---:|",
            line("Quality gate", functional),
            line("Release-blocking known bugs", release_gate),
            line("Non-blocking known bug diagnostics", known_bugs),
            "",
            "Release-blocking known bugs represent high-severity/security defects and should keep the release gate red until fixed or formally waived.",
            "",
        ]
    )

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(content, encoding="utf-8")
    sys.stdout.write(content)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
