---
layout: default
title: XWiki Knowledge Stack
parent: Home Automation & Networking
nav_order: 10
---

# XWiki Knowledge Stack

A self-hosted knowledge management platform combining XWiki with AI-powered features for homelab infrastructure documentation.

[View on GitHub](https://github.com/icepaule/xwiki-stack){: .btn .btn-primary .fs-5 .mb-4 .mb-md-0 .mr-2 }

---

## Architecture

```
                    +-------------------+
                    |    AnythingLLM    |
                    |   (RAG Engine)    |
                    |    Port 3001      |
                    +--------+----------+
                             |
+----------+    +------------+------------+    +-----------+
|  Ollama  |<-->|    Bridge (FastAPI)     |<-->|  XWiki    |
| (AI/LLM) |    |    Port 8090           |    | Port 8085 |
+----------+    +------------------------+    +-----+-----+
                                                    |
+----------+    +------------------------+    +-----+-----+
| Docker   |<-->|   AutoDoc (FastAPI)    |<-->| PostgreSQL|
| Socket   |    |    Port 8091           |    | Port 5433 |
+----------+    +------------------------+    +-----------+
```

## Components

| Service | Description | Port |
|:--------|:-----------|:-----|
| **XWiki** | Wiki engine (LTS, PostgreSQL backend) | 8085 |
| **PostgreSQL** | Database for XWiki | 5433 |
| **Bridge** | FastAPI middleware - GitHub sync, AI endpoints, Word import, RAG ingest | 8090 |
| **AutoDoc** | Infrastructure auto-discovery - Docker, Network, ESXi, Synology scanning | 8091 |
| **AnythingLLM** | RAG engine with Ollama as LLM/embedding provider | 3001 |

## Features

### GitHub Repository Sync
Automatically imports all GitHub repositories as XWiki pages including README content, language breakdown, and metadata.

### AI-Powered Endpoints
- **Summarize** - Condense technical documents
- **Runbook Generator** - Create operational runbooks from notes
- **Classify** - Categorize content (Network, Security, Storage, etc.)

### Infrastructure Auto-Discovery (AutoDoc)
Scheduled scans with AI analysis:
- **Docker** - Containers, networks, volumes via Docker socket
- **Network** - Subnet discovery via nmap
- **ESXi** - VMs, datastores, networking via SSH
- **Synology** - Volumes, shares, packages via SSH

### Confluence Migration
Standalone script to migrate Confluence spaces to XWiki with content conversion and attachment support.

### RAG Integration
Ingest XWiki spaces/pages into AnythingLLM workspaces for semantic search and AI-assisted knowledge retrieval.

## Quick Start

```bash
git clone https://github.com/icepaule/xwiki-stack.git
cd xwiki-stack
cp .env.example .env
# Edit .env with your actual values
make setup
```

## API Documentation

After deployment, Swagger UI is available at:
- Bridge: `http://YOUR_HOST:8090/docs`
- AutoDoc: `http://YOUR_HOST:8091/docs`

### Key Endpoints

```bash
# Sync all GitHub repos to XWiki
curl -X POST http://HOST:8090/api/github/sync

# Sync specific repos
curl -X POST http://HOST:8090/api/github/sync \
  -H "Content-Type: application/json" \
  -d '{"repos": ["repo-name"]}'

# AI summarize
curl -X POST http://HOST:8090/api/ai/summarize \
  -H "Content-Type: application/json" \
  -d '{"text": "Your text here..."}'

# Run Docker scan
curl -X POST http://HOST:8091/api/scan/docker

# Run all scans
curl -X POST http://HOST:8091/api/scan/all
```

## Stack Details

- **XWiki**: LTS release with PostgreSQL backend
- **Bridge/AutoDoc**: Python 3.13 + FastAPI + uvicorn
- **AI Backend**: Ollama (external) with qwen2.5:14b and nomic-embed-text
- **Scanning**: python-nmap, paramiko (SSH), Docker SDK
- **Scheduling**: APScheduler for periodic infrastructure scans

## Configuration

All configuration is done via environment variables in `.env` (not committed). See `.env.example` for all available options.

---

*Built with Docker Compose, FastAPI, and XWiki LTS*
