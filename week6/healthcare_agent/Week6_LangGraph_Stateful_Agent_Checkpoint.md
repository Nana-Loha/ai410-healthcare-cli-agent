# Week 6 — LangGraph Stateful Agent Checkpoint Submission

**Student:** Pitchanan Lohavanichbutr  
**Course:** AI410 Spring 2026 | Bellevue College  
**Repository:** https://github.com/Nana-Loha/ai410  
**Sprint:** Sprint 3 — Healthcare AI Agent

---

## Artifact 1 — State Graph Implementation

The Sprint 3 Healthcare AI Agent implements a 4-node stateful LangGraph workflow with conditional routing and self-correction loops. The graph is defined in `graph.py` and orchestrates all clinical query processing.

### Node Summary

| Node | Role |
|---|---|
| `planner_node` | Classifies user intent into `soap` / `drug_check` / `symptom` using keyword detection. Initializes all state fields. |
| `tool_node` | Calls the appropriate clinical tool. Uses Claude Sonnet 4.6 for SOAP and symptom tasks; Claude Opus 4.6 for safety-critical drug interaction analysis. |
| `evaluator_node` | Validates output quality. Triggers retry loop (max 3 attempts) on failure. Escalates to HITL when retries are exhausted. |
| `hitl_node` | Pauses graph execution and requires human confirmation before displaying high-risk medical output. Suppresses output if rejected. |

### Conditional Routing Logic

After the evaluator node, routing is decided by `route_after_evaluator`:

- `retry` → `tool_node`: if `last_error` exists and `retry_count < max_retries` (3)
- `hitl` → `hitl_node`: if `needs_human` flag is True
- `end` → `END`: if output quality is confirmed and no human review required

### Graph Flow

```
[START]
    ↓
[planner_node]   — classify intent
    ↓
[tool_node]  ←──────────────────────┐
    ↓                               │ retry (retry_count < 3)
[evaluator_node] ───────────────────┘
    │
    ├── needs_human = True → [hitl_node] → [END]
    │
    └── needs_human = False → [END]
```

---

## Artifact 2 — Architecture Write-up

### State Schema (AgentState)

| Field | Type | Purpose |
|---|---|---|
| `user_input` | str | Raw user query |
| `task_type` | str | Classified intent: soap / drug_check / symptom |
| `clinical_note` | str | Extracted note for SOAP tasks |
| `soap_summary` | str | Formatted SOAP output |
| `icd10_codes` | list | ICD-10 code suggestions |
| `final_response` | str | Drug check or symptom output |
| `risk_level` | str | low / medium / high |
| `needs_human` | bool | Trigger HITL checkpoint |
| `human_approved` | bool | Human decision result |
| `last_error` | str | Last tool error message |
| `retry_count` | int | Current retry attempt |
| `max_retries` | int | Maximum retries allowed (3) |

### HITL Design Decisions

HITL checkpoints are triggered at three boundaries:

1. **Emergency symptom detection** — HITL requires confirmation before returning the emergency result as the final agent response.
2. **Severe drug interaction** — HITL requires confirmation before returning the HIGH-severity interaction report as the final agent response.
3. **All-provider failure** — agent pauses when all retry attempts are exhausted.

HITL is not triggered on every output to avoid **Click Fatigue** — users ignoring prompts without reading them. Checkpoints are reserved exclusively for genuine high-risk boundaries where clinician review is medically necessary.

### Model Allocation (Per Week 3 Research)

| Task | Model | Rationale |
|---|---|---|
| Symptom checking | Claude Sonnet 4.6 | Balanced speed and reasoning |
| SOAP summarization | Claude Sonnet 4.6 | Structured output, cost-efficient |
| Drug interactions | Claude Opus 4.6 | Safety-critical — highest reasoning capability |
| Provider fallback | GPT-5.4 | Vendor diversity (FR-002, FR-012) |

---

## Artifact 3 — Self-Correction Loop Evidence

The self-correction loop is implemented in `evaluator_node`. When a tool call fails, the evaluator checks the retry count against `max_retries` (3). If retries remain, execution returns to `tool_node`. After 3 failures, the error is escalated to the HITL node for human review.

### Figure 1 — Self-correction retry loop (3 retries with invalid API key)

![Self-correction retry loop](screenshots/Screenshot%202026-05-14%20224112.png)

*Figure 1: Tool node fails 3 times → Evaluator node triggers retry → Max retries reached → Escalates to HITL*

### Figure 2 — HITL escalation after retry exhaustion

![HITL escalation after max retries](screenshots/Screenshot%202026-05-14%20224151.png)

*Figure 2: After 3 failed attempts, HITL node displays user-friendly error and requests human confirmation*

---

## Artifact 4 — Human-in-the-Loop Checkpoint Evidence

### 4A — Emergency Symptom Detection

Input: `"I have severe chest pain and shortness of breath"`

The planner routes to symptom check. The tool returns `risk_level=high` and `emergency=true`. The evaluator passes output to the HITL node, which requires clinician confirmation before returning the emergency result as the final agent response.

### Figure 3 — Symptom check triggering HITL (emergency detected)

![Symptom check with HITL triggered](screenshots/Screenshot%202026-05-14%20221310.png)

*Figure 3: Planner → Tool (Risk: HIGH) → Evaluator (OK) → HITL (Human approval required)*

### Figure 4 — HITL approval and final output

![HITL approved and symptom analysis displayed](screenshots/Screenshot%202026-05-14%20221837.png)

*Figure 4: Clinician approves → Agent displays emergency symptom analysis with medical disclaimer*

---

### 4B — Severe Drug Interaction Detection

Input: `"I'm taking warfarin and aspirin"`

The planner routes to `drug_check`. Claude Opus 4.6 returns `severity=severe` and `needs_human=True`. The HITL node requires clinician confirmation before returning the severe interaction report as the final agent response.

### Figure 5 — Drug interaction check triggering HITL (severity: SEVERE)

![Drug interaction check with HITL triggered](screenshots/Screenshot%202026-05-14%20222025.png)

*Figure 5: Planner → Tool (Severity: SEVERE, Claude Opus 4.6) → Evaluator (OK) → HITL*

### Figure 6 — Drug interaction approved and full report displayed

![Drug interaction approved](screenshots/Screenshot%202026-05-14%20222133.png)

*Figure 6: Clinician approves → Agent displays complete drug interaction report with precautions*

---

## References

- Yao et al. (2022). ReAct: Synergizing Reasoning and Acting in Language Models. arXiv:2210.03629.
- LangGraph Documentation. LangChain Inc., 2026. https://docs.langchain.com/oss/python/langgraph/overview
- AI410 Week 3 Model Workflow Comparison Memo. Pitchanan Lohavanichbutr, 2026.
- AI410 Week 6 CLAUDE.md and SPEC.md. Pitchanan Lohavanichbutr, 2026.