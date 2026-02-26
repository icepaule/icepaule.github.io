#!/usr/bin/env python3
"""
generate_docs.py - Automated documentation generator for icepaule GitHub repos.

Fetches READMEs from GitHub, creates/updates Jekyll project pages.
Protects manually curated pages from being overwritten.
"""

import json
import os
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PROJECTS_DIR = REPO_ROOT / "projects"
DATA_DIR = REPO_ROOT / "_data"
GITHUB_USER = "icepaule"
MANUALLY_CURATED_MARKER = "<!-- manually-curated -->"
STUB_THRESHOLD = 500  # bytes

# Category mapping: repo name (lowercase) -> parent category title
CATEGORY_MAP = {
    # Security & Malware Analysis
    "iceporge": "Security & Malware Analysis",
    "iceporge-cockpit": "Security & Malware Analysis",
    "iceporge-mwdb-stack": "Security & Malware Analysis",
    "iceporge-mwdb-feeder": "Security & Malware Analysis",
    "iceporge-cape-feed": "Security & Malware Analysis",
    "iceporge-cape-mailer": "Security & Malware Analysis",
    "iceporge-ghidra-orchestrator": "Security & Malware Analysis",
    "iceporge-malware-rag": "Security & Malware Analysis",
    "icelaborvpn": "Security & Malware Analysis",
    "iceintelligence": "Security & Malware Analysis",
    "icecrow": "Security & Malware Analysis",
    "icematrix": "Security & Malware Analysis",
    "icebackup": "Security & Malware Analysis",
    # Home Automation & Networking
    "icehomeassist": "Home Automation & Networking",
    "icewifi": "Home Automation & Networking",
    "adguard-kiosk": "Home Automation & Networking",
    "tibberampel": "Home Automation & Networking",
    "icexwiki": "Home Automation & Networking",
    "icemailarchive": "Home Automation & Networking",
    # Mesh & Communication
    "ice-mtastik": "Mesh & Communication",
    "icemeshcore": "Mesh & Communication",
    # Data & Tools
    "icedataemphasise": "Data & Tools",
    "icetimereport": "Data & Tools",
    "iceai-tax-2025": "Data & Tools",
    "iceseller": "Data & Tools",
    # Hardware & ESP32
    "esp32cam-dataset-firmware": "Hardware & ESP32",
    "followmysun": "Hardware & ESP32",
    # Cloud & Infrastructure
    "icehetzner": "Cloud & Infrastructure",
}

# Repos to always skip (this site itself, profile repo, etc.)
SKIP_REPOS = {
    "icepaule.github.io",
    "icepaule",
    ".github",
}

# Regex patterns for sensitive data sanitization
SANITIZE_PATTERNS = [
    # Public IP addresses (not RFC1918)
    (
        r'\b(?!10\.)(?!172\.(?:1[6-9]|2[0-9]|3[01])\.)(?!192\.168\.)'
        r'(?!127\.)(?!0\.)'
        r'(?:(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)\.){3}'
        r'(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)\b',
        'x.x.x.x'
    ),
    # SSH private keys
    (r'-----BEGIN (?:RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----[\s\S]*?-----END (?:RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----',
     '[PRIVATE KEY REMOVED]'),
    # Generic API keys/tokens (long hex/base64 strings that look like secrets)
    (r'(?i)(?:api[_-]?key|api[_-]?token|secret[_-]?key|access[_-]?token|auth[_-]?token)\s*[:=]\s*["\']?([a-zA-Z0-9_\-]{20,})["\']?',
     lambda m: m.group(0).split(m.group(1))[0] + '****'),
    # Password patterns
    (r'(?i)(?:password|passwd|pass)\s*[:=]\s*["\']?([^\s"\']{3,})["\']?',
     lambda m: m.group(0).split(m.group(1))[0] + '****'),
    # Email addresses
    (r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
     '****@****.***'),
]


def run_gh(args, timeout=30):
    """Run a gh CLI command and return stdout."""
    try:
        result = subprocess.run(
            ["gh"] + args,
            capture_output=True, text=True, timeout=timeout
        )
        if result.returncode != 0:
            print(f"  gh error: {result.stderr.strip()}", file=sys.stderr)
            return None
        return result.stdout
    except subprocess.TimeoutExpired:
        print(f"  gh timeout: {' '.join(args)}", file=sys.stderr)
        return None
    except FileNotFoundError:
        print("Error: gh CLI not found. Install it from https://cli.github.com/", file=sys.stderr)
        sys.exit(1)


def get_repos():
    """Fetch all public, non-fork repos for the user."""
    output = run_gh([
        "repo", "list", GITHUB_USER,
        "--json", "name,description,isFork,isPrivate,pushedAt,defaultBranchRef",
        "--limit", "200",
        "--no-archived",
    ], timeout=60)
    if not output:
        return []

    repos = json.loads(output)
    # Filter: public, non-fork, not in skip list
    filtered = []
    for r in repos:
        if r.get("isPrivate"):
            continue
        if r.get("isFork"):
            continue
        if r["name"] in SKIP_REPOS:
            continue
        filtered.append(r)

    print(f"Found {len(filtered)} public non-fork repos (skipped {len(repos) - len(filtered)})")
    return filtered


