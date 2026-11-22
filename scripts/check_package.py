#!/usr/bin/env python3
"""Offline integrity checks. Does not evaluate model behavior or legal correctness."""
from pathlib import Path
import json
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = [
    "skills/invention-disclosure-review/SKILL.md",
    "skills/invention-disclosure-review/agents/openai.yaml",
    "skills/invention-disclosure-review/references/workflow.md",
    "skills/invention-disclosure-review/references/report-contract.md",
    "skills/invention-disclosure-review/references/report-template.md",
    "examples/invention-disclosure-review/README.md",
    "examples/invention-disclosure-review/inputs.md",
    "examples/invention-disclosure-review/worked-example.md",
    "evaluations/disclosure-review-cases.json",
    "skills/portfolio-strategy/SKILL.md", "skills/portfolio-strategy/agents/openai.yaml",
    "skills/portfolio-strategy/references/workflow.md", "skills/portfolio-strategy/references/input-format.md",
    "skills/portfolio-strategy/scripts/strategy.py", "tests/test_strategy.py",
    "examples/portfolio-strategy/input.json", "examples/portfolio-strategy/csv-input.json",
    "examples/portfolio-strategy/records.csv", "examples/portfolio-strategy/sources.md",
    "examples/portfolio-strategy/README.md", "examples/portfolio-strategy/expected-output.json",
    "examples/portfolio-strategy/strategy-review.md", "templates/strategy-review.md",
    "evaluations/strategy-cases.json",
    "README.md", "LICENSE", "CONTRIBUTING.md", "ROADMAP.md", "PUBLISHING.md", "CHANGELOG.md",
    "skills/filing-review/SKILL.md", "skills/filing-review/agents/openai.yaml",
    "skills/filing-review/references/review-guidance.md",
    "skills/filing-review/references/input-format.md",
    "skills/filing-review/scripts/review.py", "tests/test_review.py",
    "examples/filing-review/input.json", "examples/filing-review/sources.md",
    "examples/filing-review/README.md", "examples/filing-review/expected-output.json",
    "examples/filing-review/review-packet.md", "evaluations/filing-review-cases.json",
    "skills/invention-intake/SKILL.md",
    "skills/invention-intake/agents/openai.yaml",
    "skills/invention-intake/references/evidence.md",
    "skills/invention-intake/references/interview.md",
    "skills/invention-intake/references/outputs.md",
    "skills/invention-intake/references/filing-review.md",
    "templates/invention-disclosure.md", "templates/filing-review.md",
    "examples/synthetic-invention/inputs.md",
    "examples/synthetic-invention/worked-example.md",
    "examples/synthetic-invention/reviewer-notes.md",
    "evaluations/cases.json", "evaluations/rubric.md", "evaluations/STATUS.md",
]

