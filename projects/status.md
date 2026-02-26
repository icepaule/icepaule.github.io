---
layout: default
title: Status Dashboard
nav_order: 99
---

# Status Dashboard
{: .fs-9 }

Automated documentation & security scanning status.
{: .fs-6 .fw-300 }

*Last updated: 2026-02-26 10:45 UTC*

---

## CI/CD Pipeline

```mermaid
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
```

---

## Documentation Coverage

**35 repos** documented: 19 curated, 13 auto-generated.

| Repo | Description | Status | Doc Page |
|:-----|:------------|:-------|:---------|
| [adguard-kiosk](https://github.com/icepaule/adguard-kiosk) | My Adguard implementation using a raspberry 3b | Curated | [View](adguard-kiosk.html) |
| [audiobookshelf-synology](https://github.com/icepaule/audiobookshelf-synology) | Selbst gehosteter Hoerbuch-Server mit KI-Metadaten (Ollama)  | Auto | [View](audiobookshelf-synology.html) |
| [cuckoo-docker](https://github.com/icepaule/cuckoo-docker) | Creating a docker container hosting a cuckoo sandbox | Auto | [View](cuckoo-docker.html) |
| [doed_forensics](https://github.com/icepaule/doed_forensics) | doed´s little helpers | Auto | [View](doed_forensics.html) |
| [esp32cam-dataset-firmware](https://github.com/icepaule/esp32cam-dataset-firmware) | AI Edge version to look at my postbox if there is a mail. | No README | - |
| [followmysun](https://github.com/icepaule/followmysun) | Single axis adjustment for my solar panel | No README | - |
| [Ice-GitHub-Doku](https://github.com/icepaule/Ice-GitHub-Doku) |  | Auto | [View](ice-github-doku.html) |
| [Ice-MTastik](https://github.com/icepaule/Ice-MTastik) | My Meshtastik setup | Curated | [View](ice-mtastik.html) |
| [IceAI-tax-2025](https://github.com/icepaule/IceAI-tax-2025) |  | Auto | [View](iceai-tax-2025.html) |
| [IceBackup](https://github.com/icepaule/IceBackup) |  | Auto | [View](icebackup.html) |
| [IceCrow](https://github.com/icepaule/IceCrow) |  | No README | - |
| [IceDataEmphasise](https://github.com/icepaule/IceDataEmphasise) |  | Curated | [View](icedataemphasise.html) |
| [IceHomeAssist](https://github.com/icepaule/IceHomeAssist) | My Home Assistant setup | Curated | [View](icehomeassist.html) |
| [IceIntelligence](https://github.com/icepaule/IceIntelligence) |  | Curated | [View](iceintelligence.html) |
| [IceLaborVPN](https://github.com/icepaule/IceLaborVPN) | Secure Zero-Trust Remote Access Gateway for Malware Analysis | Curated | [View](icelaborvpn.html) |
| [IceMailArchive](https://github.com/icepaule/IceMailArchive) | Self-hosted Email-Archivierung mit OpenArchiver, Proton Brid | Auto | [View](icemailarchive.html) |
| [IceMatrix](https://github.com/icepaule/IceMatrix) |  | Auto | [View](icematrix.html) |
| [IceMeshCore](https://github.com/icepaule/IceMeshCore) |  | Curated | [View](icemeshcore.html) |
| [IcePorge](https://github.com/icepaule/IcePorge) | IcePorge - Comprehensive Malware Analysis & Threat Intellige | Curated | [View](iceporge.html) |
| [IcePorge-CAPE-Feed](https://github.com/icepaule/IcePorge-CAPE-Feed) | MalwareBazaar to CAPE to MISP automated pipeline | Curated | [View](iceporge-cape-feed.html) |
| [IcePorge-CAPE-Mailer](https://github.com/icepaule/IcePorge-CAPE-Mailer) | CAPE Sandbox Email Integration - Automated malware analysis  | Curated | [View](iceporge-cape-mailer.html) |
| [IcePorge-Cockpit](https://github.com/icepaule/IcePorge-Cockpit) | Cockpit web management modules for CAPE and MWDB stacks | Curated | [View](iceporge-cockpit.html) |
| [IcePorge-Ghidra-Orchestrator](https://github.com/icepaule/IcePorge-Ghidra-Orchestrator) | Automated Ghidra reverse engineering with LLM enhancement | Curated | [View](iceporge-ghidra-orchestrator.html) |
| [IcePorge-Malware-RAG](https://github.com/icepaule/IcePorge-Malware-RAG) | LLM-powered malware analysis using RAG and vector databases | Curated | [View](iceporge-malware-rag.html) |
| [IcePorge-MWDB-Feeder](https://github.com/icepaule/IcePorge-MWDB-Feeder) | Multi-source malware sample aggregator (URLhaus, ThreatFox,  | Curated | [View](iceporge-mwdb-feeder.html) |
| [IcePorge-MWDB-Stack](https://github.com/icepaule/IcePorge-MWDB-Stack) | MWDB-core with Karton orchestration for malware sample manag | Curated | [View](iceporge-mwdb-stack.html) |
| [IceSeller](https://github.com/icepaule/IceSeller) |  | Auto | [View](iceseller.html) |
| [IceTimereport](https://github.com/icepaule/IceTimereport) |  | Curated | [View](icetimereport.html) |
| [IceWiFi](https://github.com/icepaule/IceWiFi) | My Home-WiFi setup using UniFi equipment | Curated | [View](icewifi.html) |
| [IceXWiKi](https://github.com/icepaule/IceXWiKi) |  | Auto | [View](icexwiki.html) |
| [no-telemetry](https://github.com/icepaule/no-telemetry) | Win10 Telemetry blocklist for piHole | Auto | [View](no-telemetry.html) |
| [secintel](https://github.com/icepaule/secintel) | A security intel project powered by Django | Auto | [View](secintel.html) |
| [tibberampel](https://github.com/icepaule/tibberampel) | Meine Tibberampel mit einem ESP8266 | Curated | [View](tibberampel.html) |
| [Torlinks](https://github.com/icepaule/Torlinks) | Tor Links Database. This repository contains 2 files contain | Auto | [View](torlinks.html) |
| [xwiki-stack](https://github.com/icepaule/xwiki-stack) |  | Curated | [View](xwiki-stack.html) |

---

## Security Scan Summary

*No scan results available. Run scan_secrets.py first.*



---

## Configuration

| Setting | Status |
|:--------|:-------|
| Daily Schedule | 03:00 UTC |
| Secret Scanning | Enabled |
| Doc Generation | Enabled |
| Pushover Alerts | Configured |
| Fork Scanning | Disabled |

---

*This page is auto-generated by [generate_status.py](https://github.com/icepaule/icepaule.github.io/blob/main/scripts/generate_status.py).*
