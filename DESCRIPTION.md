# PromptHub

> Git-like version control for AI prompts — with semantic diff and output regression testing.

## The Problem

Every AI engineer manages prompts like this:
- Files named `prompt_v2_FINAL_REAL.txt`
- Copy-pasted into Notion with no history
- No idea why outputs changed after a small tweak
- No way to prove a prompt change improved things

## The Solution

```bash
pip install prompthub-cli
```

PromptHub treats prompts as first-class artifacts with real version history,
semantic diffing, and behavioural regression testing.

## What Makes It Different

`git diff` tells you line 3 changed.
PromptHub tells you the **meaning** changed.
PROMPT DIFF  v1 → v2

─────────────────────────────────────────

Semantic distance:  0.53  (significant change)
STRUCTURAL CHANGES

Added: format constraint
Added: expert tone

~ Modified: length  24 chars longer

CHARACTER DELTA

v1: 55 chars

v2: 79 chars

Δ:  +24 chars

## Features

- **Version control** — snapshot any prompt file with a commit message
- **Semantic diff** — cosine distance on sentence embeddings, not line diffs
- **Structural detection** — format, tone, length, reasoning, role changes
- **Output regression testing** — run both versions through a local LLM, compare outputs
- **Full rollback** — restore any previous version in one command
- **Fully local** — SQLite storage, Ollama for inference, no API costs, your prompts stay yours

## Installation

```bash
pip install prompthub-cli
```

Requires [Ollama](https://ollama.com) for regression testing:

```bash
ollama pull llama3.2
```

## Quick Start

```bash
# Initialise a repo in your project
prompthub init

# Track a prompt file
prompthub add system_prompt.txt

# Commit the current version
prompthub commit -m "initial version"

# Make changes and commit again
prompthub commit -m "added JSON output format"

# See full version history
prompthub log

# Semantic diff between versions
prompthub diff v1 v2

# Add a regression test case
prompthub test-add --name "basic question" --input "What is the capital of France?"

# Run regression tests between versions
prompthub test-run v1 v2

# Roll back to a previous version
prompthub rollback v1
```

## Regression Testing Output
REGRESSION REPORT  v1 → v2

─────────────────────────────────────────

Test: basic question

Status:        CHANGED

Semantic shift: 0.27  (moderate change)
v1 output: The capital of France is Paris.

v2 output: {"capital": "Paris"}
Test: explanation test

Status:        CHANGED

Semantic shift: 0.53  (significant change)
v1 output: A neural network is a computer system inspired by...

v2 output: {"type": "object", "properties": {"name": "Neural Network"...

## Stack

- Python 3.11+
- Typer + Rich (CLI)
- SQLite (local version storage)
- sentence-transformers (semantic diff)
- Ollama (regression testing)

## Links

- GitHub: [github.com/remin-franklin-eliyas/prompthub](https://github.com/remin-franklin-eliyas/prompthub)
- PyPI: [pypi.org/project/prompthub-cli](https://pypi.org/project/prompthub-cli)

## Author

Built by Remin Franklin
[LinkedIn](https://linkedin.com/in/remin-franklin-eliyas) · [GitHub](https://github.com/remin-franklin-eliyas)