"""Validate data quality of papers.csv and print a markdown report.

Usage:
    python validate_data.py

To add a new check, define a function that accepts a list of row dicts
and returns a CheckResult, then add it to the CHECKS list.
"""

import csv
import os
from collections import Counter
from dataclasses import dataclass, field

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..", "..")
PAPERS_CSV = os.path.join(REPO_ROOT, "public", "data", "papers.csv")


@dataclass
class CheckResult:
    name: str
    severity: str  # "error" or "warning"
    issues: list = field(default_factory=list)


# ---------------------------------------------------------------------------
# Checks — each takes a list of row dicts and returns a CheckResult
# ---------------------------------------------------------------------------

def check_empty_abstracts(rows):
    """Report papers with empty or missing abstracts."""
    issues = []
    for row in rows:
        abstract = (row.get("Abstract") or "").strip()
        if not abstract:
            doi = row.get("DOI", "N/A")
            title = row.get("Title", "N/A")
            issues.append(f"DOI `{doi}` — {title}")
    return CheckResult("Empty or missing abstracts", "error", issues)


def check_duplicate_dois(rows):
    """Report duplicate DOI values."""
    doi_counts = Counter(row["DOI"] for row in rows if row.get("DOI", "").strip())
    issues = []
    for doi, count in sorted(doi_counts.items()):
        if count > 1:
            issues.append(f"DOI `{doi}` appears {count} times")
    return CheckResult("Duplicate DOIs", "error", issues)


def check_duplicate_titles(rows):
    """Report duplicate paper titles (may be legitimate across venues)."""
    title_rows = {}
    for row in rows:
        title = (row.get("Title") or "").strip()
        if title:
            title_rows.setdefault(title, []).append(row)
    issues = []
    for title, matching in sorted(title_rows.items()):
        if len(matching) > 1:
            venues = ", ".join(
                f"{r.get('Conference', '?')} {r.get('Year', '?')}" for r in matching
            )
            issues.append(f"\"{title}\" — appears in: {venues}")
    return CheckResult("Duplicate paper titles", "warning", issues)


# Registry of all checks — add new check functions here
CHECKS = [
    check_empty_abstracts,
    check_duplicate_dois,
    check_duplicate_titles,
]


# ---------------------------------------------------------------------------
# Report generation
# ---------------------------------------------------------------------------

def generate_report(rows):
    results = [check(rows) for check in CHECKS]

    total_errors = sum(len(r.issues) for r in results if r.severity == "error")
    total_warnings = sum(len(r.issues) for r in results if r.severity == "warning")

    lines = []
    lines.append("# Data Validation Report")
    lines.append("")
    lines.append(f"**Papers checked:** {len(rows)}")
    lines.append(f"**Errors:** {total_errors}")
    lines.append(f"**Warnings:** {total_warnings}")
    lines.append("")

    for result in results:
        icon = "x" if result.severity == "error" else "!"
        status = "PASS" if not result.issues else result.severity.upper()
        lines.append(f"## [{status}] {result.name}")
        lines.append("")
        if not result.issues:
            lines.append("No issues found.")
        else:
            lines.append(f"{len(result.issues)} issue(s) found:")
            lines.append("")
            for issue in result.issues:
                lines.append(f"- {issue}")
        lines.append("")

    return "\n".join(lines)


REPORT_FILE = os.path.join(os.path.dirname(__file__), "report.md")


def main():
    with open(PAPERS_CSV, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    report = generate_report(rows)
    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"Report written to {REPORT_FILE}")


if __name__ == "__main__":
    main()
