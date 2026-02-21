---
layout: default
title: IceTimereport
parent: Data & Tools
nav_order: 2
---

# IceTimereport

[View on GitHub](https://github.com/icepaule/IceTimereport){: .btn .btn-primary .fs-5 .mb-4 .mb-md-0 .mr-2 }

***

Automatisierte Arbeitszeitnachweise aus [Solidtime](https://www.solidtime.io/) mit ArbZG-Compliance-Prüfung.

## Was macht dieses Tool?

Dieses Tool liest Zeiteinträge aus einer lokalen Solidtime-Installation (PostgreSQL-Datenbank) und erzeugt zwei Excel-Arbeitszeitnachweise:

| Version | Datei | Zweck |
|---------|-------|-------|
| **Real** | `Arbeitszeitnachweis_YYYY_real.xlsx` | Echte Stunden + ArbZG-Verstoß-Spalte (privat) |
| **Büro** | `Arbeitszeitnachweis_YYYY.xlsx` | Korrigierte Stunden, ArbZG-konform (für Vorgesetzte) |

### ArbZG-Prüfungen

| § | Regel | Prüfung |
|---|-------|---------|
| §3 | Max. 10 Stunden pro Tag | Tägliche Arbeitszeit |
| §3 | Durchschnitt ≤ 8h über 24 Wochen | Gleitender Durchschnitt |
| §4 | Pause: 30 min > 6h, 45 min > 9h | Lücken zwischen Einträgen |
| §5 | Ruhezeit ≥ 11 Stunden | Ende Tag N → Start Tag N+1 |
| §9 | Keine Sonn-/Feiertagsarbeit | Datumsprüfung |

### Abwesenheitsbehandlung

| Tagestyp | Ist-Stunden | Soll-Stunden | Effekt auf Überstunden |
|----------|-------------|-------------|------------------------|
| **Urlaub** | hours_per_day | hours_per_day | Neutral (bezahlte Abwesenheit) |
| **Krank** | hours_per_day | hours_per_day | Neutral (Entgeltfortzahlung) |
| **Gleittag** | 0 | hours_per_day | Überstundenabbau |
| **Leerer Werktag** | 0 | hours_per_day | Überstundenabbau (Brückentag) |
| **Wochenende/Feiertag** | Tatsächliche Arbeitszeit | 0 | Vollständig als Überstunden |

### Korrektur-Algorithmus (Büro-Version)

- Wochenend-/Feiertagsstunden → auf nächsten Werktag verschoben
- Max. 10h/Tag, Überschuss → Carry-Over auf Folgetage
- Fiktive Start-/End-/Pausenzeiten (Start 08:00)
- Urlaub/Krank → Ist = Soll = hours_per_day (überstundenneutral)
- Gleittag → Ist = 0, Soll bleibt (Überstundenabbau)
- **Gesamtstunden bleiben erhalten** (nur Verteilung ändert sich)

## Features

- Automatische Feiertagsberechnung für alle 16 Bundesländer
- Erkennung von Urlaub/Krank/Gleittagen aus Projekt-Namen
- Urlaubs- und Überstundenkonto (kumulativ seit Vertragsstart)
- Monatliche E-Mail mit Zusammenfassung + Excel-Anhang + Google Drive Link
- ArbZG-Compliance-Bestätigung in der E-Mail (§3, §4, §5, §9)
- Google Drive Sync via rclone
- Täglicher Cron-Job für automatische Generierung

## Voraussetzungen

- Docker + Docker Compose
- Laufende [Solidtime](https://www.solidtime.io/)-Installation (Docker)
- Beide Container im selben Docker-Netzwerk

## Dokumentation

| Dokument | Inhalt |
|----------|--------|
| [Benutzerhandbuch](https://icepaule.github.io/IceTimereport/USER) | Tägliche Nutzung, Konfiguration, FAQ |
| [Administratorhandbuch](https://icepaule.github.io/IceTimereport/ADMIN) | Installation, Solidtime-Setup, E-Mail, rclone, Troubleshooting |
| [Berechnungslogik](https://icepaule.github.io/IceTimereport/CALCULATIONS) | Detaillierte Erklärung aller Berechnungen und Algorithmen |

## Projektstruktur

```
overtime-report/
├── Dockerfile              # Python 3.11 + psycopg2 + openpyxl + rclone
├── docker-compose.yml      # Container-Definition
├── requirements.txt        # Python-Abhängigkeiten
├── .env.example            # Konfigurations-Template
├── entrypoint.sh           # Container-Startskript
├── crontab                 # Scheduling-Konfiguration
├── app/
│   ├── main.py             # CLI: generate / send-email / check
│   ├── db.py               # PostgreSQL-Abfragen (Solidtime)
│   ├── holidays.py         # Deutsche Feiertage (alle Bundesländer)
│   ├── azg.py              # ArbZG Verstoß-Erkennung + Korrektur
│   ├── excel_real.py       # Reale Version (+ ArbZG-Spalte)
│   ├── excel_office.py     # Büro-Version (korrigiert)
│   └── mailer.py           # E-Mail-Versand (SMTP)
├── output/                 # Generierte Excel-Dateien
│   ├── real/               # Private Version
│   └── office/             # Büro-Version
└── docs/
    ├── USER.md             # Benutzerhandbuch
    ├── ADMIN.md            # Administratorhandbuch
    └── CALCULATIONS.md     # Berechnungslogik
```

## Lizenz

MIT