def get_readme(repo_name):
    """Fetch README content for a repo via gh API."""
    import base64
    output = run_gh([
        "api", f"repos/{GITHUB_USER}/{repo_name}/readme",
        "--jq", ".content",
    ], timeout=30)
    if not output or not output.strip():
        return None
    try:
        content = base64.b64decode(output.strip()).decode("utf-8", errors="replace")
        return content
    except Exception as e:
        print(f"  Could not decode README for {repo_name}: {e}", file=sys.stderr)
        return None


def sanitize_content(text):
    """Remove sensitive data from README content."""
    for pattern, replacement in SANITIZE_PATTERNS:
        if callable(replacement):
            text = re.sub(pattern, replacement, text)
        else:
            text = re.sub(pattern, replacement, text)
    return text


def strip_readme_title(text, repo_name):
    """Remove the first H1 heading if it matches the repo name (we add our own)."""
    lines = text.split('\n')
    for i, line in enumerate(lines):
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith('# '):
            # Remove the first H1
            lines[i] = ''
            break
        else:
            # First non-empty line is not H1, stop
            break
    return '\n'.join(lines).strip()


def get_existing_nav_orders(category):
    """Get all nav_order values used in a category."""
    orders = set()
    for md_file in PROJECTS_DIR.glob("*.md"):
        try:
            content = md_file.read_text(encoding="utf-8")
        except Exception:
            continue
        # Check if this page belongs to the category
        if f"parent: {category}" in content:
            match = re.search(r'nav_order:\s*(\d+)', content)
            if match:
                orders.add(int(match.group(1)))
    return orders


def next_nav_order(category):
    """Find the next available nav_order for a category."""
    existing = get_existing_nav_orders(category)
    order = 1
    while order in existing:
        order += 1
    return order


def is_manually_curated(file_path):
    """Check if a file is manually curated and should not be overwritten."""
    if not file_path.exists():
        return False
    try:
        content = file_path.read_text(encoding="utf-8")
    except Exception:
        return False
    # Explicit marker
    if MANUALLY_CURATED_MARKER in content:
        return True
    # Size check: files > STUB_THRESHOLD are considered curated
    if file_path.stat().st_size > STUB_THRESHOLD:
        return True
    return False


def repo_to_filename(repo_name):
    """Convert repo name to the expected markdown filename."""
    return repo_name.lower().replace(" ", "-") + ".md"


def get_category(repo_name):
    """Get the category for a repo, defaulting to Data & Tools."""
    return CATEGORY_MAP.get(repo_name.lower(), "Data & Tools")


def generate_page(repo, readme_content):
    """Generate a Jekyll markdown page for a repo."""
    name = repo["name"]
    description = repo.get("description") or name
    category = get_category(name)
    nav_order = next_nav_order(category)

    # Sanitize and process README
    if readme_content:
        readme_content = sanitize_content(readme_content)
        readme_content = strip_readme_title(readme_content, name)

    page = f"""---
layout: default
title: {name}
parent: {category}
nav_order: {nav_order}
---

# {name}

[View on GitHub](https://github.com/{GITHUB_USER}/{name}){{: .btn .btn-primary .fs-5 .mb-4 .mb-md-0 .mr-2 }}

***

**{description}**

"""

    if readme_content and readme_content.strip():
        page += readme_content + "\n"
    else:
        page += f"*No README available. Visit the [GitHub repository](https://github.com/{GITHUB_USER}/{name}) for more information.*\n"

    return page


def main():
    print("=== IcePaule Documentation Generator ===\n")

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    PROJECTS_DIR.mkdir(parents=True, exist_ok=True)

    repos = get_repos()
    if not repos:
        print("No repos found. Check gh auth status.")
        sys.exit(1)

    repo_status = []
    created = 0
    updated = 0
    skipped_curated = 0
    skipped_no_readme = 0

    for repo in sorted(repos, key=lambda r: r["name"].lower()):
        name = repo["name"]
        filename = repo_to_filename(name)
        file_path = PROJECTS_DIR / filename
        status_entry = {
            "name": name,
            "description": repo.get("description") or "",
            "pushed_at": repo.get("pushedAt") or "",
            "doc_file": filename,
            "status": "unknown",
        }

        print(f"\nProcessing: {name}")

        # Check if manually curated
        if is_manually_curated(file_path):
            print(f"  SKIP: manually curated ({file_path.stat().st_size} bytes)")
            status_entry["status"] = "curated"
            repo_status.append(status_entry)
            skipped_curated += 1
            continue

        # Fetch README
        readme = get_readme(name)

        if file_path.exists() and not readme:
            # Existing stub, no README available - leave as-is
            print(f"  SKIP: existing page, no README to update")
            status_entry["status"] = "no_readme"
            repo_status.append(status_entry)
            skipped_no_readme += 1
            continue

        # Generate page
        page_content = generate_page(repo, readme)

        if file_path.exists():
            print(f"  UPDATE: {filename}")
            updated += 1
            status_entry["status"] = "auto_updated"
        else:
            print(f"  CREATE: {filename}")
            created += 1
            status_entry["status"] = "auto_created"

        file_path.write_text(page_content, encoding="utf-8")
        repo_status.append(status_entry)

    # Save repo status
    status_file = DATA_DIR / "repo_status.json"
    status_file.write_text(
        json.dumps(repo_status, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

    print(f"\n=== Summary ===")
    print(f"Total repos processed: {len(repos)}")
    print(f"Pages created: {created}")
    print(f"Pages updated: {updated}")
    print(f"Skipped (curated): {skipped_curated}")
    print(f"Skipped (no README): {skipped_no_readme}")
    print(f"Status saved to: {status_file}")


if __name__ == "__main__":
    main()
