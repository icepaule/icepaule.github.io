---
layout: default
title: IceSpider
parent: Data & Tools
nav_order: 17
---

# IceSpider

[View on GitHub](https://github.com/icepaule/IceSpider){: .btn .btn-primary .fs-5 .mb-4 .mb-md-0 .mr-2 }

***

**IceSpider**

An enhanced SpiderFoot deployment with Ollama AI integration for intelligent OSINT analysis, automated correlation, and comprehensive reporting.

## Features

- **SpiderFoot Full** with all 230+ OSINT modules and CLI tools (Nmap, Nuclei, WhatWeb, testssl.sh, etc.)
- **Ollama AI Integration** - Custom SpiderFoot modules that use local LLM for:
  - Automated threat assessment of findings
  - Intelligent entity extraction from unstructured data
  - AI-powered scan summarization and reporting
  - Cross-finding correlation and pattern detection
- **Additional OSINT Modules**:
  - `sfp_abuseipdb` - AbuseIPDB IP reputation lookups
  - `sfp_cve_enrich` - CVE enrichment via NVD/NIST API
  - `sfp_ollama_analyzer` - AI threat analysis of malicious findings
  - `sfp_ollama_summarizer` - AI scan summary generation
  - `sfp_ollama_entities` - AI entity extraction from web content
- **Custom Correlation Rules** for enhanced pattern detection
- **Orchestrator Scripts** for automated scanning and AI-powered reporting
- **Tor Proxy** for dark web OSINT modules
- **Nginx Reverse Proxy** with basic auth and TLS

## Architecture

```
+-------------------+       +-------------------+       +-------------------+
|   Nginx Proxy     |------>|   SpiderFoot      |------>|   Ollama LLM      |
|   (Port 443/80)   |       |   (Port 5001)     |       |   (10.10.0.210)   |
+-------------------+       +-------------------+       +-------------------+
                                    |                           |
                            +-------+-------+           +-------+-------+
                            |  SQLite DB    |           | llama3 / mistral |
                            |  Custom Mods  |           | AI Analysis      |
                            |  Correlations |           +-------------------+
                            +---------------+
                                    |
                            +-------+-------+
                            |   Tor Proxy   |
                            |  (Port 9050)  |
                            +---------------+
```

## Quick Start

### 1. Prerequisites

- Docker and Docker Compose
- Ollama running on `10.10.0.210:11434` with a model pulled (e.g., `llama3:8b`)
- (Optional) API keys for enhanced OSINT sources

### 2. Deploy

```bash
# Clone the repository
git clone https://github.com/icepaule/IceSpider.git
cd IceSpider

# Copy and edit environment configuration
cp config/env.example .env
nano .env  # Add your API keys

# Generate self-signed TLS cert (or add your own to certs/)
./scripts/generate-cert.sh

# Build and start
docker-compose up -d --build

# Verify Ollama connectivity
docker-compose exec spiderfoot python -c "
import requests
r = requests.get('http://10.10.0.210:11434/api/tags')
print('Ollama models:', [m['name'] for m in r.json().get('models', [])])
"
```

### 3. Access

- **Web UI**: https://localhost (via Nginx) or http://localhost:5001 (direct)
- Default credentials (change in `.env`): `icespider` / `IceSpider2024!`

### 4. Configure API Keys

Open the SpiderFoot web UI, go to **Settings** and add API keys for maximum coverage:

| Priority | Source | Free Tier |
|----------|--------|-----------|
| 1 | Shodan | 100 queries/month |
| 2 | VirusTotal | 4 req/min, 500/day |
| 3 | AlienVault OTX | Unlimited |
| 4 | GreyNoise Community | Unlimited |
| 5 | Censys | 250 queries/month |
| 6 | SecurityTrails | 50 queries/month |
| 7 | ipinfo.io | 50k req/month |
| 8 | urlscan.io | 100 scans/day |
| 9 | AbuseIPDB | 1000 checks/day |
| 10 | Have I Been Pwned | Limited free |

### 5. Run AI-Enhanced Scan

```bash
# Using the orchestrator script
docker-compose exec spiderfoot python /home/spiderfoot/scripts/orchestrator.py \
  --target example.com \
  --name "Full OSINT Scan" \
  --usecase all \
  --ai-report

# Or use the web UI and let the Ollama modules work automatically
```

## Custom Modules

### Ollama AI Modules

| Module | Description |
|--------|-------------|
| `sfp_ollama_analyzer` | Analyzes malicious indicators and vulnerabilities with AI threat assessment |
| `sfp_ollama_summarizer` | Generates executive summaries at scan completion |
| `sfp_ollama_entities` | Extracts structured entities (names, orgs, tech) from unstructured content |

### Additional OSINT Modules

| Module | Description |
|--------|-------------|
| `sfp_abuseipdb` | IP address reputation and abuse reports from AbuseIPDB |
| `sfp_cve_enrich` | CVE detail enrichment from NIST NVD API |

## Custom Correlation Rules

| Rule | Risk | Description |
|------|------|-------------|
| `ai_threat_convergence` | HIGH | Multiple AI-flagged threats on same host |
| `exposed_admin_panels` | HIGH | Admin panels with weak security indicators |
| `credential_exposure_chain` | HIGH | Email found in breaches + credentials leaked |
| `shadow_infrastructure` | MEDIUM | Forgotten/stale infrastructure with active services |
| `crypto_suspicious_activity` | MEDIUM | Crypto wallets associated with malicious activity |
| `supply_chain_risk` | MEDIUM | Third-party JS/dependencies with known issues |

## Configuration

### Environment Variables (.env)

```bash
# SpiderFoot
SF_PORT=5001
SF_MAX_THREADS=5
SF_DNS_SERVER=x.x.x.x

# Ollama
OLLAMA_HOST=http://10.10.0.210:11434
OLLAMA_MODEL=llama3:8b

# Authentication
AUTH_USER=icespider
AUTH_PASS=****

# API Keys (optional)
SHODAN_API_KEY=
VIRUSTOTAL_API_KEY=
ABUSEIPDB_API_KEY=
```

### Ollama Model Recommendations

| Model | Size | Best For |
|-------|------|----------|
| `llama3:8b` | ~4.7GB | General analysis, good balance |
| `llama3:70b` | ~40GB | Deep analysis, best quality |
| `mistral:7b` | ~4.1GB | Fast, good structured output |
| `mixtral:8x7b` | ~26GB | Strong reasoning, correlation |

## Directory Structure

```
IceSpider/
├── docker-compose.yml      # Full stack orchestration
├── Dockerfile              # Enhanced SpiderFoot image
├── .env                    # Environment configuration
├── nginx/
│   └── nginx.conf          # Reverse proxy with auth
├── config/
│   └── env.example         # Template environment file
├── modules/
│   ├── sfp_ollama_analyzer.py    # AI threat analyzer
│   ├── sfp_ollama_summarizer.py  # AI scan summarizer
│   ├── sfp_ollama_entities.py    # AI entity extractor
│   ├── sfp_abuseipdb.py          # AbuseIPDB module
│   └── sfp_cve_enrich.py         # CVE enrichment module
├── correlations/
│   ├── ai_threat_convergence.yaml
│   ├── exposed_admin_panels.yaml
│   ├── credential_exposure_chain.yaml
│   ├── shadow_infrastructure.yaml
│   ├── crypto_suspicious_activity.yaml
│   └── supply_chain_risk.yaml
├── scripts/
│   ├── orchestrator.py     # Scan automation + AI reporting
│   ├── generate-cert.sh    # TLS cert generator
│   └── healthcheck.py      # Health monitoring
└── certs/                  # TLS certificates
```

## License

MIT License - Based on [SpiderFoot](https://github.com/smicallef/spiderfoot)
