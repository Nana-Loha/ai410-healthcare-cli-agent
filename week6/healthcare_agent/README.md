# Healthcare AI Agent — Sprint 3

A LangGraph-powered CLI agent for healthcare tasks: symptom checking, SOAP note generation, and drug interaction analysis.

> ⚕️ **Not a substitute for professional medical advice.**

---

## Features

- **Planner node** — detects intent (symptom / SOAP / drug check)
- **Tool node** — calls Claude-powered clinical tools
- **Evaluator node** — self-correction retry loop (max 3 retries)
- **HITL node** — human-in-the-loop checkpoint for high-risk results
- **State persistence** — patient context (allergies, medications, conditions) carried across turns

---

## Setup

### 1. Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) package manager

### 2. Install dependencies

```bash
uv sync
```

Or install from `pyproject.toml` manually:

```bash
uv add anthropic langgraph langchain-core
```

### 3. Set your API key

```bash
# macOS / Linux
export ANTHROPIC_API_KEY=sk-ant-...

# Windows PowerShell
$env:ANTHROPIC_API_KEY = "sk-ant-..."

# Windows CMD
set ANTHROPIC_API_KEY=sk-ant-...
```

---

## Run

```bash
uv run python main.py
```

---

## Example interactions

```
You: I have chest pain and shortness of breath
You: Patient note: 45yo male with hypertension, presents with fatigue and dizziness
You: I'm taking warfarin and aspirin, are there interactions?
```

---

## Project structure

```
healthcare_agent/
├── state.py      # AgentState TypedDict
├── tools.py      # check_symptoms, check_drug_interaction, generate_soap_summary
├── nodes.py      # planner_node, tool_node, evaluator_node, hitl_node
├── graph.py      # LangGraph StateGraph with conditional routing
└── main.py       # CLI chat loop entry point
```

---

## Graph flow

```
planner → tool → evaluator ──(error + retries left)──→ tool   (retry loop)
                          └──(needs_human)───────────→ hitl → END
                          └──(ok)──────────────────────────→ END
```

---

## Environment variables

| Variable | Required | Description |
|---|---|---|
| `ANTHROPIC_API_KEY` | ✅ | Claude API key from console.anthropic.com |
