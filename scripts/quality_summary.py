from __future__ import annotations

import argparse
import ast
import sys
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class TestCase:
    path: str
    name: str
    markers: set[str]


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


def parse_junit_failures(path: Path) -> list[str]:
    if not path.exists():
        return []

    root = ET.parse(path).getroot()
    failures = []
    for testcase in root.iter("testcase"):
        has_failure = testcase.find("failure") is not None or testcase.find("error") is not None
        if has_failure:
            classname = testcase.attrib.get("classname", "")
            name = testcase.attrib.get("name", "")
            failures.append(f"{classname}::{name}".strip(":"))
    return failures


def decorator_marker_name(decorator: ast.expr) -> str | None:
    node = decorator
    if isinstance(node, ast.Call):
        node = node.func

    parts = []
    while isinstance(node, ast.Attribute):
        parts.append(node.attr)
        node = node.value
    if isinstance(node, ast.Name):
        parts.append(node.id)

    dotted = ".".join(reversed(parts))
    prefix = "pytest.mark."
    if dotted.startswith(prefix):
        return dotted.removeprefix(prefix)
    return None


def collect_tests(test_dir: Path) -> list[TestCase]:
    cases = []
    for path in sorted(test_dir.glob("test_*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in tree.body:
            if isinstance(node, ast.FunctionDef) and node.name.startswith("test_"):
                markers = {
                    marker
                    for decorator in node.decorator_list
                    if (marker := decorator_marker_name(decorator))
                }
                cases.append(TestCase(str(path), node.name, markers))
    return cases


def line(label: str, totals: dict[str, int]) -> str:
    passed = totals["tests"] - totals["failures"] - totals["errors"] - totals["skipped"]
    return (
        f"| {label} | {totals['tests']} | {passed} | {totals['failures']} | "
        f"{totals['errors']} | {totals['skipped']} |"
    )


def passed_count(totals: dict[str, int]) -> int:
    return totals["tests"] - totals["failures"] - totals["errors"] - totals["skipped"]


def coverage_line(label: str, cases: list[TestCase], selector) -> str:
    selected = [case for case in cases if selector(case)]
    blocking = [
        case for case in selected if "known_bug_high" in case.markers or "security" in case.markers
    ]
    diagnostics = [
        case for case in selected if "known_bug" in case.markers and case not in blocking
    ]
    return f"| {label} | {len(selected)} | {len(blocking)} | {len(diagnostics)} |"


def coverage_counts(cases: list[TestCase]) -> list[tuple[str, int, int, int]]:
    lenses = [
        ("API contract and schema", lambda case: "contract" in case.markers),
        ("Negative and edge cases", lambda case: "negative" in case.markers),
        ("Security and authorization", lambda case: "security" in case.markers),
        ("Test data management", lambda case: "data_management" in case.markers),
        ("UX and API usability", lambda case: "test_ux_quality.py" in case.path),
        ("Resilience", lambda case: "test_resilience.py" in case.path),
    ]
    rows = []
    for label, selector in lenses:
        selected = [case for case in cases if selector(case)]
        blocking = [
            case
            for case in selected
            if "known_bug_high" in case.markers or "security" in case.markers
        ]
        diagnostics = [
            case for case in selected if "known_bug" in case.markers and case not in blocking
        ]
        rows.append((label, len(selected), len(blocking), len(diagnostics)))
    return rows


def coverage_line_from_counts(label: str, total: int, blocking: int, diagnostics: int) -> str:
    return f"| {label} | {total} | {blocking} | {diagnostics} |"


def simple_status(ok: bool) -> str:
    return "OK" if ok else "Attention"


def architecture_status(root: Path) -> list[str]:
    checks = [
        (
            "Domain HTTP client",
            root / "tests/client.py",
            "Centralizes base URL, timeout, endpoint paths, and HTTP session lifecycle.",
        ),
        (
            "Centralized test data",
            root / "tests/data.py",
            "Keeps service IDs, categories, search terms, and webhook events in one place.",
        ),
        (
            "Signed webhook helper",
            root / "tests/helpers.py",
            "Builds canonical JSON body and HMAC headers through a reusable helper.",
        ),
        (
            "Lint gate",
            root / ".github/workflows/quality.yml",
            "Runs ruff check and format validation before API test execution.",
        ),
    ]
    lines = []
    for label, path, description in checks:
        status = "Present" if path.exists() else "Missing"
        lines.append(f"| {label} | {status} | {description} |")
    return lines


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--functional", default="reports/pytest-junit.xml")
    parser.add_argument("--release-gate", default="reports/release-gate-junit.xml")
    parser.add_argument("--known-bugs", default="reports/known-bugs-junit.xml")
    parser.add_argument("--output", default="reports/quality-summary.md")
    parser.add_argument("--test-dir", default="tests")
    args = parser.parse_args()

    functional = parse_junit(Path(args.functional))
    release_gate = parse_junit(Path(args.release_gate))
    known_bugs = parse_junit(Path(args.known_bugs))
    release_failures = parse_junit_failures(Path(args.release_gate))
    diagnostic_failures = parse_junit_failures(Path(args.known_bugs))
    test_cases = collect_tests(Path(args.test_dir))
    coverage = coverage_counts(test_cases)
    functional_ok = functional["failures"] == 0 and functional["errors"] == 0
    release_blocked = release_gate["failures"] > 0 or release_gate["errors"] > 0
    total_executed = functional["tests"] + release_gate["tests"] + known_bugs["tests"]
    total_failures = functional["failures"] + release_gate["failures"] + known_bugs["failures"]
    total_errors = functional["errors"] + release_gate["errors"] + known_bugs["errors"]

    content_lines = [
        "# Quality Summary",
        "",
        "## Geral",
        "",
        "| Item | Status | Leitura rapida |",
        "|---|---|---|",
        f"| Automacao do CI | {simple_status(functional_ok)} | Quality gate funcional executou com {passed_count(functional)} de {functional['tests']} testes passando. |",
        f"| Decisao de release | {'Blocked' if release_blocked else 'OK'} | {release_gate['failures']} bug(s) critico(s)/seguranca ainda exigem correcao ou waiver formal. |",
        f"| Diagnostico conhecido | {'Tracked' if known_bugs['tests'] else 'None'} | {known_bugs['failures']} bug(s) medio/baixo ou risco(s) de UX seguem documentados. |",
        f"| Total executado | {'Reviewed'} | {total_executed} testes nos relatorios, com {total_failures} falha(s) esperadas e {total_errors} erro(s). |",
        "",
        "> CI verde significa que a automacao rodou corretamente. Nao significa liberacao automatica: release segue bloqueado enquanto houver bugs criticos listados abaixo.",
        "",
        "## Numeros-chave",
        "",
        "| Indicador | Valor |",
        "|---|---:|",
        f"| Quality gate funcional | {passed_count(functional)}/{functional['tests']} passed |",
        f"| Release blockers conhecidos | {release_gate['failures']} |",
        f"| Bugs diagnosticos conhecidos | {known_bugs['failures']} |",
        f"| Lentes de qualidade mapeadas | {len(coverage)} |",
        "",
        "## Execution Gates",
        "",
        "| Suite | Tests | Passed | Failures | Errors | Skipped |",
        "|---|---:|---:|---:|---:|---:|",
        line("Quality gate", functional),
        line("Release-blocking known bugs", release_gate),
        line("Non-blocking known bug diagnostics", known_bugs),
        "",
        "Release-blocking known bugs represent high-severity/security defects. Release should not be approved until they are fixed or formally waived.",
        "",
        "## Quality Lenses",
        "",
        "| Lens | Tests mapped | Blocking known bugs | Diagnostic known bugs |",
        "|---|---:|---:|---:|",
        *[coverage_line_from_counts(*row) for row in coverage],
        "",
        "## Test Architecture",
        "",
        "| Area | Status | Why it matters |",
        "|---|---|---|",
        *architecture_status(Path.cwd()),
        "",
    ]

    if release_failures:
        content_lines.extend(
            [
                "## Release Blockers",
                "",
                "| Failing test |",
                "|---|",
                *[f"| `{failure}` |" for failure in release_failures],
                "",
            ]
        )

    if diagnostic_failures:
        content_lines.extend(
            [
                "## Diagnostic Bugs",
                "",
                "| Failing test |",
                "|---|",
                *[f"| `{failure}` |" for failure in diagnostic_failures],
                "",
            ]
        )

    content = "\n".join(content_lines)

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(content, encoding="utf-8")
    sys.stdout.write(content)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
