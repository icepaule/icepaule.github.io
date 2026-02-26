#!/usr/bin/env python3
"""
generate_status.py - Status dashboard generator for icepaule.github.io.

Generates projects/status.md with Mermaid charts, coverage tables,
and security scan summaries.
"""

import json
import os
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = REPO_ROOT / "_data"
PROJECTS_DIR = REPO_ROOT / "projects"
STATUS_FILE = PROJECTS_DIR / "status.md"
GITHUB_USER = "icepaule"


def load_json(filename):
    """Load a JSON file from _data/."""
    path = DATA_DIR / filename
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def generate_pipeline_diagram():
    """Generate Mermaid flowchart for the CI/CD pipeline."""
    return """```mermaid
flowchart LR
    A[Cron 03:00 UTC] --> B[Checkout]
    B --> C[Setup Python]
    C --> D{Scan Secrets}
    D -->|Findings| E[Pushover Alert]
    D -->|Clean| F[Generate Docs]
    E --> F
    F --> G[Generate Status]
    G --> H{Changes?}
    H -->|Yes| I[Commit & Push]
    H -->|No| J[Done]
    I --> J

    style A fill:#2d333b,stroke:#539bf5
    style D fill:#2d333b,stroke:#f47067
    style E fill:#2d333b,stroke:#f0883e
    style F fill:#2d333b,stroke:#57ab5a
    style I fill:#2d333b,stroke:#539bf5
```"""


def generate_coverage_table(repo_status):
    """Generate documentation coverage table."""
    if not repo_status:
        return "*No repo status data available. Run generate_docs.py first.*"

    lines = [
        "| Repo | Description | Status | Doc Page |",
        "|:-----|:------------|:-------|:---------|",
    ]

    status_icons = {
        "curated": "Curated",
        "auto_updated": "Auto",
        "auto_created": "Auto",
        "no_readme": "No README",
        "unknown": "Unknown",
    }

    for repo in sorted(repo_status, key=lambda r: r["name"].lower()):
        name = repo["name"]
        desc = repo.get("description", "")[:60]
        status = status_icons.get(repo.get("status", "unknown"), "Unknown")
        doc_file = repo.get("doc_file", "")
        if doc_file and repo.get("status") in ("curated", "auto_updated", "auto_created"):
            doc_link = f"[View]({doc_file.replace('.md', '.html')})"
        else:
            doc_link = "-"

        lines.append(f"| [{name}](https://github.com/{GITHUB_USER}/{name}) | {desc} | {status} | {doc_link} |")

    return "\n".join(lines)


def generate_scan_summary(scan_results):
    """Generate security scan summary section."""
    if not scan_results:
        return "*No scan results available. Run scan_secrets.py first.*"

    scan_date = scan_results.get("scan_date", "unknown")[:10]
    total = scan_results.get("total_repos", 0)
    clean = scan_results.get("clean_repos", 0)
    with_findings = scan_results.get("repos_with_findings", 0)
    total_findings = scan_results.get("total_findings", 0)
    verified = scan_results.get("verified_findings", 0)
    new = scan_results.get("new_findings", 0)

    lines = [
        f"| Metric | Value |",
        f"|:-------|:------|",
        f"| Last Scan | {scan_date} |",
        f"| Repos Scanned | {total} |",
        f"| Clean Repos | {clean} |",
        f"| Repos with Findings | {with_findings} |",
        f"| Total Findings | {total_findings} |",
        f"| Verified Findings | {verified} |",
        f"| New Findings (last scan) | {new} |",
    ]
    return "\n".join(lines)


def generate_pie_chart(scan_results):
    """Generate Mermaid pie chart for scan results."""
    if not scan_results:
        return ""

    clean = scan_results.get("clean_repos", 0)
    with_findings = scan_results.get("repos_with_findings", 0)

    if clean == 0 and with_findings == 0:
        return ""

    return f"""```mermaid
pie title Repository Security Status
    "Clean" : {clean}
    "Findings" : {with_findings}
```"""


def generate_config_status():
    """Generate configuration status section."""
    pushover_configured = bool(
        os.environ.get("PUSHOVER_USER_KEY") and os.environ.get("PUSHOVER_API_TOKEN")
    )

    lines = [
        "| Setting | Status |",
        "|:--------|:-------|",
        f"| Daily Schedule | 03:00 UTC |",
        f"| Secret Scanning | Enabled |",
        f"| Doc Generation | Enabled |",
        f"| Pushover Alerts | {'Configured' if pushover_configured else 'Not configured'} |",
        f"| Fork Scanning | Disabled |",
    ]
    return "\n".join(lines)


def main():
    print("=== IcePaule Status Dashboard Generator ===\n")

    repo_status = load_json("repo_status.json")
    scan_results = load_json("scan_results.json")

    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    # Count stats
    total_repos = len(repo_status) if repo_status else 0
    curated = sum(1 for r in (repo_status or []) if r.get("status") == "curated")
    auto = sum(1 for r in (repo_status or []) if r.get("status") in ("auto_updated", "auto_created"))

    page = f"""---
layout: default
title: Status Dashboard
nav_order: 99
---

# Status Dashboard
{{: .fs-9 }}

Automated documentation & security scanning status.
{{: .fs-6 .fw-300 }}

*Last updated: {now}*

---

## CI/CD Pipeline

{generate_pipeline_diagram()}

---

## Documentation Coverage

**{total_repos} repos** documented: {curated} curated, {auto} auto-generated.

{generate_coverage_table(repo_status)}

---

## Security Scan Summary

{generate_scan_summary(scan_results)}

{generate_pie_chart(scan_results)}

---

## Configuration

{generate_config_status()}

---

*This page is auto-generated by [generate_status.py](https://github.com/{GITHUB_USER}/{GITHUB_USER}.github.io/blob/main/scripts/generate_status.py).*
"""

    PROJECTS_DIR.mkdir(parents=True, exist_ok=True)
    STATUS_FILE.write_text(page, encoding="utf-8")
    print(f"Status dashboard written to: {STATUS_FILE}")


if __name__ == "__main__":
    main()
