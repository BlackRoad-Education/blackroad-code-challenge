<!-- BlackRoad SEO Enhanced -->

# ulackroad code challenge

> Part of **[BlackRoad OS](https://blackroad.io)** — Sovereign Computing for Everyone

[![BlackRoad OS](https://img.shields.io/badge/BlackRoad-OS-ff1d6c?style=for-the-badge)](https://blackroad.io)
[![BlackRoad Education](https://img.shields.io/badge/Org-BlackRoad-Education-2979ff?style=for-the-badge)](https://github.com/BlackRoad-Education)
[![License](https://img.shields.io/badge/License-Proprietary-f5a623?style=for-the-badge)](LICENSE)

**ulackroad code challenge** is part of the **BlackRoad OS** ecosystem — a sovereign, distributed operating system built on edge computing, local AI, and mesh networking by **BlackRoad OS, Inc.**

## About BlackRoad OS

BlackRoad OS is a sovereign computing platform that runs AI locally on your own hardware. No cloud dependencies. No API keys. No surveillance. Built by [BlackRoad OS, Inc.](https://github.com/BlackRoad-OS-Inc), a Delaware C-Corp founded in 2025.

### Key Features
- **Local AI** — Run LLMs on Raspberry Pi, Hailo-8, and commodity hardware
- **Mesh Networking** — WireGuard VPN, NATS pub/sub, peer-to-peer communication
- **Edge Computing** — 52 TOPS of AI acceleration across a Pi fleet
- **Self-Hosted Everything** — Git, DNS, storage, CI/CD, chat — all sovereign
- **Zero Cloud Dependencies** — Your data stays on your hardware

### The BlackRoad Ecosystem
| Organization | Focus |
|---|---|
| [BlackRoad OS](https://github.com/BlackRoad-OS) | Core platform and applications |
| [BlackRoad OS, Inc.](https://github.com/BlackRoad-OS-Inc) | Corporate and enterprise |
| [BlackRoad AI](https://github.com/BlackRoad-AI) | Artificial intelligence and ML |
| [BlackRoad Hardware](https://github.com/BlackRoad-Hardware) | Edge hardware and IoT |
| [BlackRoad Security](https://github.com/BlackRoad-Security) | Cybersecurity and auditing |
| [BlackRoad Quantum](https://github.com/BlackRoad-Quantum) | Quantum computing research |
| [BlackRoad Agents](https://github.com/BlackRoad-Agents) | Autonomous AI agents |
| [BlackRoad Network](https://github.com/BlackRoad-Network) | Mesh and distributed networking |
| [BlackRoad Education](https://github.com/BlackRoad-Education) | Learning and tutoring platforms |
| [BlackRoad Labs](https://github.com/BlackRoad-Labs) | Research and experiments |
| [BlackRoad Cloud](https://github.com/BlackRoad-Cloud) | Self-hosted cloud infrastructure |
| [BlackRoad Forge](https://github.com/BlackRoad-Forge) | Developer tools and utilities |

### Links
- **Website**: [blackroad.io](https://blackroad.io)
- **Documentation**: [docs.blackroad.io](https://docs.blackroad.io)
- **Chat**: [chat.blackroad.io](https://chat.blackroad.io)
- **Search**: [search.blackroad.io](https://search.blackroad.io)

---


> Coding challenge platform with test runner

Part of the [BlackRoad OS](https://blackroad.io) ecosystem — [BlackRoad-Education](https://github.com/BlackRoad-Education)

---

# BlackRoad Code Challenge Platform

Coding challenge platform with subprocess-based multi-language test runner, grading, and leaderboard.

## Features

- **Multi-language**: Python, JavaScript (Node), Bash execution
- **Test Runner**: Subprocess with configurable timeout, stdin injection, stdout comparison
- **Grading**: Weighted test case scoring, status (Accepted/WA/TLE/Runtime Error)
- **Hidden Tests**: Public + hidden test case support
- **Challenges**: Two Sum, FizzBuzz built-in; extensible dataclass API
- **Leaderboard**: Per-challenge and global rankings
- **Explanations**: Auto-generated step-by-step problem breakdowns
- **AI Assistant (Ollama)**: All AI requests are routed to your local Ollama instance — no external providers

## AI / Ollama Routing

Mentioning any of the following handles in a message automatically routes the
request to your local [Ollama](https://ollama.com) instance:

| Handle | Routes to |
|---|---|
| `@ollama` | Ollama (local) |
| `@copilot` | Ollama (local) |
| `@lucidia` | Ollama (local) |
| `@blackboxprogramming` | Ollama (local) |

**No request is ever sent to an external AI provider.**

### Prerequisites

1. Install Ollama: <https://ollama.com/download>
2. Pull a model: `ollama pull llama3`
3. Start the server: `ollama serve`

### Usage

```python
from code_challenge import CodeChallengePlatform

platform = CodeChallengePlatform()   # connects to http://localhost:11434 by default

# Any of these are equivalent — all go straight to Ollama:
print(platform.ask_ai("@copilot what is a hash map?"))
print(platform.ask_ai("@lucidia explain binary search"))
print(platform.ask_ai("@blackboxprogramming solve two sum in Python"))
print(platform.ask_ai("@ollama what is time complexity?"))

# Plain messages also go to Ollama (no external provider fallback):
print(platform.ask_ai("What is dynamic programming?"))
```

You can customise the Ollama endpoint and model:

```python
platform = CodeChallengePlatform(
    ollama_base_url="http://localhost:11434",
    ollama_model="mistral",
)
```

## Usage

```bash
python code_challenge.py
```

## License

Proprietary — BlackRoad OS, Inc. All rights reserved.
