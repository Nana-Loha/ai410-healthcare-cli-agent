# Data Model: Healthcare CLI AI Agent

**Phase**: 1 — Design  
**Date**: 2026-04-20  
**Feature**: specs/001-healthcare-cli-agent/spec.md

All entities are in-memory only. No entity is persisted beyond the active session.

---

## Entities

### SymptomQuery

Represents a user's symptom input for a single analysis request.

| Field | Type | Description | Constraints |
|-------|------|-------------|-------------|
| `symptoms` | `list[str]` | Raw symptom strings from user input | Non-empty; each item non-blank |
| `clarification` | `str \| None` | User's answer to the follow-up clarifying question | Optional; set after clarification step |
| `provider` | `str` | Name of the AI provider to use | One of: `claude`, `openai`, `gemini` |

**State transitions**:
```
RECEIVED → AWAITING_CLARIFICATION (if ambiguous) → ANALYSED
RECEIVED → ANALYSED (if unambiguous)
```

---

### MedicalRecord

Represents the text content of a patient's medical record submitted for summarisation.

| Field | Type | Description | Constraints |
|-------|------|-------------|-------------|
| `content` | `str` | Full text of the medical record | Non-empty |
| `source_label` | `str \| None` | Display label (e.g., filename) for user-facing output | Never contains path that could re-identify patient |
| `provider` | `str` | Name of the AI provider to use | One of: `claude`, `openai`, `gemini` |

**Note**: `content` is never written to disk or logs. `source_label` is a user-provided string for display only.

---

### RecordSummary

The structured output of a medical record summarisation.

| Field | Type | Description |
|-------|------|-------------|
| `diagnoses` | `list[str]` | Listed diagnoses extracted from the record |
| `medications` | `list[str]` | Current medications mentioned |
| `allergies` | `list[str]` | Allergies mentioned |
| `follow_ups` | `list[str]` | Recommended follow-up actions |
| `disclaimer` | `str` | Standard medical disclaimer (always present) |

---

### DrugList

Represents the set of drug names provided by the user for interaction analysis.

| Field | Type | Description | Constraints |
|-------|------|-------------|-------------|
| `drugs` | `list[str]` | Drug names as supplied by the user | Minimum 2 items; each item non-blank |
| `provider` | `str` | Name of the AI provider to use | One of: `claude`, `openai`, `gemini` |

---

### InteractionPair

A single drug–drug interaction within an `InteractionReport`.

| Field | Type | Description |
|-------|------|-------------|
| `drug_a` | `str` | First drug name |
| `drug_b` | `str` | Second drug name |
| `severity` | `Severity` | Enum: `none`, `mild`, `moderate`, `severe` |
| `description` | `str` | Plain-language description of the interaction |
| `precautions` | `list[str]` | Recommended precautions |
| `sources` | `list[str]` | Citation strings or "Based on AI provider knowledge" |

---

### InteractionReport

The full output of a drug interaction check.

| Field | Type | Description |
|-------|------|-------------|
| `pairs` | `list[InteractionPair]` | All checked drug pairs |
| `unrecognised` | `list[str]` | Drug names the provider could not identify |
| `max_severity` | `Severity` | Highest severity across all pairs |
| `disclaimer` | `str` | Standard medical disclaimer (always present) |

---

### SymptomAnalysis

The structured output of a symptom check.

| Field | Type | Description |
|-------|------|-------------|
| `conditions` | `list[Condition]` | Possible conditions with likelihood |
| `next_steps` | `list[str]` | Recommended actions |
| `emergency` | `bool` | True if life-threatening condition detected |
| `sources` | `list[str]` | Citation strings |
| `disclaimer` | `str` | Standard medical disclaimer (always present) |

---

### Condition

A single possible condition within a `SymptomAnalysis`.

| Field | Type | Description |
|-------|------|-------------|
| `name` | `str` | Condition name |
| `likelihood` | `Likelihood` | Enum: `low`, `moderate`, `high` |
| `description` | `str` | Brief plain-language description |

---

### AIProvider (configuration, not patient data)

Represents a configured AI provider connection. Stored only in `ProviderFactory`'s registry during the session.

| Field | Type | Description | Constraints |
|-------|------|-------------|-------------|
| `name` | `str` | Provider identifier | One of: `claude`, `openai`, `gemini` |
| `api_key_env_var` | `str` | Name of the environment variable holding the API key | Never stores the key itself |
| `model_id` | `str` | Default model ID for this provider | e.g., `claude-sonnet-4-6`, `gpt-4o`, `gemini-2.0-flash` |

---

### Session

In-memory session state for a single CLI invocation.

| Field | Type | Description |
|-------|------|-------------|
| `active_provider` | `str` | Currently selected provider name |
| `first_call_confirmed` | `bool` | Whether the user has confirmed the first API call this session |

---

## Enumerations

```
Severity: none | mild | moderate | severe
Likelihood: low | moderate | high
```

---

## Relationships

```
Session ──has──> AIProvider (active)
SymptomQuery ──produces──> SymptomAnalysis
DrugList ──produces──> InteractionReport
InteractionReport ──contains──> InteractionPair[]
SymptomAnalysis ──contains──> Condition[]
MedicalRecord ──produces──> RecordSummary
```
