# CLI Contract: Healthcare AI Agent

**Phase**: 1 — Design  
**Date**: 2026-04-20

This document defines the complete command-line interface contract for the healthcare agent CLI. All subcommands follow `agent <subcommand> [options]`.

---

## Global Options

| Flag | Description | Default |
|------|-------------|---------|
| `--provider <name>` | AI provider to use for this command | Value from config file |
| `--help` | Show help and exit | — |
| `--version` | Print version and exit | — |

---

## Subcommand: `symptoms`

Check possible conditions for a set of symptoms.

```
agent symptoms [OPTIONS]
```

### Options

| Flag | Type | Required | Description |
|------|------|----------|-------------|
| `--input TEXT` | string | Yes (or stdin) | Free-form symptom description |
| `--provider TEXT` | string | No | Override active provider |

### Behaviour

1. If `--input` is omitted and stdin is a TTY, prompts interactively.
2. If stdin is a pipe and `--input` is omitted, reads from stdin.
3. If input is ambiguous, agent asks one clarifying question and waits for a response.
4. If `emergency=true` in analysis result, prints emergency prompt before all other output.
5. Always appends the standard medical disclaimer to output.

### Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Analysis completed successfully |
| 1 | Empty input |
| 2 | Provider error (API unavailable, invalid key) |
| 3 | User aborted confirmation prompt |

### Example

```
$ agent symptoms --input "severe chest pain, shortness of breath"

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

## Subcommand: `summarize`

Summarize a medical record.

```
agent summarize [OPTIONS]
```

### Options

| Flag | Type | Required | Description |
|------|------|----------|-------------|
| `--file PATH` | path | Yes (or `--input`) | Path to a plain-text medical record file |
| `--input TEXT` | string | Yes (or `--file`) | Inline record text |
| `--provider TEXT` | string | No | Override active provider |

### Behaviour

1. Exactly one of `--file` or `--input` must be provided.
2. If `--file` is provided, reads file content into memory; does not retain path after reading.
3. For records exceeding the provider's context window, chunks the text and merges summaries.
4. Always appends the standard medical disclaimer to output.
5. No content is written to disk or logs.

### Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Summary completed successfully |
| 1 | Neither `--file` nor `--input` provided, or both provided |
| 2 | File not found or unreadable |
| 3 | Provider error |
| 4 | User aborted confirmation prompt |

### Example

```
$ agent summarize --file discharge_summary.txt

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

## Subcommand: `interactions`

Check drug–drug interactions.

```
agent interactions [OPTIONS]
```

### Options

| Flag | Type | Required | Description |
|------|------|----------|-------------|
| `--drugs TEXT` | comma-separated string | Yes | Drug names to check (minimum 2) |
| `--provider TEXT` | string | No | Override active provider |

### Behaviour

1. Parses `--drugs` as a comma-separated list; trims whitespace from each name.
2. Requires at least 2 drug names; exits with code 1 if fewer than 2 provided.
3. If `max_severity == severe`, displays a confirmation prompt before showing results.
4. Flags any unrecognised drug names with a warning.
5. Always appends the standard medical disclaimer to output.

### Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Interaction check completed |
| 1 | Fewer than 2 drug names provided |
| 2 | Provider error |
| 3 | User aborted confirmation prompt |

### Example

```
$ agent interactions --drugs "warfarin, aspirin"

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

## Subcommand: `config`

View or set agent configuration (no patient data).

```
agent config [OPTIONS]
```

### Options

| Flag | Type | Required | Description |
|------|------|----------|-------------|
| `--set-provider TEXT` | string | No | Set the default AI provider |
| `--show` | flag | No | Print current configuration |

### Behaviour

1. Configuration is stored at `~/.config/healthcare-agent/config.toml`.
2. Only provider name is stored; API keys are never written to config.
3. Valid provider names: `claude`, `openai`, `gemini`.

### Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Configuration updated or shown |
| 1 | Invalid provider name |

### Example

```
$ agent config --set-provider gemini
Default provider set to: gemini

$ agent config --show
Default provider: gemini
Config file: ~/.config/healthcare-agent/config.toml
```

---

## Standard Medical Disclaimer

All commands that return healthcare information MUST append the following line to output:

```
⚕️  This information is not a substitute for professional medical advice, diagnosis, or treatment.
```

## Standard Output Format

- Human-readable text by default (no flags required).
- Sections separated by a horizontal rule (`───`).
- Warnings and emergency prompts prefixed with `⚠️ `.
- Disclaimer prefixed with `⚕️ `.
- Errors written to stderr; all normal output to stdout.
