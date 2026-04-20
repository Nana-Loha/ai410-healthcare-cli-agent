# AI410 — Healthcare CLI Agent

A CLI-based AI agent for healthcare queries: symptom checking, medical record summarization, and drug interaction checking — powered by your choice of Claude, GPT-4, or Gemini.

> **Medical Disclaimer**: This tool is not a substitute for professional medical advice, diagnosis, or treatment. Always consult a qualified healthcare provider.

---

## Features

- **Symptom checking** — analyse free-form symptoms, detect emergencies, ask one clarifying question when input is ambiguous
- **Medical record summarization** — produce a structured summary (diagnoses, medications, allergies, follow-ups) from inline text or a file
- **Drug interaction checking** — report severity levels and precautions for any combination of drugs, with a confirmation gate for severe interactions
- **Multi-provider AI support** — switch between Claude, GPT-4, and Gemini per command or set a persistent default

---

## Prerequisites

- Python 3.12+
- [`uv`](https://github.com/astral-sh/uv) package manager
- At least one provider API key (set as an environment variable):

| Provider | Environment Variable |
|---|---|
| Anthropic Claude | `ANTHROPIC_API_KEY` |
| OpenAI GPT-4 | `OPENAI_API_KEY` |
| Google Gemini | `GOOGLE_API_KEY` |

---

## Installation

```bash
# Clone the repository
git clone <repo-url>
cd ai410

# Install dependencies
uv sync

# (Optional) Install as a runnable command
uv pip install -e .
```

---

## Configuration

Set your default AI provider once:

```bash
agent config --set-provider claude
```

Valid provider names: `claude`, `openai`, `gemini`.

Provider configuration is stored at `~/.config/healthcare-agent/config.toml` and contains only the provider name — **API keys are never written to the config file**. Keys are read exclusively from environment variables at runtime.

```bash
# View current configuration
agent config --show
```

---

## Usage

All commands follow the pattern `agent <subcommand> [options]`.

### Global options

| Flag | Description |
|---|---|
| `--provider TEXT` | Override the active provider for this command |
| `--help` | Show help and exit |
| `--version` | Print version and exit |

---

### `symptoms` — Check symptoms

Analyse one or more symptoms and receive possible conditions, likelihoods, recommended next steps, and cited sources. Life-threatening symptoms surface an emergency prompt before all other output.

```bash
agent symptoms [OPTIONS]
```

| Flag | Type | Required | Description |
|---|---|---|---|
| `--input TEXT` | string | Yes (or stdin) | Free-form symptom description |
| `--provider TEXT` | string | No | Override active provider |

**Example**:

```bash
agent symptoms --input "severe chest pain, shortness of breath"
```

```text
⚠️  EMERGENCY: These symptoms may indicate a life-threatening condition.
    Call emergency services (911) immediately.
    ─────────────────────────────────────────────────────

Possible conditions:
  • Acute myocardial infarction (High likelihood)
    Immediate medical attention required.

Next steps:
  1. Call 911 immediately.
  2. Chew aspirin if not allergic and no contraindications.

Sources: Based on Claude AI provider knowledge.

⚕️  This information is not a substitute for professional medical advice,
    diagnosis, or treatment.
```

---

### `summarize` — Summarize a medical record

Produce a structured summary of a plain-text medical record provided inline or via a file path. Long records are chunked and merged automatically. No content is written to disk or logs.

```bash
agent summarize [OPTIONS]
```

| Flag | Type | Required | Description |
|---|---|---|---|
| `--file PATH` | path | Yes (or `--input`) | Path to a plain-text medical record file |
| `--input TEXT` | string | Yes (or `--file`) | Inline record text |
| `--provider TEXT` | string | No | Override active provider |

**Example**:

```bash
agent summarize --file discharge_summary.txt
```

```text
Medical Record Summary
──────────────────────
Diagnoses:
  • Type 2 Diabetes Mellitus
  • Hypertension

Medications:
  • Metformin 500mg twice daily
  • Lisinopril 10mg once daily

Allergies:
  • Penicillin (rash)

Follow-up Recommendations:
  1. HbA1c check in 3 months.
  2. Blood pressure monitoring weekly.

⚕️  This information is not a substitute for professional medical advice,
    diagnosis, or treatment.
```

---

### `interactions` — Check drug interactions

Report known interactions, severity levels, and precautions for two or more drugs. A confirmation prompt is shown before displaying severe interactions.

```bash
agent interactions [OPTIONS]
```

| Flag | Type | Required | Description |
|---|---|---|---|
| `--drugs TEXT` | comma-separated string | Yes | Drug names to check (minimum 2) |
| `--provider TEXT` | string | No | Override active provider |

**Example**:

```bash
agent interactions --drugs "warfarin, aspirin"
```

```text
⚠️  SEVERE interaction detected. Do you want to proceed? [y/N]: y

Drug Interaction Report
───────────────────────
warfarin ↔ aspirin
  Severity: SEVERE
  Description: Combined use significantly increases bleeding risk.
  Precautions:
    • Avoid concurrent use unless directed by a physician.
    • Monitor INR closely if combination is necessary.
  Sources: Based on Claude AI provider knowledge.

⚕️  This information is not a substitute for professional medical advice,
    diagnosis, or treatment.
```

---

### `config` — Manage configuration

View or update the agent's provider configuration. No patient data is involved.

```bash
agent config [OPTIONS]
```

| Flag | Type | Required | Description |
|---|---|---|---|
| `--set-provider TEXT` | string | No | Set the default AI provider |
| `--show` | flag | No | Print current configuration |

**Example**:

```bash
agent config --set-provider gemini
# Default provider set to: gemini

agent config --show
# Default provider: gemini
# Config file: ~/.config/healthcare-agent/config.toml
```

---

## Exit Codes

| Code | Meaning |
|---|---|
| 0 | Command completed successfully |
| 1 | Invalid or missing input (empty symptoms, fewer than 2 drugs, missing `--file`/`--input`, invalid provider name) |
| 2 | Provider error (API unavailable, missing or invalid API key, file not found) |
| 3 | User aborted a confirmation prompt |
| 4 | Both `--file` and `--input` provided to `summarize` (mutually exclusive) |

---

## Development

### Install dependencies

```bash
uv sync
```

### Run tests

```bash
uv run pytest
```

### Project layout

```
src/
├── cli/
│   ├── main.py          # CLI entry point and subcommands
│   └── output.py        # Rich-formatted output helpers
├── providers/
│   ├── base.py          # AIProvider protocol and ProviderFactory
│   ├── claude.py        # Anthropic Claude adapter
│   ├── gpt.py           # OpenAI GPT-4 adapter
│   └── gemini.py        # Google Gemini adapter
├── services/
│   ├── symptoms.py      # Symptom analysis service
│   ├── summarizer.py    # Medical record summarization service
│   └── interactions.py  # Drug interaction service
└── config.py            # Config loading and Session model

tests/
├── unit/
├── integration/
└── contract/
```

### Contribution guidelines

- Use `uv` exclusively — never `pip`
- One feature per branch
- Tests go in `/tests`, using `pytest`
- Never store or log patient data
- Always include the medical disclaimer in any output that returns healthcare information

---

## License

License not yet specified.
