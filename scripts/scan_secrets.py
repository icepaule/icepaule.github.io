#!/usr/bin/env python3
"""
scan_secrets.py - TruffleHog secret scanner for icepaule GitHub repos.

Scans all public repos for leaked secrets using TruffleHog.
NEVER stores actual secret values - only metadata and finding hashes.
"""

import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = REPO_ROOT / "_data"
GITHUB_USER = "icepaule"
SCAN_TIMEOUT = 300  # 5 minutes per repo
SKIP_REPOS = {"icepaule.github.io", "icepaule", ".github"}


def run_gh(args, timeout=60):
    """Run a gh CLI command and return stdout."""
    try:
        result = subprocess.run(
            ["gh"] + args,
            capture_output=True, text=True, timeout=timeout
        )
        if result.returncode != 0:
            return None
        return result.stdout
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return None


def get_repos(include_forks=False):
    """Fetch all public repos for the user."""
    output = run_gh([
        "repo", "list", GITHUB_USER,
        "--json", "name,isFork,isPrivate",
        "--limit", "200",
        "--no-archived",
    ], timeout=60)
    if not output:
        return []

    repos = json.loads(output)
    filtered = []
    for r in repos:
        if r.get("isPrivate"):
            continue
        if not include_forks and r.get("isFork"):
            continue
        if r["name"] in SKIP_REPOS:
            continue
        filtered.append(r["name"])
    return sorted(filtered)


def compute_finding_hash(detector, repo, raw_result):
    """Create a stable hash for deduplication. NEVER includes the actual secret."""
    key_parts = [
        detector,
        repo,
        raw_result.get("SourceMetadata", {}).get("Data", {}).get("Git", {}).get("file", ""),
        raw_result.get("SourceMetadata", {}).get("Data", {}).get("Git", {}).get("commit", ""),
        str(raw_result.get("SourceMetadata", {}).get("Data", {}).get("Git", {}).get("line", "")),
    ]
    return hashlib.sha256("|".join(key_parts).encode()).hexdigest()[:16]


def scan_repo(repo_name):
    """Run TruffleHog on a single repo. Returns list of safe finding records."""
    repo_url = f"https://github.com/{GITHUB_USER}/{repo_name}.git"
    print(f"  Scanning {repo_name}...", end=" ", flush=True)

    try:
        result = subprocess.run(
            ["trufflehog", "git", repo_url, "--json", "--no-update"],
            capture_output=True, text=True, timeout=SCAN_TIMEOUT
        )
    except subprocess.TimeoutExpired:
        print(f"TIMEOUT ({SCAN_TIMEOUT}s)")
        return [{"repo": repo_name, "error": "timeout", "detector": "TIMEOUT"}]
    except FileNotFoundError:
        print("ERROR: trufflehog not found")
        sys.exit(1)

    findings = []
    for line in result.stdout.strip().split('\n'):
        if not line.strip():
            continue
        try:
            raw = json.loads(line)
        except json.JSONDecodeError:
            continue

        detector_type = raw.get("DetectorType", "Unknown")
        if isinstance(detector_type, dict):
            detector_type = detector_type.get("name", "Unknown")
        detector = raw.get("DetectorName", str(detector_type))
        verified = raw.get("Verified", False)
        finding_hash = compute_finding_hash(detector, repo_name, raw)

        # SAFE record - no actual secret values
        findings.append({
            "repo": repo_name,
            "detector": detector,
            "verified": verified,
            "hash": finding_hash,
            "file": raw.get("SourceMetadata", {}).get("Data", {}).get("Git", {}).get("file", ""),
            "commit": raw.get("SourceMetadata", {}).get("Data", {}).get("Git", {}).get("commit", "")[:8],
        })

    count = len(findings)
    if count > 0:
        verified_count = sum(1 for f in findings if f.get("verified"))
        print(f"{count} findings ({verified_count} verified)")
    else:
        print("clean")

    return findings


def load_previous_findings():
    """Load previously known finding hashes."""
    path = DATA_DIR / "previous_findings.json"
    if path.exists():
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            return set(data.get("hashes", []))
        except (json.JSONDecodeError, KeyError):
            pass
    return set()


def save_previous_findings(all_hashes):
    """Save all known finding hashes for future deduplication."""
    path = DATA_DIR / "previous_findings.json"
    data = {
        "updated": datetime.now(timezone.utc).isoformat(),
        "hashes": sorted(all_hashes),
    }
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def main():
    print("=== IcePaule Secret Scanner ===\n")
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    repos = get_repos(include_forks=False)
    if not repos:
        print("No repos found. Check gh auth status.")
        sys.exit(1)

    print(f"Scanning {len(repos)} repos...\n")

    previous_hashes = load_previous_findings()
    all_findings = []
    new_findings = []
    repos_with_findings = set()
    repos_clean = set()

    for repo_name in repos:
        findings = scan_repo(repo_name)
        if findings:
            has_real_finding = any(f.get("detector") != "TIMEOUT" for f in findings)
            if has_real_finding:
                repos_with_findings.add(repo_name)
            all_findings.extend(findings)
            for f in findings:
                h = f.get("hash", "")
                if h and h not in previous_hashes:
                    new_findings.append(f)
        else:
            repos_clean.add(repo_name)

    # Collect all hashes (previous + new)
    current_hashes = previous_hashes.copy()
    for f in all_findings:
        h = f.get("hash", "")
        if h:
            current_hashes.add(h)

    # Save results (safe - no secret values)
    scan_results = {
        "scan_date": datetime.now(timezone.utc).isoformat(),
        "total_repos": len(repos),
        "clean_repos": len(repos_clean),
        "repos_with_findings": len(repos_with_findings),
        "total_findings": len(all_findings),
        "new_findings": len(new_findings),
        "verified_findings": sum(1 for f in all_findings if f.get("verified")),
        "findings": all_findings,
        "new_finding_details": new_findings,
    }

    results_file = DATA_DIR / "scan_results.json"
    results_file.write_text(
        json.dumps(scan_results, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

    save_previous_findings(current_hashes)

    print(f"\n=== Scan Summary ===")
    print(f"Total repos scanned: {len(repos)}")
    print(f"Clean repos: {len(repos_clean)}")
    print(f"Repos with findings: {len(repos_with_findings)}")
    print(f"Total findings: {len(all_findings)}")
    print(f"New findings: {len(new_findings)}")
    print(f"Verified findings: {scan_results['verified_findings']}")
    print(f"Results saved to: {results_file}")

    # Exit code 0 = success (even with findings)
    # The notification script handles alerting
    return 0


if __name__ == "__main__":
    sys.exit(main())
