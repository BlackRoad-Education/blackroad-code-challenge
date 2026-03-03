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
