---
layout: default
title: IceGeigerCounter
parent: Data & Tools
nav_order: 11
---

# IceGeigerCounter

[View on GitHub](https://github.com/icepaule/IceGeigerCounter){: .btn .btn-primary .fs-5 .mb-4 .mb-md-0 .mr-2 }

***

**IceGeigerCounter**

{% raw %}
DIY-Geigerzähler auf Basis eines **Wemos ESP-WROOM-02** (ESP8266) mit integriertem 18650-Akkufach, einem GM-Röhren-Modul, 0,96" OLED-Display und Piezo-Sound, in einem kompakten 3D-gedruckten Gehäuse.

## Status

- [x] Hardware ausgewählt & Kompatibilität geprüft (Chip live via `esptool` verifiziert: ESP8266EX)
- [x] Stromversorgung geklärt (5V-Pin am Board vom TP5400-Booster nutzbar)
- [x] Firmware-Wahl getroffen
- [ ] Bauteile bestellt
- [ ] Verkabelung aufgebaut
- [ ] Firmware geflasht & konfiguriert
- [ ] Gehäuse gedruckt & montiert
- [ ] Kalibrierung / erster Dauertest

## Doku-Struktur

1. [Stückliste](https://github.com/icepaule/IceGeigerCounter/blob/main/docs/01-parts-list.md)
2. [Verkabelung](https://github.com/icepaule/IceGeigerCounter/blob/main/docs/02-wiring.md)
3. [Firmware](https://github.com/icepaule/IceGeigerCounter/blob/main/docs/03-firmware.md)
4. [Gehäuse](https://github.com/icepaule/IceGeigerCounter/blob/main/docs/04-enclosure.md)
5. [Zusammenbau](https://github.com/icepaule/IceGeigerCounter/blob/main/docs/05-assembly.md)

## Sicherheitshinweise

- Das GM-Tube-Modul erzeugt intern eine Hochspannung von ca. 380–500V für die Geiger-Müller-Röhre. Nicht bei angeschlossener Spannungsquelle an die Röhren-/HV-Kontakte fassen.
- Für den Betrieb wird keine radioaktive Prüfquelle benötigt – natürliche Hintergrundstrahlung reicht zum Testen der Funktion aus.
{% endraw %}
