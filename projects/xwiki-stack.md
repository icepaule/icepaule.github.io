---
layout: default
title: IceXWiKi - Knowledge Stack
parent: Home Automation & Networking
nav_order: 10
---

# IceXWiKi - Self-Hosted Knowledge Stack

A self-hosted knowledge management platform combining **XWiki** with AI-powered features, infrastructure auto-discovery, GitHub integration, and Confluence migration.

[View on GitHub](https://github.com/icepaule/IceXWiKi){: .btn .btn-primary .fs-5 .mb-4 .mb-md-0 .mr-2 }

---

## Overview

Built as a Docker Compose stack with 5 services, designed for homelab environments. XWiki serves as the central wiki engine, extended by custom FastAPI microservices for GitHub sync, AI features, infrastructure scanning, and RAG-based semantic search.

![XWiki Home](https://raw.githubusercontent.com/icepaule/IceXWiKi/main/docs/screenshots/xwiki-home.png)

## Architecture

| Service | Description | Port |
|:--------|:-----------|:-----|
| **XWiki** | Wiki engine (LTS, PostgreSQL backend) | 8085 |
| **PostgreSQL** | Database backend | 5433 |
| **Bridge** | FastAPI - GitHub sync, AI endpoints, Word import, RAG | 8090 |
| **AutoDoc** | FastAPI - Infrastructure scanning + Web GUI | 8091 |
| **AnythingLLM** | RAG engine with Ollama LLM/embedding provider | 3001 |

External dependency: **Ollama** running on a separate host with `qwen2.5:14b` (LLM) and `nomic-embed-text` (embeddings).

## Bridge API

FastAPI service connecting XWiki to external systems: GitHub repository sync, AI-powered summarization/runbook generation/classification, Word document import, and RAG ingestion via AnythingLLM.

![Bridge Swagger UI](https://raw.githubusercontent.com/icepaule/IceXWiKi/main/docs/screenshots/bridge-swagger.png)

### Key Endpoints

| Endpoint | Method | Description |
|:---------|:-------|:-----------|
| `/api/github/sync` | POST | Sync GitHub repos to XWiki pages |
| `/api/import/word` | POST | Import DOCX files as wiki pages |
| `/api/ai/summarize` | POST | AI-powered text summarization |
| `/api/ai/runbook` | POST | Generate runbooks from notes |
| `/api/ai/classify` | POST | Classify content categories |
| `/api/rag/ingest-space` | POST | Ingest XWiki space into AnythingLLM |

### GitHub Sync Result

All GitHub repositories are automatically imported as XWiki pages with README content, language breakdown, and metadata:

![GitHub Space in XWiki](https://raw.githubusercontent.com/icepaule/IceXWiKi/main/docs/screenshots/xwiki-github-space.png)

## AutoDoc - Infrastructure Auto-Discovery

Automated infrastructure scanning with web GUI, scheduled scans, and AI-annotated reports written directly to XWiki.

![AutoDoc Web GUI](https://raw.githubusercontent.com/icepaule/IceXWiKi/main/docs/screenshots/autodoc-gui.png)

### Scanners

| Scanner | Method | Discovers |
|:--------|:-------|:----------|
| Docker | Docker API (socket + TCP) | Containers, images, networks, volumes |
| Network | nmap | Subnet hosts, open ports, services |
| ESXi | SSH (paramiko, RSA key) | VMs, datastores, networking |
| Synology | SSH (paramiko, ed25519) | Volumes, shares, packages |

### AutoDoc API

![AutoDoc Swagger UI](https://raw.githubusercontent.com/icepaule/IceXWiKi/main/docs/screenshots/autodoc-swagger.png)

## Confluence Migration

Standalone Python script to bulk-migrate all Confluence spaces to XWiki, including content conversion and attachment transfer.

![Migrated Confluence Spaces](https://raw.githubusercontent.com/icepaule/IceXWiKi/main/docs/screenshots/xwiki-confluence-spaces.png)

### Capabilities

- Pagination support for large spaces (1300+ pages tested)
- Confluence Storage Format (XHTML) to XWiki 2.1 syntax conversion
- Attachment migration with content-type preservation
- Macro mapping: `tip` → `success`, `note` → `warning`, `info`/`warning`/`error` preserved
- Handles headings, bold, italic, code blocks, tables, links, images
- Post-migration macro fix script for already-migrated pages

### Usage

```bash
# Migrate all spaces
export $(grep -v '^#' .env | xargs)
python3 scripts/migrate_confluence.py --space ALL

# Dry run for a single space
python3 scripts/migrate_confluence.py --space NETOPS --dry-run

# Fix macros in already-migrated pages
python3 scripts/fix_macros.py
```

## Quick Start

```bash
git clone https://github.com/icepaule/IceXWiKi.git
cd IceXWiKi
cp .env.example .env
# Edit .env with your actual values (passwords, IPs, tokens)
make setup
# or: docker compose up -d --build
```

Wait ~2 minutes for XWiki initialization, then access:
- **XWiki**: `http://YOUR_HOST:8085`
- **Bridge API**: `http://YOUR_HOST:8090/docs`
- **AutoDoc**: `http://YOUR_HOST:8091`
- **AnythingLLM**: `http://YOUR_HOST:3001`

## Makefile Targets

```bash
make up           # Start all services
make down         # Stop all services
make restart      # Restart all services
make logs         # Follow logs
make build        # Build custom images
make github-sync  # Trigger GitHub repo sync
make scan-all     # Run all AutoDoc scans
make scan-docker  # Run Docker scan only
make clean        # Remove containers and volumes
```

## Requirements

- Docker Engine 24+ with Compose v2
- Ollama instance with `qwen2.5:14b` and `nomic-embed-text` models
- ~4 GB RAM for the stack
- ~10 GB disk for XWiki data, PostgreSQL, and AnythingLLM

**Optional:** SSH key access to ESXi/Synology (for AutoDoc), Docker TCP API on remote hosts, Confluence server (for migration), GitHub account (for repo sync).

## Security

- No secrets in the repository - all credentials are in `.env` (gitignored)
- XWiki REST API uses Basic Auth
- SSH scanning uses key-based authentication (keys mounted as volumes)
- Docker socket is mounted read-only

---

*Built with Docker Compose, FastAPI, XWiki LTS, and Ollama AI*
