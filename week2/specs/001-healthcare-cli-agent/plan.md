# Implementation Plan: Healthcare CLI AI Agent

**Branch**: `001-healthcare-cli-agent` | **Date**: 2026-04-20 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/001-healthcare-cli-agent/spec.md`

## Summary

Build a CLI-based healthcare AI agent supporting symptom checking, medical record summarization, and drug interaction checking across multiple AI providers (Claude, GPT-4, Gemini). The agent enforces strict patient-data safety (no persistence), mandatory medical disclaimers, and confirmation prompts for critical actions. Implemented in Python 3.12+ using the `anthropic`, `openai`, and `google-generativeai` SDKs with a `typer`-based CLI.

## Technical Context

**Language/Version**: Python 3.12+
**Primary Dependencies**: anthropic, openai, google-generativeai, typer, rich, pydantic
**Storage**: N/A (no persistence; session-only in-memory state)
**Testing**: pytest + pytest-mock
**Target Platform**: Cross-platform terminal (Linux, macOS, Windows)
**Project Type**: CLI application
**Performance Goals**: Symptom response ≤ 30s; drug interaction check (10 drugs) ≤ 45s under normal network
**Constraints**: Zero patient data persisted; all AI calls streamed or handled in-process; no external logging of user data
**Scale/Scope**: Single-user, single-session; no concurrency needed for v1

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

The project constitution is an unfilled template with no active constraints. No gates apply. All design decisions default to spec requirements and CLAUDE.md conventions.

**Post-design re-check**: No violations detected. The single-project structure, no-persistence model, and test-first approach are all consistent with the spirit of the template principles.

## Project Structure

### Documentation (this feature)

```text
specs/001-healthcare-cli-agent/
├── plan.md              # This file (/speckit-plan command output)
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
│   └── cli-contract.md
└── tasks.md             # Phase 2 output (/speckit-tasks command)
```

### Source Code (repository root)

```text
src/
├── cli/
│   ├── __init__.py
│   ├── main.py          # typer app entry point, subcommands
│   └── output.py        # rich-formatted output helpers, disclaimer injection
├── providers/
│   ├── __init__.py
│   ├── base.py          # AIProvider abstract base class
│   ├── claude.py        # Anthropic Claude provider
│   ├── gpt.py           # OpenAI GPT-4 provider
│   └── gemini.py        # Google Gemini provider
├── services/
│   ├── __init__.py
│   ├── symptoms.py      # Symptom checking logic + emergency detection
│   ├── summarizer.py    # Medical record chunking + summarization
│   └── interactions.py  # Drug interaction checking + severity detection
└── config.py            # Provider config loading (env vars + config file)

tests/
├── unit/
│   ├── test_symptoms.py
│   ├── test_summarizer.py
│   ├── test_interactions.py
│   └── test_config.py
├── integration/
│   └── test_provider_routing.py
└── contract/
    └── test_cli_contract.py
```

**Structure Decision**: Single project layout. The CLI, provider abstraction, and service logic are cleanly separated by responsibility. No backend/frontend split needed for a CLI tool.

## Complexity Tracking

No constitution violations to justify.
