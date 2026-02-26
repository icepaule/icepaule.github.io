---
layout: default
title: Ice-GitHub-Doku
parent: Data & Tools
nav_order: 6
---

# Ice-GitHub-Doku

[View on GitHub](https://github.com/icepaule/Ice-GitHub-Doku){: .btn .btn-primary .fs-5 .mb-4 .mb-md-0 .mr-2 }

***

**Ice-GitHub-Doku**

Portable Build-Script for automated GitHub Pages generation with integrated TruffleHog security scanning.

Scans all public repositories for leaked secrets, fetches README content, and generates a complete Jekyll site (just-the-docs theme) — ready to push to `<username>.github.io`.

## Features

- **TruffleHog Security Gate** — Scans all repos for verified secrets before building; auto-installs if not present
- **Automatic Repo Discovery** — Finds all public source repos via GitHub API
- **Category Mapping** — Configurable repo-to-category mapping via `categories.conf`
- **README Fetching** — Pulls and sanitizes README content for each project page
- **Jekyll Generation** — Generates `_config.yml`, `Gemfile`, category pages, project pages, and `index.md`
- **Dry-Run Mode** — Generate without pushing to verify output
- **Portable** — Runs on any Linux/macOS with Bash 4+, git, gh, jq, curl

## Quick Start

### 1. Clone this repo

```bash
git clone https://github.com/icepaule/Ice-GitHub-Doku.git
cd Ice-GitHub-Doku
```

### 2. Create a GitHub Token

Go to [github.com/settings/tokens/new](https://github.com/settings/tokens/new) and create a token with these scopes:

| Scope | Purpose |
|-------|---------|
| `repo` | Clone/push to the site repository |
| `read:org` | TruffleHog org-wide secret scanning |

### 3. Configure the `.env` file

```bash
cp .env.example .env
# Edit .env and paste your token:
nano .env
```

The `.env` file is automatically loaded by the script and excluded from git via `.gitignore`.

### 4. Test with dry-run

```bash
chmod +x build-ghpages.sh
./build-ghpages.sh --dry-run
```

### 5. Build and push

```bash
./build-ghpages.sh
```

## Prerequisites

| Tool | Purpose | Install |
|------|---------|---------|
| `bash` 4+ | Script runtime | Pre-installed on most systems |
| `git` | Repository operations | `apt install git` |
| `gh` | GitHub CLI (API, clone, push) | [cli.github.com](https://cli.github.com/) |
| `jq` | JSON processing | `apt install jq` |
| `curl` | HTTP requests | `apt install curl` |
| `base64` | README content decoding | Part of coreutils |
| `trufflehog` | Secret scanning | **Auto-installed** by the script |

### One-liner install (Debian/Ubuntu)

```bash
apt update && apt install -y git jq curl
# gh CLI:
curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg \
  | dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" \
  | tee /etc/apt/sources.list.d/github-cli.list > /dev/null
apt update && apt install -y gh
```

TruffleHog is installed automatically on first run.

## Usage

```
Usage: build-ghpages.sh [OPTIONS]

Options:
  --dry-run       Generate site without pushing to GitHub
  --user USER     GitHub username (default: icepaule)
  --skip-scan     Skip TruffleHog security scan
  -h, --help      Show this help message
```

### Environment Variables

All configuration can be overridden via the `.env` file or environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `GH_TOKEN` | *(required)* | GitHub Personal Access Token |
| `GITHUB_USER` | `icepaule` | GitHub username |
| `SITE_REPO` | `<user>.github.io` | Target site repository |
| `CLONE_DIR` | `/tmp/<site-repo>` | Local clone directory |
| `CATEGORIES_CONF` | `./categories.conf` | Path to category mapping |

### Examples

```bash
# Standard build
./build-ghpages.sh

# Dry-run (generate without push)
./build-ghpages.sh --dry-run

# Different user
./build-ghpages.sh --user another-user

# Skip security scan (faster, not recommended)
./build-ghpages.sh --skip-scan

# Override via environment
CLONE_DIR=/opt/site ./build-ghpages.sh --dry-run
```

## Build Phases

The script runs 9 sequential phases:

| Phase | Name | Description |
|-------|------|-------------|
| 0 | Dependency Check | Verifies all tools; auto-installs TruffleHog |
| 1 | Authentication | Validates GitHub token from `.env` or environment |
| 2 | TruffleHog Scan | Scans all repos for verified leaked secrets |
| 3 | Repo Discovery | Fetches public source repos via `gh repo list` |
| 4 | Category Mapping | Loads `categories.conf`; generates default if missing |
| 5 | README Fetching | Downloads and sanitizes README for each repo |
| 6 | Jekyll Generation | Creates `_config.yml`, pages, and `index.md` |
| 7 | Git Operations | Clones site repo, copies content, commits, pushes |
| 8 | Summary | Prints all project URLs grouped by category |

### TruffleHog Security Gate (Phase 2)

- Attempts org-wide scan first: `trufflehog github --org=<user> --only-verified`
- Falls back to per-repo scanning if org scan fails
- Generates a JSON report at `/tmp/trufflehog-report-<timestamp>.json`
- **Interactive mode**: Prompts to continue or abort on findings
- **Non-interactive mode** (CI/cron): Aborts on any finding

## Category Configuration

Edit `categories.conf` to map repositories to categories:

```
# Format: REPONAME|CATEGORY_KEY
IcePorge|security
IceHomeAssist|homeautomation
Ice-MTastik|mesh
IceTimereport|data
followmysun|hardware
```

Available category keys:

| Key | Display Name |
|-----|-------------|
| `security` | Security & Malware Analysis |
| `homeautomation` | Home Automation & Networking |
| `mesh` | Mesh & Communication |
| `data` | Data & Tools |
| `hardware` | Hardware & ESP32 |

Repos not listed in `categories.conf` are discovered but skipped with a warning, making it easy to identify new repos that need categorization.

## Generated Site Structure

```
<site-repo>/
├── _config.yml          # Jekyll config (just-the-docs dark theme)
├── Gemfile              # Ruby dependencies for GitHub Pages
├── index.md             # Homepage with project table by category
└── projects/
    ├── security.md      # Category parent page
    ├── IcePorge.md      # Project page with README content
    ├── IcePorge-Cockpit.md
    └── ...
```

Each project page includes:
- Repository description
- Link to GitHub source
- Full sanitized README content

## Deploying to Another Server

1. Clone this repo
2. Install prerequisites (see above)
3. Create `.env` with your GitHub token
4. Adjust `categories.conf` for your repos (or delete it — a default will be auto-generated)
5. Run `./build-ghpages.sh --dry-run` to verify
6. Run `./build-ghpages.sh` to push

### Automation (Cron)

```bash
# Rebuild site daily at 2:00 AM
0 2 * * * cd /opt/Ice-GitHub-Doku && ./build-ghpages.sh >> /var/log/ghpages-build.log 2>&1
```

Note: In non-interactive mode (cron), the script aborts if TruffleHog finds verified secrets.

## File Overview

| File | Description |
|------|-------------|
| `build-ghpages.sh` | Main build script |
| `categories.conf` | Repo-to-category mapping |
| `.env.example` | Template for environment configuration |
| `.env` | Your local configuration (git-ignored) |
| `.gitignore` | Excludes `.env` and build artifacts |

## License

MIT
