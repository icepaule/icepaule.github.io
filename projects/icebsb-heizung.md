---
layout: default
title: IceBSB-Heizung
parent: Data & Tools
nav_order: 10
---

# IceBSB-Heizung

[View on GitHub](https://github.com/icepaule/IceBSB-Heizung){: .btn .btn-primary .fs-5 .mb-4 .mb-md-0 .mr-2 }

***

**IceBSB-Heizung**

{% raw %}
Dokumentation für die BSB-LAN-Anbindung der Heizungsanlage (Siemens LMU7) an Home Assistant.

BSB-LAN ist ein ESP32-basierter Adapter, der über den BSB-Bus mit dem Heizungscontroller spricht und die Werte per HTTP/JSON, REST und MQTT nach außen gibt. Dieses Repo dokumentiert Aufbau, Netzwerk-Anbindung, Home-Assistant-Integration und die Migration der Firmware von Version 3.2.2 auf 5.1.

## Hardware

| Komponente | Info |
|---|---|
| Controller | Siemens LMU7 (Heizkreis 1, Trinkwasser) |
| Bedieneinheit | AVS37.294/100 |
| Adapter | BSB-LAN, ESP32-DevKit (generisch), 4 MB Flash |
| Anbindung | WLAN (Bad!IoT / VLAN12), BSB-Bus verkabelt zum Heizungscontroller |
| Standort | Heizungskeller |

## Inhalt

- [Architektur](https://github.com/icepaule/IceBSB-Heizung/blob/main/docs/architektur.md) — wie BSB-LAN, Heizung, WLAN und Home Assistant zusammenspielen
- [Netzwerk](https://github.com/icepaule/IceBSB-Heizung/blob/main/docs/netzwerk.md) — Netzwerk-Historie, IP-Drift-Vorfall und Fix
- [Home Assistant Integration](https://github.com/icepaule/IceBSB-Heizung/blob/main/docs/homeassistant.md) — Entities, Sensoren, Dashboard
- [Firmware-Update 3.2.2 → 5.1](https://github.com/icepaule/IceBSB-Heizung/blob/main/docs/firmware-update.md) — kompletter Update-Prozess Schritt für Schritt
- [Parameter-Referenz](https://github.com/icepaule/IceBSB-Heizung/blob/main/docs/parameter-referenz.md) — BSB-Parameter, die für dieses System freigeschaltet wurden
- [Gaswarner](https://github.com/icepaule/IceBSB-Heizung/blob/main/docs/gaswarner.md) — MQ-2-Gassensor (Luft4) im Heizungskeller, Alarmierung über Push/Alexa/Dashboard

## Status

- Firmware: BSB-LAN v5.1.1 (offizieller, gerätespezifischer Parameter-Export liegt bereit, aber wegen eines gefundenen Duplikat-Zeilen-Bugs noch nicht produktiv im Einsatz — siehe [Firmware-Update, Abschnitt 17](https://github.com/icepaule/IceBSB-Heizung/blob/main/docs/firmware-update.md))
- Netzwerk: WLAN Bad!IoT (VLAN12), DHCP — **bekannt schwacher Empfang am Standort Heizungskeller** (-79dBm/39% Retries), Hardware-Fix (ESP32-WROOM-32U mit externer Antenne) beschafft, Tausch steht noch aus
- Home Assistant: native `bsblan`-Integration + eigene REST-Sensoren, vollständig funktionsfähig
- Gaswarner (Luft4/MQ-2): aktiv, end-to-end getestet

## Lizenz / Hinweis

Keine Zugangsdaten, Passwörter oder IP-adressbezogenen Geheimnisse in diesem Repo. Alle Beispiele sind anonymisiert bzw. beziehen sich auf private RFC1918-Adressen ohne sicherheitsrelevanten Wert.
{% endraw %}
