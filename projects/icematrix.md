---
layout: default
title: IceMatrix
parent: Hardware & ESP32
nav_order: 2
---

<!-- manually-curated -->

# IceMatrix

[View on GitHub](https://github.com/icepaule/IceMatrix){: .btn .btn-primary .fs-5 .mb-4 .mb-md-0 .mr-2 }

***

**IceMatrix**

{% raw %}
LED-Matrix-Displays fürs Zuhause — von seriellen MAX7219-Dot-Matrix-Anzeigen (Tasmota + Node-RED + Home Assistant) bis zu einem eigenständigen RGB-HUB75-Panel-Projekt auf ESP32-S3.

## Hardware

| Display | Module | Farbe | ESP | Funktion |
|---------|--------|-------|-----|----------|
| Matrix1 (PV-Matrix) | 4x MAX7219 (32x8) | Rot | ESP-12F | PV-Leistung (Sonnenstand-basiert) |
| Matrix2 | 4x MAX7219 (32x8) | Rot | ESP-12F | Uhrzeit + PV-Leistung |
| Matrix3 | 8x MAX7219 (64x8) | 4x Rot + 4x Blau | Wemos D1 Mini | Uhrzeit + PV + Alerts |
| Matrix4 (Strompreis) | 4x MAX7219 (32x8) | Rot | Wemos D1 Mini | Tibber Strompreis + Trend |
| Matrix5 (2FA-Anzeige) | 2x HUB75 P4-2121-64x32-16S | RGB | ESP32-S3 | TOTP/2FA-Codes, eigene Firmware |

> ESP-12F (Matrix1/2) und Wemos D1 Mini (Matrix3/4) haben unterschiedliche GPIO-Zuordnungen — Details in der Repo-Doku.

## Architektur (Matrix1-4)

```mermaid
flowchart LR
    subgraph HA["Home Assistant"]
        S1["PV Leistung"]
        S2["Tibber"]
        S3["NINA / DWD"]
        S4["Divera THW"]
        S5["Netzwerk"]
        S6["Petkit"]
        S7["Meshtastic"]
    end
    HA --> NR["Node-RED<br/>Formatierung: Uhrzeit, PV Watt/kWh, Alert-Codes"]
    NR -->|"cmnd/&lt;name&gt;/DisplayText<br/>cmnd/&lt;name&gt;/DisplayDimmer"| MQTT[("MQTT<br/>Mosquitto")]
    MQTT --> T1["Tasmota ESP8266"]
    T1 --> M["MAX7219 Matrix"]
```

**Matrix5** läuft komplett unabhängig davon auf eigener C++/PlatformIO-Firmware (kein Tasmota, kein Node-RED) — HUB75-RGB-Panels brauchen eine kontinuierliche DMA-Ansteuerung, die Tasmota nicht unterstützt. Stattdessen: WLAN + NTP-Sync, HMAC-SHA1/TOTP direkt auf dem ESP32-S3, Ausgabe auf zwei gekettete 64x32-Panels.

## Custom Firmware (Pflicht für Matrix1-4!)

Die Standard-Tasmota-Firmware enthält **nicht** den MAX7219-Dot-Matrix-Treiber (nur den 7-Segment-Treiber) — ohne Custom-Build (`USE_DISPLAY_MAX7219_MATRIX`) leuchten alle LEDs permanent.

## Alert-System (Matrix3)

14 priorisierte Alert-Codes über 4 Prioritätsstufen (THW-Alarm, Wetter-/Hochwasserwarnungen, Netzwerkstatus, Haushaltsgeräte, Strompreis) — jeder einzeln per Home-Assistant-Toggle ein-/ausschaltbar, alle standardmäßig aus.

## Dokumentation

| Dokument | Inhalt |
|---|---|
| [docs/custom-build.md](https://github.com/icepaule/IceMatrix/blob/main/docs/custom-build.md) | Custom-Tasmota-Build für MAX7219 Dot-Matrix (Matrix1-4) |
| [docs/nodered-config.md](https://github.com/icepaule/IceMatrix/blob/main/docs/nodered-config.md) | Node-RED-Flows, MQTT-Topics, Alert-System, alle 4 Displays im Detail |
| [docs/matrix5-totp.md](https://github.com/icepaule/IceMatrix/blob/main/docs/matrix5-totp.md) | Matrix5: HUB75/ESP32-S3, Verkabelungsplan, Firmware-Gerüst |

## Status

- [x] Matrix1-4 produktiv im Einsatz (Tasmota + Node-RED + Home Assistant)
- [x] Matrix5: ESP32-S3 erkannt, WLAN/NTP-Firmware erfolgreich getestet
- [ ] Matrix5: finale TOTP-Firmware mit echten Accounts
- [ ] Fotos aller 5 Displays

## Keine sensiblen Daten in diesem Repo

Interne IPs sowie WLAN-/MQTT-Zugangsdaten werden in der Doku durch Platzhalter ersetzt.
Ein früherer Commit hatte versehentlich echte Zugangsdaten im Klartext enthalten — ein
Folgecommit hatte nur den *aktuellen* Dateiinhalt redigiert, die Klartext-Version blieb aber
über die Git-History abrufbar. Die komplette History wurde inzwischen bereinigt
(`git filter-repo` + Force-Push), betroffene interne Referenzen sind durchgängig durch
Platzhalter ersetzt.
{% endraw %}
