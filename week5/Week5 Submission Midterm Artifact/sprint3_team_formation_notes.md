# Sprint 3 Team Formation and Kickoff

## Team Roster

| Role | Assigned To |
|---|---|
| Engineering Lead | Pitchanan Lohavanichbutr |
| Data / Retrieval Lead | TBD |
| Evaluation / Safety Lead | TBD |
| Integration Lead | TBD |

> **Note:** Team formation is still in process. Sprint 3 scope builds directly on
> the Healthcare AI Agent developed across Weeks 1–4 and the
> [Clinical SOAP Summarization with ICD-10 RAG](https://github.com/Nana-Loha/ai400-clinical-soap-nlp)
> application, including the Claude Code skills and hooks established in Week 2.

---

## Project Concept Statement

Our project is a stateful, LangGraph-orchestrated Healthcare AI web application that
assists clinical staff with SOAP-structured medical note summarization, ICD-10 code
suggestion via RAG, symptom checking, and drug interaction analysis — powered by a
user-selected AI provider (Claude, GPT-4, or Gemini). Sprint 3 elevates the existing
agent into a ReAct-loop workflow with explicit node transitions, self-correction on
tool failures, and human-in-the-loop checkpoints at high-impact medical decision
boundaries (e.g., severe drug interaction confirmation, emergency symptom detection).
The goal is to reduce documentation burden for doctors while maintaining strict patient
data privacy, Zero Data Retention API usage, and responsible AI safeguards. The final
deliverable targets a deployable web application built on Streamlit.

---

## Sprint 3 Connection to Prior Artifacts

All prior artifacts from Weeks 1–4 and the Clinical SOAP Summarization with ICD-10 RAG application serve as the Sprint 3 foundation:

| Prior Artifact | Sprint 3 Use |
|---|---|
| [Clinical SOAP Summarization with ICD-10 RAG](https://github.com/Nana-Loha/ai400-clinical-soap-nlp) | De-identification, SOAP summarization, ICD-10 RAG — integrated as core nodes |
| SPEC.md (root) | Frozen requirements baseline — functional requirements FR-001 to FR-012 |
| CLAUDE.md | Agent behavior guidelines and development conventions |
| `.claude/skills/` | Reusable Claude Code skills built in Week 2, active across all Sprint 3 work |
| `.claude/hooks/` | Pre-commit / pre-push validation hooks from Week 2 |
| `.specify/` | Spec Kit artifacts (spec, plan, tasks, data-model) |
| MCP config (`.vscode/`) | MCP filesystem server connected in Week 2, used for Sprint 3 tool calls |

---

## Initial Data / Source Inventory

### Medical Knowledge
- AI provider knowledge base (Claude, GPT-4, Gemini) — primary source for all queries
- Medical disclaimer injected on every response (FR-003)
- [Clinical SOAP Summarization with ICD-10 RAG](https://github.com/Nana-Loha/ai400-clinical-soap-nlp) — de-identification, SOAP format, ICD-10 RAG

### User Input Channels
- Web UI text input — free-form symptom description
- Web UI file upload — plain-text medical records
- Web UI form input — drug names for interaction checking
- Chat interface — conversational input for symptom queries

### AI Provider APIs
- Anthropic Claude (`ANTHROPIC_API_KEY`)
- OpenAI GPT-4 (`OPENAI_API_KEY`)
- Google Gemini (`GOOGLE_API_KEY`)

### MCP Integrations (Week 2 setup)
- MCP Filesystem Server — read/write local files for record input and session logs
- Potential extension: MCP for external medical reference lookup (Phase 2)

### Configuration Storage
- `~/.config/healthcare-agent/config.toml` — provider preference only, no patient data

---

## SPEC.md Draft Skeleton (Sprint 3 Extension)

```markdown
# SPEC.md — Sprint 3 Extension: LangGraph Orchestration

## Problem Statement
Doctors spend an estimated 2 hours on documentation for every 1 hour of patient care.
This project integrates the Clinical SOAP Summarization with ICD-10 RAG application with a stateful LangGraph
agent to automate SOAP summarization, ICD-10 code suggestion, drug interaction checking,
and symptom analysis — reducing documentation burden while keeping the doctor in control
via HITL checkpoints.

## User Stories (Sprint 3 additions)
- US-5: As a doctor, I want the agent to self-correct when a provider
        fails, so I always receive a response without manual retry.
- US-6: As a doctor, I want the agent to pause and ask me to confirm
        before displaying emergency or severe interaction information.
- US-7: As a developer, I want observable node transitions so I can
        debug agent reasoning paths.
- US-8: As a doctor, I want my notes de-identified and summarized in
        SOAP format with ICD-10 suggestions automatically.

## Functional Requirements (additions)
- FR-013: Agent MUST use LangGraph state machine for all query routing.
- FR-014: ReAct loop MUST retry on provider failure (max 2 retries,
          fallback to next configured provider).
- FR-015: HITL checkpoint MUST interrupt graph execution at emergency
          symptom and severe drug interaction nodes.
- FR-016: All node transitions MUST be logged for observability.

## Non-Functional Requirements
- Latency: response within 30s under normal network conditions (SC-001)
- Reliability: 0 unhandled exceptions across 100 test runs
- Privacy: no patient data persisted between sessions (FR-004)
- FR-017: System MUST call AI provider APIs via Zero Data Retention (ZDR)
          endpoints to prevent PII/PHI leakage through provider prompt logs.

## Human-in-the-Loop Design
- Checkpoint 1: Emergency symptom detected → pause → user confirms → display
- Checkpoint 2: Severe drug interaction → pause → user confirms → display
- Checkpoint 3: All provider retries exhausted → pause → suggest manual action
- HITL checkpoints must be minimal and purposeful to avoid Click Fatigue —
  triggered only on genuine high-risk boundaries, not routine interactions.
- Medical record summarization outputs structured in SOAP format
  (Subjective, Objective, Assessment, Plan) to reduce hallucination risk.

## Regulatory Awareness
- FTC Health Breach Notification Rule (HBNR) applies to consumer health apps
  even when not a HIPAA Covered Entity.
- All AI provider API usage must be reviewed for data retention policies
  before production deployment.

## Evaluation Criteria
- Directional accuracy of symptom conditions (qualitative review)
- Retry success rate (target: recover from 90% of single-provider failures)
  with root cause analysis per failure type (rate limit / timeout / content filter)
- HITL trigger accuracy (no false negatives on emergency symptoms;
  monitor false positive rate to prevent Click Fatigue)
- Latency p50 / p95 across 50 test runs
- 100% disclaimer coverage (automated output scan)
- Zero PII/PHI appearing in provider API logs (verified via ZDR audit)

## Out of Scope (Sprint 3)
- Mobile native app
- PDF / DOCX record parsing
- Persistent patient data storage
- Multi-user sessions
```

---

## Planning Questions

### What real user problem are you solving?
Doctors spend an estimated 2 hours on documentation for every 1 hour of direct patient
care, leading to burnout and reduced care quality. This project provides an AI-assisted
web application for clinical staff — automating SOAP summarization, ICD-10 code
suggestion, drug interaction checking, and symptom analysis — with mandatory human
confirmation before displaying high-risk medical information. It combines the [Clinical SOAP Summarization with ICD-10 RAG](https://github.com/Nana-Loha/ai400-clinical-soap-nlp) application with a LangGraph agentic workflow and responsible AI safeguards.

### What external tools or MCP integrations will likely be required?
- AI provider APIs: Anthropic Claude, OpenAI GPT-4, Google Gemini
  (via Zero Data Retention endpoints to prevent PHI leakage)
- MCP Filesystem Server (configured in Week 2) — for reading local medical record files
- LangGraph — stateful orchestration and conditional routing
- Potential future: MCP-backed medical reference API for citation enrichment

### Where will your human-in-the-loop checkpoints exist?
1. **Emergency symptom detection** — agent pauses before displaying life-threatening
   condition warnings; user must confirm to proceed.
2. **Severe drug interaction** — agent pauses before displaying HIGH-severity
   interaction reports; user must confirm to proceed.
3. **All-provider failure** — agent pauses and surfaces a manual action prompt
   when all retry attempts are exhausted.

> HITL checkpoints are designed to be minimal and purposeful — triggered only at
> genuine high-risk boundaries to avoid Click Fatigue (users ignoring prompts).

### How will you evaluate retrieval / reasoning quality?
- **Disclaimer coverage**: automated scan — 100% of responses must include the
  medical disclaimer (SC-003).
- **HITL trigger accuracy**: manual review of 20 emergency and severe-interaction
  test cases — zero false negatives acceptable; false positive rate monitored
  to prevent Click Fatigue.
- **Retry recovery rate**: inject provider failures in test harness by failure type
  (rate limit / timeout / content filter); target >= 90% recovery within 2 retries.
- **Latency**: measure p50 and p95 over 50 runs; target p50 < 30s (SC-001).
- **Observability**: verify node transition logs are emitted for every query path.
- **Privacy audit**: confirm zero PII/PHI appears in provider API logs via ZDR
  endpoint verification.