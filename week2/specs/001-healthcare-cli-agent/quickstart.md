# Quickstart: Healthcare CLI AI Agent

**Date**: 2026-04-20

---

## Prerequisites

- Python 3.12+
- `uv` package manager installed
- API key(s) for at least one provider:
  - Claude: `ANTHROPIC_API_KEY`
  - OpenAI: `OPENAI_API_KEY`
  - Google Gemini: `GOOGLE_API_KEY`

---

## Installation

```bash
# Clone the repository
git clone <repo-url>
cd ai410

# Install dependencies
uv sync

# (Optional) Install as a command
uv pip install -e .
```

---

## Set Your API Key

```bash
export ANTHROPIC_API_KEY="your-key-here"
# or
export OPENAI_API_KEY="your-key-here"
# or
export GOOGLE_API_KEY="your-key-here"
```

---

## Configure Default Provider

```bash
agent config --set-provider claude
```

---

## Check Symptoms

```bash
agent symptoms --input "headache, fever, stiff neck"
```

---

## Summarize a Medical Record

```bash
agent summarize --file path/to/record.txt
```

---

## Check Drug Interactions

```bash
agent interactions --drugs "metformin, lisinopril, aspirin"
```

---

## Use a Specific Provider for a Single Command

```bash
agent symptoms --input "chest tightness" --provider openai
```

---

## Run Tests

```bash
uv run pytest
```

---

## Disclaimer

All output from this tool includes the following notice:

> This information is not a substitute for professional medical advice, diagnosis, or treatment.
