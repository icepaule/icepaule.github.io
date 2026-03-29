---
layout: default
title: IcePhotos
parent: Data & Tools
nav_order: 13
---

# IcePhotos

[View on GitHub](https://github.com/icepaule/IcePhotos){: .btn .btn-primary .fs-5 .mb-4 .mb-md-0 .mr-2 }

***

**IcePhotos**

**Immich on Synology DS1821+ with Remote GPU Acceleration (NVIDIA RTX 3060)**

A production-ready setup for running [Immich](https://immich.app) on a Synology NAS with GPU-accelerated machine learning on a separate server.

## Architecture

```
┌─────────────────────────────────┐     ┌──────────────────────────────┐
│  Synology DS1821+ (NAS)         │     │  GPU Server (NVIDIA RTX 3060)│
│                                 │     │                              │
│  ┌───────────────────────────┐  │     │  ┌────────────────────────┐  │
│  │ Immich Server    :2283    │──┼─────┼─▶│ Immich ML (CUDA) :3003 │  │
│  └───────────────────────────┘  │     │  └────────────────────────┘  │
│  ┌───────────────────────────┐  │     │  ┌────────────────────────┐  │
│  │ PostgreSQL (pgvecto.rs)   │  │     │  │ Ollama          :11434 │  │
│  └───────────────────────────┘  │     │  └────────────────────────┘  │
│  ┌───────────────────────────┐  │     └──────────────────────────────┘
│  │ Redis (Valkey)            │  │
│  └───────────────────────────┘  │
│                                 │
│  📁 /volume1/photo (External)   │
│  📁 /volume2/docker/immich      │
└─────────────────────────────────┘
```

## Features

| Feature | Backend | Location |
|---|---|---|
| Face Detection + Clustering | Immich ML (CUDA) | GPU Server |
| Smart Search / CLIP | Immich ML (CUDA) | GPU Server |
| OCR | Immich ML (CUDA) | GPU Server |
| Image Captions | Ollama (Vision Models) | GPU Server |
| Photo Storage | Synology RAID6 | NAS |
| Database (PostgreSQL) | pgvecto.rs + VectorChord | NAS |
| External Library | Synology Photos read-only | NAS |

## Quick Start

See the full [Setup Guide](https://icepaule.github.io/IcePhotos/) for detailed step-by-step instructions.

## Repository Structure

```
├── README.md                          # This file
├── docs/                              # GitHub Pages documentation
│   └── index.md                       # Full setup guide
├── synology/                          # Synology NAS configuration
│   ├── docker-compose.yml             # Immich Server + DB + Redis
│   └── .env.example                   # Environment template (no secrets)
└── gpu-server/                        # GPU Server configuration
    └── docker-compose.yml             # Immich ML with CUDA
```

## License

MIT
