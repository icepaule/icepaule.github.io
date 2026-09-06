---
layout: default
title: IceDrone
parent: Data & Tools
nav_order: 26
---

# IceDrone

[View on GitHub](https://github.com/icepaule/IceDrone){: .btn .btn-primary .fs-5 .mb-4 .mb-md-0 .mr-2 }

***

**IceDrone**

{% raw %}
A small, 3D-printable brushed quadcopter built around the **Seeed Studio XIAO ESP32-S3 Sense**, a **GY-91 IMU**, four **8520 brushed coreless motors** and 75/76 mm propellers. The project combines an Open32Drone-derived flight stack with Wi-Fi camera streaming and a modular printable airframe sized for an **Anycubic Kobra S1**.

> **Current mechanical design: Airframe V2.** The older V1 frame/cradle files have been removed from `main`; Git history still contains them if needed.
>
> Full documentation: **[icepaule.github.io/IceDrone](https://icepaule.github.io/IceDrone/)** and [`docs/`](https://github.com/icepaule/IceDrone/blob/main/docs/).

## Airframe V2

![IceDrone Airframe V2 assembly](https://raw.githubusercontent.com/icepaule/IceDrone/main/cad/airframe_v2/renders/assembly_preview_v2.png)

The current airframe is a modular **123 mm Quad-X** design with dedicated mounts for the 1S battery, electronics deck, XIAO ESP32-S3 Sense camera board, GY-91 IMU and a lightweight flight cage or closed canopy.

![Airframe V2 printable parts](https://raw.githubusercontent.com/icepaule/IceDrone/main/cad/airframe_v2/renders/airframe_v2_parts.png)

Detailed part descriptions, OpenSCAD sources, STL downloads, Kobra S1 print settings and validation notes are in **[`cad/airframe_v2/`](https://github.com/icepaule/IceDrone/blob/main/cad/airframe_v2/)**.

### Main printable parts

| Part | Preview | Source / STL |
|---|---|---|
| Main Quad-X frame | <img src="cad/airframe_v2/renders/frame_v2.png" width="180"> | [`frame_v2.scad`](https://github.com/icepaule/IceDrone/blob/main/cad/airframe_v2/scad/frame_v2.scad) · [`frame_v2.stl`](https://github.com/icepaule/IceDrone/blob/main/cad/airframe_v2/stl/frame_v2.stl) |
| Electronics deck | <img src="cad/airframe_v2/renders/electronics_deck_v2.png" width="180"> | [`electronics_deck_v2.scad`](https://github.com/icepaule/IceDrone/blob/main/cad/airframe_v2/scad/electronics_deck_v2.scad) · [`electronics_deck_v2.stl`](https://github.com/icepaule/IceDrone/blob/main/cad/airframe_v2/stl/electronics_deck_v2.stl) |
| Battery sled | <img src="cad/airframe_v2/renders/battery_sled_650_v2.png" width="180"> | [`battery_sled_650_v2.scad`](https://github.com/icepaule/IceDrone/blob/main/cad/airframe_v2/scad/battery_sled_650_v2.scad) · [`battery_sled_650_v2.stl`](https://github.com/icepaule/IceDrone/blob/main/cad/airframe_v2/stl/battery_sled_650_v2.stl) |
| XIAO camera mount | <img src="cad/airframe_v2/renders/xiao_camera_mount_15deg.png" width="180"> | [`xiao_camera_mount_15deg.scad`](https://github.com/icepaule/IceDrone/blob/main/cad/airframe_v2/scad/xiao_camera_mount_15deg.scad) · [`xiao_camera_mount_15deg.stl`](https://github.com/icepaule/IceDrone/blob/main/cad/airframe_v2/stl/xiao_camera_mount_15deg.stl) |
| GY-91 IMU saddle | <img src="cad/airframe_v2/renders/imu_gy91_saddle.png" width="180"> | [`imu_gy91_saddle.scad`](https://github.com/icepaule/IceDrone/blob/main/cad/airframe_v2/scad/imu_gy91_saddle.scad) · [`imu_gy91_saddle.stl`](https://github.com/icepaule/IceDrone/blob/main/cad/airframe_v2/stl/imu_gy91_saddle.stl) |
| Flight cage | <img src="cad/airframe_v2/renders/flight_cage_v2.png" width="180"> | [`flight_cage_v2.scad`](https://github.com/icepaule/IceDrone/blob/main/cad/airframe_v2/scad/flight_cage_v2.scad) · [`flight_cage_v2.stl`](https://github.com/icepaule/IceDrone/blob/main/cad/airframe_v2/stl/flight_cage_v2.stl) |
| Closed canopy | <img src="cad/airframe_v2/renders/canopy_v2.png" width="180"> | [`canopy_v2.scad`](https://github.com/icepaule/IceDrone/blob/main/cad/airframe_v2/scad/canopy_v2.scad) · [`canopy_v2.stl`](https://github.com/icepaule/IceDrone/blob/main/cad/airframe_v2/stl/canopy_v2.stl) |
| Motor-cup fit test | <img src="cad/airframe_v2/renders/motor_cup_test_v2.png" width="180"> | [`motor_cup_test_v2.scad`](https://github.com/icepaule/IceDrone/blob/main/cad/airframe_v2/scad/motor_cup_test_v2.scad) · [`motor_cup_test_v2.stl`](https://github.com/icepaule/IceDrone/blob/main/cad/airframe_v2/stl/motor_cup_test_v2.stl) |

## Propellers and replacement CAD

The purchased 75 mm propellers can be used directly. Parametric replacement/test models are kept separately under [`cad/propellers/`](https://github.com/icepaule/IceDrone/blob/main/cad/propellers/) so the flight airframe and experimental propeller work remain clearly separated.

| Standard 75 mm | Experimental toroidal / low-noise concept |
|---|---|
| <img src="cad/propellers/renders/prop75_standard.png" width="300"> | <img src="cad/propellers/renders/prop75_toroidal.png" width="300"> |

The repository includes CW/CCW STL exports and a 1 mm shaft-fit coupon. The toroidal model is experimental and should be bench-tested for current draw, vibration, balance and thrust before flight use.

## Design goals

- mostly printable micro quadcopter
- **123 mm diagonal motor-center wheelbase**
- **8520 brushed motors**, nominal 1.0 mm shafts
- **75/76 mm two-blade CW/CCW propellers**
- target takeoff mass around **60–80 g**
- XIAO ESP32-S3 Sense as flight/camera computer
- QVGA MJPEG live video over 2.4 GHz Wi-Fi
- MAVLink telemetry/control over UDP 14550
- stabilized/manual first-flight target
- printable on an Anycubic Kobra S1 with a 0.4 mm nozzle

## Repository layout

```text
.
├── README.md
├── bom/
├── cad/
│   ├── airframe_v2/
│   │   ├── scad/
│   │   ├── stl/
│   │   └── renders/
│   └── propellers/
│       ├── scad/
│       ├── stl/
│       └── renders/
├── docs/
├── firmware/
└── hardware/
```

## Quick start

1. Read [`docs/01_BOM.md`](https://github.com/icepaule/IceDrone/blob/main/docs/01_BOM.md) and verify the actual delivered part dimensions.
2. Print [`cad/airframe_v2/stl/motor_cup_test_v2.stl`](https://github.com/icepaule/IceDrone/blob/main/cad/airframe_v2/stl/motor_cup_test_v2.stl) before committing to the full frame.
3. Print the Airframe V2 parts using the settings in [`docs/03_MECHANICAL.md`](https://github.com/icepaule/IceDrone/blob/main/docs/03_MECHANICAL.md).
4. Assemble electronics **without propellers**, following [`docs/02_ELECTRICAL.md`](https://github.com/icepaule/IceDrone/blob/main/docs/02_ELECTRICAL.md).
5. Run the bench firmware in [`firmware/bench_test/`](https://github.com/icepaule/IceDrone/blob/main/firmware/bench_test/) and verify IMU orientation and every motor channel.
6. Follow [`docs/05_BUILD_AND_TEST.md`](https://github.com/icepaule/IceDrone/blob/main/docs/05_BUILD_AND_TEST.md) and only then install balanced propellers.
7. Perform first hover tests using [`docs/06_FIRST_FLIGHT.md`](https://github.com/icepaule/IceDrone/blob/main/docs/06_FIRST_FLIGHT.md).

## Primary references

- Open32Drone: https://github.com/npu-ius-lab/open32drone
- ESP-FLY: https://github.com/Seeed-Projects/Co-Create_ESP-FLY
- XIAO ESP32-S3 Sense: https://wiki.seeedstudio.com/xiao_esp32s3_getting_started/

## Important safety rule

**Never test motor channels, arming logic, mixer direction or firmware changes with propellers fitted.** Verify motor order and direction at low output first. Printed propellers in particular require careful balancing and restrained bench testing before flight.

## License and attribution

Project documentation, original CAD and bench-test code are provided under Apache-2.0 unless a file states otherwise. Open32Drone source is not duplicated here. See [`NOTICE`](https://github.com/icepaule/IceDrone/blob/main/NOTICE) and [`LICENSE`](https://github.com/icepaule/IceDrone/blob/main/LICENSE).
{% endraw %}
