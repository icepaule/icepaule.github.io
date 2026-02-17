---
layout: default
title: adguard-kiosk
parent: Home Automation & Networking
nav_order: 3
---

# adguard-kiosk

[View on GitHub](https://github.com/icepaule/adguard-kiosk){: .btn .btn-primary .fs-5 .mb-4 .mb-md-0 .mr-2 }

***

**Status:** Enterprise-Grade Home-Office Security Implementation  
**Kontext:** Compliance-gerechte Absicherung privater Infrastruktur im Bankenumfeld.

## 🏛️ Regulatorische Prinzipien & Compliance
Dieses Projekt implementiert Kernforderungen moderner IT-Sicherheitsstandards (angelehnt an **BAIT**, **MaRisk** und **NIST SP 800-53**):

* **Defense-in-Depth:** Mehrschichtige Abwehr durch Kombination von DNS-Filtering (AdGuard), Perimeter-Schutz (Sophos XG) und Endpunkt-Monitoring.
* **Availability (Verfügbarkeit):** Autonomes Self-Healing durch Python-Watchdogs zur Sicherstellung der Kontinuität der Sicherheitsdienste.
* **Auditing & Logging:** Echtzeit-Audit-Trail via Pushover-API für alle sicherheitsrelevanten Ausnahmen (Unlocks).
* **Least Privilege:** Minimierung der Angriffsfläche durch Protokoll-basiertes Blocking (IPv6-Härtung).

## 🛡️ MITRE ATT&CK® Mapping
Das System bietet aktive Mitigation gegen folgende Techniken:
* **T1566 (Phishing):** Präventive Blockierung von Phishing-Domains auf DNS-Ebene.
* **T1071.004 (C2 Communication):** Unterbindung von Command-and-Control Verbindungen über DNS-Sperrlisten.
* **T1561 (Disk Wipe):** Schutz der SD-Karten-Integrität durch dediziertes Log-Management (Logrotate).
* **T1204.002 (Malicious File):** Blockierung von Download-Quellen bekannter Malware-Hoster.

## 🛠️ Verwendete Techniken & Skill-Stack
* **Infrastruktur:** Sophos Firewall (IPv6 Prefix Delegation), Raspberry Pi Edge-Hardware.
* **Sprachen:** Python 3.x (Flask für Web-Services, Pygame für GUI).
* **DevOps:** GitHub CI/CD-konforme Versionierung, Systemd Service-Orchestrierung.
* **Frontend:** X11-Kiosk Mode (Matchbox WM), Multi-Threaded Display-Ansteuerung.
* **Networking:** Deep-Dive IPv6 (IA_PD, IA_NA), SLAAC, Reverse DNS-Discovery.

## 📚 Quellen & Tools (Credits)
* **AdGuard Home:** DNS-Filter Engine.
* **Sophos SFOS:** Perimeter Protection.
* **HaGeZi & URLHaus:** Threat Intelligence Feeds.
* **Pushover:** Incident Notification API.
* **Pygame/Flask:** Frameworks für UI und Captive Portal.

***

## 💾 Log-Management (SD-Karten Schutz)
Um die Lebensdauer der SD-Karte zu maximieren, ist ein `logrotate` eingerichtet, der Logs nach 7 Tagen oder Erreichen von 10MB rotiert und komprimiert.
