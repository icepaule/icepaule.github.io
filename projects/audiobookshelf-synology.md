---
layout: default
title: audiobookshelf-synology
parent: Data & Tools
nav_order: 3
---

# audiobookshelf-synology

[View on GitHub](https://github.com/icepaule/audiobookshelf-synology){: .btn .btn-primary .fs-5 .mb-4 .mb-md-0 .mr-2 }

***

**Selbst gehosteter Hoerbuch-Server mit KI-Metadaten (Ollama) fuer Synology NAS**

Selbst gehosteter Hoerbuch-Server mit KI-gestuetzter Metadaten-Anreicherung
fuer deutsche Hoerbuecher.

## Features

- **3 Bibliotheken**: Eigene Sammlung (Samba, r/w), NAS-Sammlung (ro), USB-Sammlung (ro)
- **Streaming** auf iPhone via native iOS-App
- **Tailscale** fuer sicheren Zugriff von unterwegs (kein Port-Forwarding noetig)
- **Einschlaf-Timer** mit sanftem Ausblenden
- **KI-Metadaten** ueber Ollama (Zusammenfassung, Genre, Einschlaf-Eignung)
- **Offline-Download** fuer Hoeren ohne Netzwerk

## Architektur

```
iPhone App  -- Tailscale/LAN -->  Audiobookshelf  <-->  Ollama
                                       |
                         +-------------+-------------+
                         |             |             |
                    /audiobooks  /nas-audiobooks  /usb-audiobooks
                     (Samba)      (read-only)      (read-only)
```

## Schnellstart

```bash
# .env aus Vorlage erstellen und anpassen
cp .env.example .env
nano .env

# Container starten
docker compose up -d

# Metadaten via Ollama anreichern (nach Bibliotheks-Setup und API-Token)
python3 enrich_metadata.py --dry-run   # Vorschau
python3 enrich_metadata.py             # Ausfuehren
```

## Dokumentation

- [Administrationshandbuch](docs/ADMIN_HANDBUCH.md) - Installation, Konfiguration, Bibliotheken, Tailscale, Wartung
- [Benutzerhandbuch](docs/BENUTZER_HANDBUCH.md) - iPhone-App, Tailscale-Setup, Einschlaf-Timer, Bedienung

## Dateistruktur

```
docker-compose.yml       # Container-Definition (3 Mount-Punkte fuer 3 Bibliotheken)
.env.example             # Vorlage fuer Umgebungsvariablen (nur Platzhalter)
.env                     # Echte Konfiguration (NICHT im Repo, per .gitignore geschuetzt)
.gitignore               # Schuetzt sensible Daten vor dem Repo
enrich_metadata.py       # Ollama-Metadaten-Anreicherung
docs/
  ADMIN_HANDBUCH.md      # Administrationshandbuch
  BENUTZER_HANDBUCH.md   # Benutzerhandbuch
```

## Konfiguration

Alle Konfiguration erfolgt ueber die `.env`-Datei. Die `.env.example` dient als
Vorlage mit Platzhaltern -- keine echten Werte, Pfade oder Tokens im Repository.

Wichtige Variablen:
- `ABS_AUDIOBOOKS_PATH` - Pfad zur eigenen Hoerbuecher-Sammlung (Samba-Share)
- `ABS_MOUNT_NAS` - Pfad zur NAS-Sammlung
- `ABS_MOUNT_USB` - Pfad zur USB-Sammlung
- `ABS_API_TOKEN` - API-Token fuer das Enrichment-Skript
- `OLLAMA_URL` / `OLLAMA_MODEL` - Ollama-Verbindung fuer KI-Metadaten

## Sicherheit

Sensible Daten (API-Tokens, Pfade, IPs) stehen ausschliesslich in der `.env`-Datei,
die per `.gitignore` vom Repository ausgeschlossen ist. Die `.env.example` enthaelt
nur Platzhalter wie `<pfad-zur-nas-sammlung>`, keine echten Zugangsdaten oder Pfade.
