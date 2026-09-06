---
layout: default
title: IceMark5
parent: Data & Tools
nav_order: 43
---

# IceMark5

[View on GitHub](https://github.com/icepaule/IceMark5){: .btn .btn-primary .fs-5 .mb-4 .mb-md-0 .mr-2 }

***

**IceMark5**

{% raw %}
![IceMark5 Web-GUI](https://raw.githubusercontent.com/icepaule/IceMark5/main/docs/images/webgui-dashboard.png)
*Echter Screenshot des aktuellen Firmware-Dashboards – alle drei Module noch
unverbunden, da HF/LF/UHF-Hardware noch nicht verbaut ist (siehe Statustabelle
unten).*

Ein Proxmark5-inspirierter Multi-Band-RFID-Nachbau auf Basis eines **ESP32-S3**
(Dual-Core, WiFi, BLE5, 8MB PSRAM) statt proprietärer FPGA-Hardware. Ziel: LF
(125kHz), HF (13.56MHz) und UHF (860-960MHz) über austauschbare, günstige
Module ansprechen und über ein eingebautes Web-GUI steuern – ganz ohne
PC-Client-Software.

> Hardware-Fotos folgen, sobald die LF/HF/UHF-Module verbaut sind. Bis dahin
> beschreiben die Diagramme in [`docs/architektur.md`](https://github.com/icepaule/IceMark5/blob/main/docs/architektur.md)
> den Aufbau.

## Stand des Projekts

| Bereich | Status |
|---|---|
| ESP32-S3 Firmware-Grundgerüst | ✅ läuft (WiFi AP/STA, REST-API, WebSocket-Log) |
| Web-GUI (Dashboard) | ✅ läuft, zeigt Modul-Status live |
| HF-Modul (PN532/RC522) | ⏳ Interface steht, Treiber fehlt noch |
| LF-Modul (125kHz Coil) | ⏳ Interface steht, Bit-Timing-ISR fehlt noch |
| UHF-Modul (UART-Reader) | ⏳ Interface steht, Vendor-Protokoll fehlt noch |

## Dokumentation

- [Schritt-für-Schritt-Anleitung](https://github.com/icepaule/IceMark5/blob/main/docs/anleitung.md) – Aufbau, Flashen, GUI-Funktionen erklärt
- [Architektur](https://github.com/icepaule/IceMark5/blob/main/docs/architektur.md) – Systemaufbau, Datenfluss, Modul-Abstraktion
- [Vergleich zum Proxmark5](https://github.com/icepaule/IceMark5/blob/main/docs/vergleich.md) – Hardware- und Funktionsvergleich
- [Bill of Materials](https://github.com/icepaule/IceMark5/blob/main/docs/bom.md) – Bauteile, Preise, Bezugsquellen

## Kurzstart

```
git clone ****@****.***:icepaule/IceMark5.git
cd IceMark5
pio run                # Firmware bauen
pio run -t uploadfs    # Web-GUI aufs Dateisystem flashen
pio run -t upload      # Firmware flashen
```

Details und Erklärungen: siehe [Anleitung](https://github.com/icepaule/IceMark5/blob/main/docs/anleitung.md).

## Lizenz / Nutzung

Forschungs- und Hobbyprojekt zur RFID-Sicherheitsanalyse eigener Systeme.
Kein produktreifes Werkzeug, keine Garantie auf Vollständigkeit oder
Rechtskonformität in jeder Jurisdiktion – Nutzung auf eigene Verantwortung
und nur an Systemen, für die eine Erlaubnis vorliegt.
{% endraw %}