def check():
    errors = []
    for name in REQUIRED:
        if not (ROOT / name).is_file():
            errors.append(f"Missing required file: {name}")
    if errors:
        return errors
    for path in ROOT.rglob("*.md"):
        for target in re.findall(r"\[[^\]]*\]\(([^)]+)\)", path.read_text()):
            if "://" in target or target.startswith("#"):
                continue
            destination = target.split("#", 1)[0]
            if not (path.parent / destination).exists():
                errors.append(f"Broken local link in {path.relative_to(ROOT)}: {target}")
    inputs = (ROOT / "examples/synthetic-invention/inputs.md").read_text()
    valid = set()
    source = None
    for line in inputs.splitlines():
        match = re.match(r"## (SRC-\d+) ", line)
        if match:
            source = match.group(1)
        match = re.match(r"### §(\d+)$", line)
        if match and source:
            valid.add((source, match.group(1)))
    output = (ROOT / "examples/synthetic-invention/worked-example.md").read_text()
    citations = re.findall(r"\[(SRC-\d+) §(\d+)\]", output)
    if not citations:
        errors.append("Worked example contains no recognized source citations")
    for citation in citations:
        if citation not in valid:
            errors.append(f"Unknown worked-example source locator: {citation}")
    cases = json.loads((ROOT / "evaluations/cases.json").read_text())
    ids = [case["id"] for case in cases]
    if len(set(ids)) != len(ids) or len(ids) != 5:
        errors.append("Expected five uniquely identified challenge cases")
    for case in cases:
        if not case.get("review_for"):
            errors.append(f"No review criteria for {case['id']}")
        if "input" in case and not (ROOT / case["input"]).is_file():
            errors.append(f"Missing case input for {case['id']}")
        if not (case.get("input") or case.get("input_text")):
            errors.append(f"No input for {case['id']}")
    for name in ("invention-intake", "filing-review", "portfolio-strategy", "invention-disclosure-review"):
        body = (ROOT / "skills" / name / "SKILL.md").read_text()
        lines = body.splitlines()
        if (len(lines) < 5 or lines[0] != "---" or lines[1] != "name: " + name
                or not lines[2].startswith("description: ") or lines[3] != "---"
                or len(lines[2].removeprefix("description: ")) > 1024 or "TODO" in body):
            errors.append("Unexpected skill frontmatter shape or unfinished scaffold: " + name)
        if "$" + name not in (ROOT / "skills" / name / "agents/openai.yaml").read_text():
            errors.append("Missing invocation prompt: " + name)
    disclosure_cases = json.loads((ROOT / "evaluations/disclosure-review-cases.json").read_text())
    if len(disclosure_cases) != 5 or len({c["id"] for c in disclosure_cases}) != 5:
        errors.append("Expected five unique disclosure-review behavioral cases")
    for case in disclosure_cases:
        if not case.get("review_for") or not (case.get("input") or case.get("input_text")):
            errors.append("Incomplete disclosure-review case: " + case["id"])
        if case.get("input") and not (ROOT / case["input"]).is_file():
            errors.append("Missing disclosure-review case input: " + case["id"])
    fixture = (ROOT / "examples/invention-disclosure-review/inputs.md").read_text()
    valid_disclosure_locators = set(re.findall(r"## (S-\d+ §\d+)", fixture))
    worked = (ROOT / "examples/invention-disclosure-review/worked-example.md").read_text()
    for locator in re.findall(r"S-\d+ §\d+", worked):
        if locator not in valid_disclosure_locators:
            errors.append("Unknown disclosure-review example locator: " + locator)
    filing_cases = json.loads((ROOT / "evaluations/filing-review-cases.json").read_text())
    if len(filing_cases) != 3 or len({c["id"] for c in filing_cases}) != 3:
        errors.append("Expected three unique filing-review behavioral cases")
    run = subprocess.run([sys.executable, str(ROOT / "skills/filing-review/scripts/review.py"),
                          str(ROOT / "examples/filing-review/input.json")], capture_output=True, text=True)
    if run.returncode:
        errors.append("Example calculator failed: " + run.stderr)
    elif json.loads(run.stdout) != json.loads((ROOT / "examples/filing-review/expected-output.json").read_text()):
        errors.append("Saved calculator output differs from fresh calculation")
    strategy_cases = json.loads((ROOT / "evaluations/strategy-cases.json").read_text())
    if len(strategy_cases) != 3 or len({c["id"] for c in strategy_cases}) != 3:
        errors.append("Expected three unique strategy behavioral cases")
    expected = json.loads((ROOT / "examples/portfolio-strategy/expected-output.json").read_text())
    for csv_mode in (False, True):
        command = [sys.executable, str(ROOT / "skills/portfolio-strategy/scripts/strategy.py"),
                   str(ROOT / ("examples/portfolio-strategy/csv-input.json" if csv_mode else "examples/portfolio-strategy/input.json"))]
        if csv_mode:
            command += ["--records-csv", str(ROOT / "examples/portfolio-strategy/records.csv")]
        run = subprocess.run(command, capture_output=True, text=True)
        if run.returncode:
            errors.append("Strategy example failed: " + run.stderr)
        elif json.loads(run.stdout) != expected:
            errors.append("Strategy saved output does not match " + ("CSV" if csv_mode else "JSON") + " calculation")
    source_text = (ROOT / "examples/portfolio-strategy/sources.md").read_text()
    valid_strategy_locators = set()
    section = None
    for line in source_text.splitlines():
        match = re.match(r"## ([A-Z]+-[0-9]+)$", line)
        if match:
            section = match.group(1)
        match = re.match(r"### §([0-9]+)$", line)
        if match and section:
            valid_strategy_locators.add(section + " §" + match.group(1))
    fixture_text = (ROOT / "examples/portfolio-strategy/input.json").read_text()
    for locator in re.findall(r"sources[.]md ([A-Z]+-[0-9]+ §[0-9]+)", fixture_text):
        if locator not in valid_strategy_locators:
            errors.append("Missing strategy example source locator: " + locator)
    return errors

if __name__ == "__main__":
    failures = check()
    if failures:
        for failure in failures:
            print("FAIL:", failure)
        raise SystemExit(1)
    print("PASS: package files, local links, sixteen case definitions, metadata shape, example locators, calculation reproducibility, and JSON/CSV equivalence.")
    print("Scope: structural checks only; no model-performance or legal validation.")
