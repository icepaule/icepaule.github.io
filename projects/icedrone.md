---
layout: default
title: IceDrone
parent: Data & Tools
nav_order: 28
---

# IceDrone

[View on GitHub](https://github.com/icepaule/IceDrone){: .btn .btn-primary .fs-5 .mb-4 .mb-md-0 .mr-2 }

***

**IceDrone**

{% raw %}
A small, 3D-printable brushed quadcopter built around the **Seeed Studio XIAO ESP32-S3 Sense** with onboard **OV3660 camera**, Wi-Fi MJPEG video and an Open32Drone-derived flight stack.

> **Project status:** early engineering documentation. This repository currently contains the bill of materials, pin/netlist tables, wiring diagram and bench-test firmware. CAD sources, renders, the Open32Drone firmware overlay and helper scripts referenced in the docs are not part of this initial upload yet.

## Design goals

- DIY-friendly, mostly printable airframe
- hand-sized: **123 mm diagonal motor-center wheelbase**
- **8520 brushed motors**, 1.0 mm shafts
- **76 mm, 2-blade CW/CCW props**
- target takeoff mass **60-80 g**
- XIAO ESP32-S3 Sense as both flight computer and camera computer
- QVGA MJPEG live video over 2.4 GHz Wi-Fi
- MAVLink telemetry/control over UDP 14550
- initial flight mode: stabilized/manual; optical flow and SBUS remain V2 options
- printable on an Anycubic Kobra S1 with a 0.4 mm nozzle

## Why this architecture

Open32Drone currently documents the XIAO ESP32-S3 Sense, 8520 motors, 76 mm props, a 300 Hz flight-critical loop, 10 kHz motor PWM and an optional low-priority MJPEG task. Its current pin map also avoids the Sense camera GPIOs. That makes it a much stronger base for a camera drone than simply adding a second ESP-CAM to ESP-FLY.

Primary technical references:

- Open32Drone: https://github.com/npu-ius-lab/open32drone
- Open32Drone tutorial: https://github.com/npu-ius-lab/open32drone/blob/main/tutorial.md
- Flix: https://github.com/okalachev/flix
- ESP-FLY: https://github.com/Seeed-Projects/Co-Create_ESP-FLY
- XIAO ESP32-S3 Sense: https://wiki.seeedstudio.com/xiao_esp32s3_getting_started/
- XIAO pin multiplexing / camera pins: https://wiki.seeedstudio.com/xiao_esp32s3_pin_multiplexing/

## Repository layout

```text
.
├── README.md
├── LICENSE
├── NOTICE
├── bom/
│   └── bom.csv
├── docs/
│   ├── 01_BOM.md
│   ├── 02_ELECTRICAL.md
│   ├── 03_MECHANICAL.md
│   ├── 04_FIRMWARE.md
│   ├── 05_BUILD_AND_TEST.md
│   ├── 06_FIRST_FLIGHT.md
│   ├── 07_SAFETY_AND_LEGAL_DE.md
│   ├── 08_TROUBLESHOOTING.md
│   └── SOURCES.md
├── firmware/
│   └── bench_test/
│       └── main.cpp
└── hardware/
    ├── pinmap.csv
    ├── motor_stage_netlist.csv
    └── wiring.svg
```

CAD sources (`cad/`), the Open32Drone firmware overlay and build/fetch scripts are planned but not yet part of this repository — see the status note above.

## Quick start

1. Read `docs/01_BOM.md` and order the V1 parts.
2. Assemble electronics **without propellers**.
3. Run the bench firmware in `firmware/bench_test/` to validate the camera, IMU wiring and each MOSFET/motor channel.
4. Fetch Open32Drone and follow `docs/04_FIRMWARE.md`.
5. Complete every prop-off test in `docs/05_BUILD_AND_TEST.md` before fitting props.
6. Perform the first hover using `docs/06_FIRST_FLIGHT.md`.

## Mechanical concept

The motors are located at ±43.49 mm in X/Y, giving a 123 mm diagonal wheelbase. With 76 mm props, adjacent motor centers are ~87 mm apart, giving roughly 11 mm tip-to-tip clearance. See `docs/03_MECHANICAL.md` for the full frame geometry and print settings.

## Wiring

![V1 wiring overview](https://raw.githubusercontent.com/icepaule/IceDrone/main/hardware/wiring.svg)

See `docs/02_ELECTRICAL.md` for the full electrical documentation.

## Important safety rule

**Never test motor channels, arming logic, mixer direction, or firmware changes with propellers fitted.** Fit propellers only after motor order and direction have been verified at low output. See `docs/07_SAFETY_AND_LEGAL_DE.md` for the full safety and (German/EU) legal notes.

## License and attribution

Original documentation, tables and bench-test code in this repository are provided under Apache-2.0. Open32Drone is also Apache-2.0; its source is not duplicated here. Preserve all upstream notices when you fetch or fork it. See `NOTICE`.
{% endraw %}
