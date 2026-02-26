#!/usr/bin/env python3
"""
notify_pushover.py - Pushover notification for new secret findings.

Sends notifications only for NEW findings (not previously known).
Graceful degradation: missing credentials = warning, no crash.
"""

import json
import os
import sys
from pathlib import Path

import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = REPO_ROOT / "_data"
SCAN_RESULTS_FILE = DATA_DIR / "scan_results.json"
PUSHOVER_API_URL = "https://api.pushover.net/1/messages.json"


def get_credentials():
    """Get Pushover credentials from environment."""
    user_key = os.environ.get("PUSHOVER_USER_KEY", "")
    api_token = os.environ.get("PUSHOVER_API_TOKEN", "")
    return user_key, api_token


def load_scan_results():
    """Load the latest scan results."""
    if not SCAN_RESULTS_FILE.exists():
        print("No scan results found.")
        return None
    try:
        return json.loads(SCAN_RESULTS_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as e:
        print(f"Error reading scan results: {e}", file=sys.stderr)
        return None


def format_message(results):
    """Format an HTML message for Pushover."""
    new_findings = results.get("new_finding_details", [])
    if not new_findings:
        return None, None

    verified = [f for f in new_findings if f.get("verified")]
    unverified = [f for f in new_findings if not f.get("verified")]

    # Determine priority
    if verified:
        priority = 1  # High priority for verified findings
    else:
        priority = 0  # Normal priority for unverified

    # Build HTML message
    lines = [f"<b>{len(new_findings)} new secret finding(s)</b>\n"]

    if verified:
        lines.append(f"<b>VERIFIED ({len(verified)}):</b>")
        repos_detectors = {}
        for f in verified:
            repo = f.get("repo", "unknown")
            detector = f.get("detector", "unknown")
            repos_detectors.setdefault(repo, set()).add(detector)
        for repo, detectors in sorted(repos_detectors.items()):
            lines.append(f"  {repo}: {', '.join(sorted(detectors))}")

    if unverified:
        lines.append(f"\n<b>Unverified ({len(unverified)}):</b>")
        repos_detectors = {}
        for f in unverified:
            repo = f.get("repo", "unknown")
            detector = f.get("detector", "unknown")
            repos_detectors.setdefault(repo, set()).add(detector)
        for repo, detectors in sorted(repos_detectors.items()):
            lines.append(f"  {repo}: {', '.join(sorted(detectors))}")

    lines.append(f"\nScan: {results.get('scan_date', 'unknown')[:10]}")
    lines.append(f"Total repos: {results.get('total_repos', 0)}")

    message = "\n".join(lines)
    return message, priority


def send_pushover(user_key, api_token, message, priority=0):
    """Send a Pushover notification."""
    payload = {
        "token": api_token,
        "user": user_key,
        "title": "IcePaule Secret Scanner",
        "message": message,
        "html": 1,
        "priority": priority,
        "sound": "siren" if priority >= 1 else "pushover",
    }

    try:
        resp = requests.post(PUSHOVER_API_URL, data=payload, timeout=30)
        resp.raise_for_status()
        result = resp.json()
        if result.get("status") == 1:
            print("Pushover notification sent successfully.")
            return True
        else:
            print(f"Pushover error: {result}", file=sys.stderr)
            return False
    except requests.RequestException as e:
        print(f"Pushover request failed: {e}", file=sys.stderr)
        return False


def main():
    print("=== IcePaule Pushover Notifier ===\n")

    # Check credentials
    user_key, api_token = get_credentials()
    if not user_key or not api_token:
        print("WARNING: Pushover credentials not configured.")
        print("Set PUSHOVER_USER_KEY and PUSHOVER_API_TOKEN environment variables.")
        print("Skipping notification.")
        return 0

    # Load scan results
    results = load_scan_results()
    if not results:
        print("No scan results to report.")
        return 0

    new_count = results.get("new_findings", 0)
    if new_count == 0:
        print("No new findings. No notification needed.")
        return 0

    print(f"Found {new_count} new finding(s). Preparing notification...")

    # Format and send
    message, priority = format_message(results)
    if not message:
        print("No message to send.")
        return 0

    success = send_pushover(user_key, api_token, message, priority)
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
