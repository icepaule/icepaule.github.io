---
layout: default
title: Ice-KVM-Bridge
parent: Data & Tools
nav_order: 19
---

# Ice-KVM-Bridge

[View on GitHub](https://github.com/icepaule/Ice-KVM-Bridge){: .btn .btn-primary .fs-5 .mb-4 .mb-md-0 .mr-2 }

***

**ESP32-S3 USB-Host-zu-WiFi-Bridge: Notfall-Fernkonsole für Geräte mit nur einem Micro-USB-Konsolenport (Fork von betaflight/bridge)**

{% raw %}
Ein ESP32-S3-WROOM-1 als **Notfall-Fernkonsole ("KVM")** für Geräte, die nur
über einen Micro-USB-Konsolenport erreichbar sind — z. B. ein
[Olimex ESP32-EVB-EA](https://www.olimex.com/Products/IoT/ESP32/ESP32-EVB-EA/open-source-hardware),
dessen eigenes WLAN gerade ausgefallen ist. Der S3 hängt sich als **USB-Host**
an den Konsolenport des Zielgeräts, spricht dessen USB-UART-Chip an und
spiegelt den Byte-Strom transparent auf **WiFi** — erreichbar per Telnet, per
Web-UI und als Live-Konsole direkt im Browser.

![Web-UI Statusseite](https://raw.githubusercontent.com/icepaule/Ice-KVM-Bridge/master/docs/img/web-ui-status.png)

Basis ist der Fork von [betaflight/bridge](https://github.com/betaflight/bridge)
(ESP-IDF, TinyUSB-Host, GPL-3.0) — ursprünglich gebaut, um einen
Flight-Controller per USB-Host + WiFi mit dem Betaflight-Configurator zu
verbinden. Die Firmware macht praktisch alles, was man für eine generische
USB-Host-zu-WiFi-Bridge braucht: Web-UI, WiFi-Setup per Captive Portal,
TLS-Zertifikat, OTA-Update — nur eben ursprünglich für einen Flugcontroller.
Dieses Repo passt sie auf einen generischen seriellen Konsolenzugang an.

## Warum das Ganze

Das EVB-EA hat keine frei zugänglichen UART-Pins — nur den Micro-USB-
Konsolenport (bestückt mit einem CH340-USB-UART-Chip). Fällt das WLAN des
EVB-EA aus, gibt es ohne physischen Zugriff sonst keine Möglichkeit, an die
Konsole zu kommen. Die Bridge löst das, indem sie selbst nie vom WLAN des
Zielgeräts abhängt — sie hängt an einem eigenen Netz.

## Features

- **USB-Host → WiFi-Bridge**: S3 nutzt seinen nativen USB-OTG-Port im
  Host-Modus, spricht den CH340 (oder andere unterstützte USB-UART-Chips) als
  CDC-ACM-Gerät an
- **Telnet** (Port 23) — Raw-TCP, funktioniert mit jedem Telnet-Client
- **Web-UI** (HTTP/HTTPS) — Status, WiFi-Konfiguration per Captive Portal,
  Firmware-Update
- **Live-Konsole im Browser** — read-only WebSocket-Ansicht (`/view`), läuft
  **parallel** zu einer aktiven Telnet-Sitzung
- **WiFi-Setup per Captive Portal** — kein Flashen von Zugangsdaten nötig
- Self-signed TLS-Zertifikat für `https://` und `wss://`

## Dokumentation

| Dokument | Inhalt |
|---|---|
| [docs/architecture.md](https://github.com/icepaule/Ice-KVM-Bridge/blob/master/docs/architecture.md) | Aufbau (Hardware + Software), Diagramme |
| [docs/hardware.md](https://github.com/icepaule/Ice-KVM-Bridge/blob/master/docs/hardware.md) | Board-Auswahl, Port-Identifikation, USB-VBUS-Falle |
| [docs/build.md](https://github.com/icepaule/Ice-KVM-Bridge/blob/master/docs/build.md) | ESP-IDF-Setup, Bauen, Flashen |
| [docs/usage.md](https://github.com/icepaule/Ice-KVM-Bridge/blob/master/docs/usage.md) | Erstinbetriebnahme, WiFi-Setup, Telnet/Web-UI/Live-Konsole |
| [docs/upstream-changes.md](https://github.com/icepaule/Ice-KVM-Bridge/blob/master/docs/upstream-changes.md) | Was gegenüber betaflight/bridge geändert wurde |
| [docs/troubleshooting.md](https://github.com/icepaule/Ice-KVM-Bridge/blob/master/docs/troubleshooting.md) | Bekannte Stolpersteine und ihre Lösung |

## Schnellstart

```bash
# ESP-IDF v5.4 (einmalig)
git clone -b release/v5.4 --recursive --depth 1 --shallow-submodules \
  https://github.com/espressif/esp-idf.git ~/esp-idf
~/esp-idf/install.sh esp32s3
export IDF_PATH=~/esp-idf
source $IDF_PATH/export.sh

# Bridge bauen und flashen
git clone https://github.com/icepaule/Ice-KVM-Bridge.git
cd Ice-KVM-Bridge
idf.py build
idf.py -p /dev/ttyUSBx flash
```

Details, Board-Auswahl und Fallstricke: siehe [docs/build.md](https://github.com/icepaule/Ice-KVM-Bridge/blob/master/docs/build.md).

## Lizenz

GPL-3.0, wie das Upstream-Projekt — siehe [LICENSE](https://github.com/icepaule/Ice-KVM-Bridge/blob/master/LICENSE). Alle
Quelldateien behalten die ursprünglichen Betaflight-Copyright-Header; eigene
Ergänzungen sind als solche markiert.
{% endraw %}
