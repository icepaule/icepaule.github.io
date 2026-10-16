---
layout: default
title: IceOSINT
parent: Data & Tools
nav_order: 44
---

# IceOSINT

[View on GitHub](https://github.com/icepaule/IceOSINT){: .btn .btn-primary .fs-5 .mb-4 .mb-md-0 .mr-2 }

***

**IceOSINT**

{% raw %}
**Production-Ready OSINT System mit Web-GUI, Docker-Stack und AWS Bedrock AI**

## Features

- 🔍 **OSINT-Tools Integration**
  - theHarvester (E-Mail/Domain-Enumeration)
  - Sublist3r (Subdomain-Finder)
  - DNS/WHOIS/SSL-Analyse
  - Ransomware.live API (Leak-Check)
  - HaveIBeenPwned (Breach-Check)

- 🤖 **AI-Powered Analysis**
  - AWS Bedrock (Claude Sonnet 4.5)
  - Automatische Risikobewertung
  - Strukturierte Berichte

- 🖥️ **Web-Dashboard**
  - Request-History
  - Live-Status-Tracking
  - Domain-Whitelist-Management
  - Export (PDF/JSON)

- 🔐 **Security**
  - Authentik-Integration (AD-Gruppen)
  - Domain-Whitelist (@mhb.de, @thesoc.de, @mpauli.de)
  - Guacamole-Ready
  - Audit-Logging

- 🐳 **Docker-Ready**
  - Single-Command-Deployment
  - Auto-Scaling
  - Health-Checks

## Quick Start

```bash
git clone https://github.com/icepaule/IceOSINT.git
cd IceOSINT
cp .env.example .env
# Edit .env with your credentials
docker-compose up -d
```

Access: https://iceosint.thesoc.de

## Architecture

```
Frontend (React) → Backend (FastAPI) → OSINT Tools
                       ↓
                   PostgreSQL
                       ↓
                   AWS Bedrock
```

## Documentation

- [Installation Guide](https://github.com/icepaule/IceOSINT/blob/main/docs/INSTALLATION.md)
- [API Documentation](https://github.com/icepaule/IceOSINT/blob/main/docs/API.md)
- [Deployment Guide](https://github.com/icepaule/IceOSINT/blob/main/docs/DEPLOYMENT.md)

## License

Internal Use Only - IT Security Lab

## Entwickelt von

Claude Code (Sonnet 4.5) - 2026-06-03
{% endraw %}
