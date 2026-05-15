# AI410 — Healthcare AI Agent: Sprint 3

A LangGraph-powered stateful agent for healthcare tasks: SOAP note generation, drug interaction checking, and symptom analysis — with human-in-the-loop safety checkpoints and a Streamlit web deployment path.

> **Medical Disclaimer**: This tool is not a substitute for professional medical advice, diagnosis, or treatment. Always consult a qualified healthcare provider.

---

## Features

- **SOAP summarization** — generate structured Subjective / Objective / Assessment / Plan notes from free-form clinical text, with ICD-10 code suggestions requiring clinician approval
- **Drug interaction checking** — report severity levels and precautions for any drug combination; severe interactions route to a human checkpoint (powered by Claude Opus 4.6 for safety-critical reasoning)
- **Symptom analysis** — analyse free-form symptoms, detect emergencies, surface risk level and recommended next steps
- **Human-in-the-loop (HITL) checkpoints** — high-risk results and ICD-10 codes pause execution for human approval before output is shown
- **Self-correcting retry loop** — evaluator node retries failed tool calls up to 3 times before escalating
- **State persistence** — patient allergies, medications, and conditions carry across conversation turns

---

## Architecture

The agent is a four-node [LangGraph](https://github.com/langchain-ai/langgraph) `StateGraph`. Every turn flows through the same pipeline; conditional edges handle retry and HITL branching.

```
planner → tool → evaluator ──(error + retries < 3)──→ tool   (retry loop)
                           ├──(needs_human = true)───→ hitl → END
                           └──(ok)────────────────────────────→ END
```

| Node | File | Responsibility |
|---|---|---|
| **planner** | `nodes.py` | Detect intent: `soap`, `drug_check`, or `symptom` |
| **tool** | `nodes.py` | Call the appropriate Claude-backed tool |
| **evaluator** | `nodes.py` | Check output quality; trigger retry or HITL |
| **hitl** | `nodes.py` | Pause for human approval (CLI: `input()`; Streamlit: `st.button()`) |

### Shared state (`state.py`)

`AgentState` is a `TypedDict` passed between all nodes — think of it as the patient chart for the session:

| Field | Type | Description |
|---|---|---|
| `user_input` | `str` | Raw user message |
| `task_type` | `str` | `"soap"` / `"drug_check"` / `"symptom"` |
| `soap_summary` | `str` | Formatted SOAP note |
| `icd10_codes` | `list` | ICD-10 suggestions pending clinician approval |
| `risk_level` | `str` | `"low"` / `"medium"` / `"high"` |
| `needs_human` | `bool` | Triggers HITL node when `True` |
| `human_approved` | `bool` | Set by HITL node after approval |
| `retry_count` | `int` | Incremented on each tool retry |
| `allergies` / `current_medications` / `conditions` | `list` | Persisted across turns |

### Tools (`tools.py`)

| Tool | Model | Purpose |
|---|---|---|
| `check_symptoms` | `claude-sonnet-4-6` | Symptom analysis + emergency detection |
| `check_drug_interaction` | `claude-opus-4-6` | Drug interaction severity + precautions |
| `generate_soap_summary` | `claude-sonnet-4-6` | SOAP note + ICD-10 suggestions |

---

## Prerequisites

- Python 3.13+
- [`uv`](https://docs.astral.sh/uv/) package manager
- Anthropic API key (required — all tools use Claude)

---

## Installation

```bash
# Clone the repository
git clone <repo-url>
cd ai410

# Install dependencies
uv sync
```

---

## Configuration

Set your Anthropic API key before running:

```bash
# macOS / Linux
export ANTHROPIC_API_KEY=sk-ant-...

# Windows PowerShell
$env:ANTHROPIC_API_KEY = "sk-ant-..."

# Windows CMD
set ANTHROPIC_API_KEY=sk-ant-...
```

API keys are read from environment variables at runtime and are never written to disk.

---

## Usage

### CLI mode

```bash
uv run python week6/healthcare_agent/main.py
```

The agent opens an interactive chat loop. Type `quit` or `exit` to stop.

**Example interactions:**

```text
You: I have chest pain and shortness of breath

You: Patient note: 45yo male with hypertension, presents with fatigue and dizziness

You: I'm taking warfarin and aspirin, are there interactions?
```

**SOAP example:**

```text
You: Patient note: 45yo male with hypertension, presents with fatigue and dizziness

🧠 [Planner Node] Analyzing user intent...
   → Task detected: soap

🔧 [Tool Node] Calling external tool...

SOAP Summary
────────────
S (Subjective): 45-year-old male reports fatigue and dizziness
O (Objective):  Hypertension noted; vital signs pending
A (Assessment): Possible hypertensive episode; rule out orthostatic hypotension
P (Plan):       Monitor BP, review medications, follow up in 1 week

🚨 [HITL Node] Human approval required!
   ICD-10 codes suggested:
   • I10 — Essential hypertension
   • R53.83 — Fatigue
   • R42 — Dizziness

⚕️  Clinician: Approve these ICD-10 codes? [y/N]:
```

**Drug interaction example:**

```text
You: I'm taking warfarin and aspirin

Drug Interaction Report
───────────────────────
Drugs checked: warfarin, aspirin
Severity: SEVERE
Interactions: Combined use significantly increases bleeding risk
Precautions: Avoid concurrent use unless directed by a physician; monitor INR closely
```

---

## Streamlit Deployment

The HITL node currently uses `input()` for CLI operation. To deploy as a Streamlit web application, replace the `input()` calls in `hitl_node` (`nodes.py:225–229`) with Streamlit components:

```python
# CLI (current)
approval = input("⚕️  Clinician: Approve these ICD-10 codes? [y/N]: ").strip().lower()

# Streamlit (migration target)
approval = "y" if st.button("Approve ICD-10 codes") else "n"
st.session_state["human_approved"] = (approval == "y")
```

All other nodes are stateless functions — they work without modification in a Streamlit session.

---

## Development

### Install dev dependencies

```bash
uv sync
```

### Run tests

```bash
uv run pytest
```

### Project layout

```
week6/healthcare_agent/
├── state.py      # AgentState TypedDict (shared patient chart)
├── tools.py      # check_symptoms, check_drug_interaction, generate_soap_summary
├── nodes.py      # planner_node, tool_node, evaluator_node, hitl_node
├── graph.py      # LangGraph StateGraph with conditional routing
└── main.py       # CLI chat loop entry point

pyproject.toml    # Project config and dependencies (Python 3.13+)
specs/            # Spec Kit artifacts
tests/            # pytest test suite
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
