# PromptHub

> Git-like version control for AI prompts — with semantic diff and output regression testing.

Most teams manage prompts in Notion, Google Docs, or files named `prompt_v2_FINAL.txt`.
PromptHub treats prompts as first-class artifacts with real version history, semantic diffing,
and behavioural regression testing.

## Why PromptHub

- `git diff` shows you line changes. PromptHub shows you *meaning* changes.
- Know exactly when a prompt change breaks existing behaviour before you ship it.
- Roll back to any previous version in one command.

## Installation

```bash
git clone https://github.com/remin-franklin-eliyas/prompthub.git
cd prompthub
python3 -m venv venv
source venv/bin/activate
pip install -e .
```

Requires [Ollama](https://ollama.com) for regression testing:
```bash
ollama pull llama3.2
```

## Usage

```bash
# Initialise a repo in your project
prompthub init

# Track a prompt file
prompthub add system_prompt.txt

# Commit the current version
prompthub commit -m "initial version"

# Make changes, commit again
prompthub commit -m "added JSON output format"

# See full version history
prompthub log

# Semantic diff between versions
prompthub diff v1 v2

# Add regression test cases
prompthub test-add --name "basic question" --input "What is the capital of France?"

# Run regression tests between versions
prompthub test-run v1 v2

# Roll back to a previous version
prompthub rollback v1
```

## Example Output

### Semantic Diff
PROMPT DIFF  v1 → v2

─────────────────────────────────────────

Semantic distance:  0.53  (significant change)
STRUCTURAL CHANGES

Added: format
Added: tone

~ Modified: length  24 chars longer

CHARACTER DELTA

v1: 55 chars

v2: 79 chars

Δ:  +24 chars

### Regression Report
REGRESSION REPORT  v1 → v2

─────────────────────────────────────────

Test: basic question

Status:        CHANGED

Semantic shift: 0.27  (moderate change)
v1 output: The capital of France is Paris.

v2 output: {"capital": "Paris"}

## Stack

- Python 3.11+
- Typer + Rich (CLI)
- SQLite (local version storage)
- sentence-transformers (semantic diff)
- Ollama (regression testing)

## Built by

Remin Franklin — [GitHub](https://github.com/remin-franklin-eliyas) · [LinkedIn](https://linkedin.com/in/remin-franklin-eliyas)
EOF