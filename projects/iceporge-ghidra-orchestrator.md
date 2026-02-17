---
layout: default
title: IcePorge-Ghidra-Orchestrator
parent: Security & Malware Analysis
nav_order: 7
---

# IcePorge-Ghidra-Orchestrator

[View on GitHub](https://github.com/icepaule/IcePorge-Ghidra-Orchestrator){: .btn .btn-primary .fs-5 .mb-4 .mb-md-0 .mr-2 }

***

**Automated Malware Reverse Engineering with AI-Powered Deobfuscation**

Part of the [IcePorge](https://github.com/icepaule/IcePorge) Malware Analysis Stack.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

***

## Overview

The Ghidra Orchestrator automates static malware analysis using Ghidra's headless mode combined with LLM-driven code deobfuscation. It integrates seamlessly with CAPE Sandbox for end-to-end malware analysis workflows.

### Key Features

- **Headless Ghidra Analysis** - Automated decompilation without GUI
- **LLM Deobfuscation** - AI-powered code understanding using Ollama
- **CAPE Integration** - REST API for automated sample submission
- **Forensic Logging** - Complete audit trail of all analysis actions
- **Knowledge Base** - Malware pattern recognition from curated datasets

***

## Architecture

```
                    CAPE Sandbox (capev2)
                          |
                          v
               POST /analyze (sample)
                          |
                          v
    +--------------------------------------------------+
    |           Ghidra Orchestrator (ki01)             |
    |                                                  |
    |  +--------------------------------------------+  |
    |  |            api_server.py                   |  |
    |  |          Flask REST API (:5000)            |  |
    |  +--------------------------------------------+  |
    |                      |                           |
    |      +---------------+---------------+           |
    |      v               v               v           |
    |  +----------+  +-----------+  +------------+    |
    |  |orchestr- |  |llm_deobf- |  |knowledge_  |    |
    |  |ator.py   |  |uscator.py |  |loader.py   |    |
    |  +----------+  +-----------+  +------------+    |
    |      |               |               |           |
    |      v               v               v           |
    |  +----------+  +-----------+  +------------+    |
    |  | Ghidra   |  |  Ollama   |  | YAML/JSON  |    |
    |  | Headless |  | (qwen2.5) |  | Knowledge  |    |
    |  +----------+  +-----------+  +------------+    |
    +--------------------------------------------------+
                          |
                          v
           /mnt/cape-data/ghidra/results/
```

***

## Components

| File | Description |
|------|-------------|
| `api_server.py` | Flask REST API for CAPE integration |
| `orchestrator.py` | Main analysis engine with Ghidra headless |
| `llm_deobfuscator.py` | LLM-based code deobfuscation engine |
| `knowledge_loader.py` | Malware knowledge base loader |
| `gpu_monitor.py` | GPU utilization monitoring for Ollama |
| `scripts/ExportAnalysis.py` | Ghidra script for data extraction |

***

## Installation

### Prerequisites

- Ghidra 11.x installed in `/opt/ghidra`
- Ollama with `qwen2.5-coder:14b` model
- Python 3.10+
- NVIDIA GPU (recommended for LLM inference)

### Setup

```bash
# Clone repository
git clone https://github.com/icepaule/IcePorge-Ghidra-Orchestrator.git
cd IcePorge-Ghidra-Orchestrator

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install flask requests

# Configure (copy and edit)
cp config/malware_knowledge.yaml.example config/malware_knowledge.yaml

# Start API server
python api_server.py
```

***

## API Endpoints

### Health Check
```bash
curl http://localhost:5000/health
```

Response:
```json
{
  "status": "healthy",
  "service": "ghidra-orchestrator",
  "version": "2.0-llm",
  "ghidra_available": true,
  "llm_available": true
}
```

### Analyze Sample
```bash
curl -X POST http://localhost:5000/analyze \
  -H "Content-Type: application/json" \
  -d '{"file_path": "/path/to/sample.exe", "task_id": "12345"}'
```

### Get Results
```bash
curl http://localhost:5000/results/12345
```

***

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `GHIDRA_PATH` | `/opt/ghidra` | Ghidra installation path |
| `OLLAMA_URL` | `http://localhost:11434` | Ollama API endpoint |
| `OLLAMA_MODEL` | `qwen2.5-coder:14b` | LLM model for deobfuscation |

### Knowledge Base

The `config/malware_knowledge.yaml` contains:
- Known API hash values
- Malware family indicators
- Obfuscation patterns

***

## Integration with CAPE

Add to CAPE processing modules to automatically analyze samples:

```python
# In CAPE processing module
import requests

def process_with_ghidra(file_path, task_id):
    response = requests.post(
        "http://ki01:5000/analyze",
        json={"file_path": file_path, "task_id": str(task_id)}
    )
    return response.json()
```

***

## Output

Analysis results are stored in `/mnt/cape-data/ghidra/results/<task_id>/`:

```
<task_id>/
├── analysis_report.json    # Structured analysis results
├── decompiled/             # Decompiled function code
├── strings.txt             # Extracted strings
├── imports.txt             # Import table
├── exports.txt             # Export table
└── forensic.log            # Complete audit trail
```

***

## Forensic Logging

Every analysis action is documented:

```
[2026-01-22T10:30:00] === Forensic Analysis Log ===
[2026-01-22T10:30:00] Task ID: 12345
[2026-01-22T10:30:01] ACTION: file_received
[2026-01-22T10:30:02] ACTION: hash_calculated
[2026-01-22T10:30:05] ACTION: ghidra_analysis_started
[2026-01-22T10:30:45] ACTION: llm_deobfuscation
[2026-01-22T10:31:00] FINDING [HIGH]: [obfuscation] RC4 decryption detected
```

***

## Service Management

```bash
# Start as systemd service
sudo systemctl start ghidra-orchestrator

# View logs
sudo journalctl -u ghidra-orchestrator -f

# Check status
sudo systemctl status ghidra-orchestrator
```

***

## License

MIT License - See [LICENSE](LICENSE)

**Author:** Michael Pauli
- GitHub: [@icepaule](https://github.com/icepaule)
- Email: info@mpauli.de
