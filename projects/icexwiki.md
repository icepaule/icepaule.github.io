---
layout: default
title: IceXWiKi
parent: Home Automation & Networking
nav_order: 6
---

# IceXWiKi

[View on GitHub](https://github.com/icepaule/IceXWiKi){: .btn .btn-primary .fs-5 .mb-4 .mb-md-0 .mr-2 }

***

**IceXWiKi**

A self-hosted knowledge management platform combining **XWiki** with AI-powered features, infrastructure auto-discovery, GitHub integration, and Confluence migration.

Built as a Docker Compose stack with 5 services, designed for homelab environments.

![XWiki Home](docs/screenshots/xwiki-home.png)

## Features

- **XWiki Wiki Engine** - Full-featured wiki with PostgreSQL backend
- **Bridge API** - FastAPI middleware connecting XWiki to GitHub, Ollama AI, Word import, and AnythingLLM RAG
- **AutoDoc** - Automated infrastructure discovery (Docker, Network, ESXi, Synology) with AI-annotated reports
- **Confluence Migration** - Bulk migrate all Confluence spaces including attachments and content conversion
- **RAG Integration** - Ingest wiki content into AnythingLLM for semantic search

## Architecture

The stack consists of 5 Docker containers:

| Service | Description | Port |
|:--------|:-----------|:-----|
| **XWiki** | Wiki engine (LTS, PostgreSQL backend) | 8085 |
| **PostgreSQL** | Database backend | 5433 |
| **Bridge** | FastAPI - GitHub sync, AI endpoints, Word import, RAG | 8090 |
| **AutoDoc** | FastAPI - Infrastructure scanning + Web GUI | 8091 |
| **AnythingLLM** | RAG engine with Ollama LLM/embedding provider | 3001 |

External dependency: **Ollama** running on a separate host with `qwen2.5:14b` and `nomic-embed-text` models.

## Screenshots

### Bridge API (Swagger UI)

![Bridge Swagger](docs/screenshots/bridge-swagger.png)

### AutoDoc Web GUI

![AutoDoc GUI](docs/screenshots/autodoc-gui.png)

### AutoDoc API (Swagger UI)

![AutoDoc Swagger](docs/screenshots/autodoc-swagger.png)

## Quick Start

```bash
git clone https://github.com/icepaule/IceXWiKi.git
cd IceXWiKi

# Configure environment
cp .env.example .env
# Edit .env with your actual values (passwords, IPs, tokens)

# Build and start
make setup
# or: docker compose up -d --build

# Wait ~2 minutes for XWiki initialization, then open:
# XWiki:    http://YOUR_HOST:8085
# Bridge:   http://YOUR_HOST:8090/docs
# AutoDoc:  http://YOUR_HOST:8091
```

## Configuration

All configuration is via environment variables in `.env` (never committed). Copy `.env.example` and fill in your values:

| Variable | Description | Example |
|:---------|:-----------|:--------|
| `XWIKI_PORT` | XWiki web port | `8085` |
| `XWIKI_ADMIN_USER` | XWiki admin username | `admin` |
| `XWIKI_ADMIN_PASSWORD` | XWiki admin password | `CHANGEME` |
| `OLLAMA_URL` | Ollama API endpoint | `http://ollama-host:11434` |
| `OLLAMA_MODEL` | LLM model for AI features | `qwen2.5:14b` |
| `DOCKER_HOSTS` | Remote Docker TCP endpoints | `tcp://nas:2375` |
| `SCAN_SUBNETS` | Subnets for network scanning | `192.168.1.0/24` |
| `GITHUB_USER` | GitHub username for repo sync | `your-user` |
| `GITHUB_TOKEN` | GitHub personal access token | *(optional, for private repos)* |
| `CONFLUENCE_URL` | Confluence server URL | `http://confluence:8090` |

See [.env.example](.env.example) for all available options.

## Services in Detail

### Bridge API (Port 8090)

FastAPI service connecting XWiki to external systems.

**Endpoints:**

| Endpoint | Method | Description |
|:---------|:-------|:-----------|
| `/api/github/sync` | POST | Sync GitHub repos to XWiki pages |
| `/api/import/word` | POST | Import DOCX files as wiki pages |
| `/api/ai/summarize` | POST | AI-powered text summarization |
| `/api/ai/runbook` | POST | Generate runbooks from notes |
| `/api/ai/classify` | POST | Classify content categories |
| `/api/rag/ingest-space` | POST | Ingest XWiki space into AnythingLLM |

### AutoDoc (Port 8091)

Infrastructure auto-discovery service with web GUI and scheduled scanning.

**Scanners:**

| Scanner | Method | Description |
|:--------|:-------|:-----------|
| Docker | Docker API (socket + TCP) | Containers, images, networks, volumes |
| Network | nmap | Subnet discovery, service detection |
| ESXi | SSH (paramiko, RSA key) | VMs, datastores, networking |
| Synology | SSH (paramiko, ed25519) | Volumes, shares, packages |

**Features:**
- Web GUI for manual scans and configuration
- APScheduler for periodic automated scans
- AI analysis of scan results via Ollama
- Results written as XWiki pages under `AutoDoc/` space

### Confluence Migration

Standalone Python script to migrate Confluence spaces to XWiki.

```bash
# Migrate all spaces
export $(grep -v '^#' .env | xargs)
python3 scripts/migrate_confluence.py --space ALL

# Dry run for a single space
python3 scripts/migrate_confluence.py --space NETOPS --dry-run
```

**Capabilities:**
- Pagination support for large spaces
- Confluence Storage Format (XHTML) to XWiki 2.1 syntax conversion
- Attachment migration with content-type preservation
- Macro mapping: `tip` -> `success`, `note` -> `warning`, `info`/`warning` preserved
- Handles headings, bold, italic, code blocks, tables, links, images

### AnythingLLM (Port 3001)

RAG engine for semantic search across wiki content. Configured to use Ollama as both LLM and embedding provider.

## Project Structure

```
IceXWiKi/
├── docker-compose.yml        # 5 services orchestration
├── .env.example              # Configuration template
├── Makefile                  # Shortcuts (up, down, sync, scan)
├── bridge/                   # Bridge FastAPI service
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app/
│       ├── main.py           # App + health + router includes
│       ├── config.py         # Pydantic settings from ENV
│       ├── routers/          # API endpoints
│       │   ├── github_sync.py
│       │   ├── word_import.py
│       │   ├── ai_endpoints.py
│       │   └── anythingllm.py
│       └── services/         # External client libraries
│           ├── xwiki_client.py
│           ├── ollama_client.py
│           ├── github_client.py
│           └── anythingllm_client.py
├── autodoc/                  # AutoDoc FastAPI service
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app/
│       ├── main.py           # App + GUI + scan endpoints
│       ├── config.py
│       ├── scheduler.py      # APScheduler periodic jobs
│       ├── scanners/         # Infrastructure scanners
│       │   ├── docker_scanner.py
│       │   ├── network_scanner.py
│       │   ├── esxi_scanner.py
│       │   └── synology_scanner.py
│       ├── services/
│       │   ├── xwiki_writer.py
│       │   └── ollama_analyzer.py
│       └── static/
│           └── index.html    # AutoDoc Web GUI
├── scripts/
│   ├── setup.sh              # Initial setup script
│   ├── migrate_confluence.py # Confluence migration
│   └── fix_macros.py         # Fix unsupported macros
└── docs/
    └── screenshots/          # Documentation images
```

## Makefile Targets

```bash
make up          # Start all services
make down        # Stop all services
make restart     # Restart all services
make logs        # Follow logs
make build       # Build custom images
make ps          # Show container status
make github-sync # Trigger GitHub repo sync
make scan-all    # Run all AutoDoc scans
make scan-docker # Run Docker scan only
make scan-network # Run network scan only
make clean       # Remove containers and volumes
```

## Requirements

- Docker Engine 24+ with Compose v2
- Ollama instance with `qwen2.5:14b` and `nomic-embed-text` models
- ~4 GB RAM for the stack
- ~10 GB disk for XWiki data, PostgreSQL, and AnythingLLM

**Optional:**
- SSH key access to ESXi and Synology hosts (for AutoDoc scanning)
- Docker TCP API enabled on remote hosts (for remote container scanning)
- Confluence server (for migration)
- GitHub account (for repo sync)

## Security Notes

- **No secrets in this repository** - all credentials are in `.env` (gitignored)
- `.env.example` contains only placeholder values
- XWiki REST API uses Basic Auth
- SSH scanning uses key-based authentication (keys mounted as volumes)
- Docker socket is mounted read-only

## License

MIT
