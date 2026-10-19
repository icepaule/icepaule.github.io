---
layout: default
title: Ice-Kubernetes
parent: Data & Tools
nav_order: 22
---

# Ice-Kubernetes

[View on GitHub](https://github.com/icepaule/Ice-Kubernetes){: .btn .btn-primary .fs-5 .mb-4 .mb-md-0 .mr-2 }

***

**Ice-Kubernetes**

{% raw %}
Migration from Docker Compose stacks to a centralized K3s Kubernetes cluster with GitOps (ArgoCD) and monitoring (Prometheus/Grafana).

## Architecture

```
                    +---------------------+
                    |   GitHub (GitOps)   |
                    |  Ice-Kubernetes.git |
                    +----------+----------+
                               |
                               v
                    +----------+----------+
                    |      ArgoCD         |
                    | (auto-sync to K3s)  |
                    +----------+----------+
                               |
         +---------------------+---------------------+
         |                     |                      |
+--------v--------+  +---------v--------+  +----------v---------+
| K3s Server Node |  | K3s Agent Node   |  | Docker Host        |
| (Control Plane) |  | (GPU Worker)     |  | (Monitored Only)   |
| - Core Platform |  | - GPU Workloads  |  | - NFS Storage      |
| - App Workloads |  | - ML Inference   |  | - Legacy Containers|
+-----------------+  +------------------+  +--------------------+
```

## Cluster Nodes

| Role | Host | OS | CPU | RAM | Storage | GPU | Status |
|------|------|----|-----|-----|---------|-----|--------|
| Server | NUC-HA | Debian 13 | i7-8559U (8T) | 32GB | 1.2TB NVMe | - | Planned |
| Agent | ki01 | Ubuntu 24.04 | 8 vCPU | 16GB | 2.9TB | RTX 3060 12GB | Planned |
| Agent | kibana-osint | Ubuntu 24.04 | 12 vCPU | 32GB | 7.9TB | - | Planned |
| Monitor-only | Synology NAS | DSM 7 | 8 vCPU | 32GB | 22TB+ | - | Docker |

## Core Platform

| Component | Purpose | Deployment |
|-----------|---------|------------|
| [K3s](https://k3s.io) | Lightweight Kubernetes | Binary install |
| [ArgoCD](https://argo-cd.readthedocs.io) | GitOps / Continuous Deployment | Helm chart |
| [Prometheus + Grafana](https://prometheus.io) | Monitoring & Dashboards | Helm chart (kube-prometheus-stack) |
| [MetalLB](https://metallb.universe.tf) | LoadBalancer for bare-metal | Helm chart |
| [Traefik](https://traefik.io) | Ingress Controller | Built into K3s |
| NFS Provisioner | Persistent storage via NFS | Helm chart |

## Workloads to Migrate

| # | Stack | Containers | Complexity |
|---|-------|-----------|------------|
| 1 | Stock Analyzer | 1 | Low |
| 2 | SearXNG | 1 | Low |
| 3 | Ice-Leak-Monitoring | 1 | Low |
| 4 | eBay Selling Assistant | 2 | Low |
| 5 | Epstein Research | 1 | Low |
| 6 | XWiki + AnythingLLM | 5 | Medium |
| 7 | Cribl / ELK Stack | 4 | Medium |
| 8 | Open Archiver | 5 | Medium |
| 9 | Tax-AI Pipeline | 13 | High |

## Not Migrating

| Workload | Reason |
|----------|--------|
| Home Assistant Supervised | Managed by hassio_supervisor, would break if moved |
| InfluxDB, Cribl, Apache2 | Native systemd services, not Docker |
| Synology containers (42) | DSM kernel too old for K3s agent, stays Docker + monitored |

## Quick Start

See [docs/01-prerequisites.md](https://github.com/icepaule/Ice-Kubernetes/blob/main/docs/01-prerequisites.md) to get started.

## Documentation

1. [Prerequisites](https://github.com/icepaule/Ice-Kubernetes/blob/main/docs/01-prerequisites.md)
2. [K3s Server Setup](https://github.com/icepaule/Ice-Kubernetes/blob/main/docs/02-k3s-server-setup.md)
3. [Core Platform](https://github.com/icepaule/Ice-Kubernetes/blob/main/docs/03-core-platform.md)
4. [Workload Migration](https://github.com/icepaule/Ice-Kubernetes/blob/main/docs/04-workload-migration.md)
5. [Agent Nodes](https://github.com/icepaule/Ice-Kubernetes/blob/main/docs/05-agent-nodes.md)
6. [Monitoring](https://github.com/icepaule/Ice-Kubernetes/blob/main/docs/06-monitoring.md)
7. [GitOps with ArgoCD](https://github.com/icepaule/Ice-Kubernetes/blob/main/docs/07-gitops-argocd.md)
8. **[Admin Guide](https://github.com/icepaule/Ice-Kubernetes/blob/main/docs/08-admin-guide.md)** - Day-to-day operations, troubleshooting, deploying new apps

## Directory Structure

```
.
├── docs/                  # Step-by-step documentation
├── manifests/
│   ├── core/              # ArgoCD, Monitoring, MetalLB, NFS
│   └── apps/              # Application workload manifests
├── helm-values/           # Helm chart value overrides
├── scripts/               # Installation & utility scripts
└── .env.example           # Environment variable template
```

## License

MIT
{% endraw %}
