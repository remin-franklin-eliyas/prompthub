# PromptHub

Git-like version control for AI prompts.

## Features
- Track and version prompt files
- Commit snapshots with messages
- View full version history
- Roll back to any previous version
- Semantic diff between versions *(coming Week 2)*
- Output regression testing *(coming Week 3)*

## Installation
```bash
git clone https://github.com/remin-franklin-eliyas/prompthub.git
cd prompthub
python3 -m venv venv
source venv/bin/activate
pip install -e .
```

## Usage
```bash
prompthub init
prompthub add my_prompt.txt
prompthub commit -m "initial version"
prompthub log
prompthub rollback v1
```

## Built by
Remin Franklin
