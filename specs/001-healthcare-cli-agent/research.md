# Research: Healthcare CLI AI Agent

**Phase**: 0 — Pre-Design Research  
**Date**: 2026-04-20  
**Feature**: specs/001-healthcare-cli-agent/spec.md

---

## Decision 1: CLI Framework

**Decision**: Use `click` as the CLI framework.

**Rationale**: `click` is the de-facto standard for Python CLIs with complex subcommands. It provides built-in support for flags, prompts (required for confirmation gates), file arguments, and help text generation. It integrates cleanly with `uv` managed projects. Typer (Click wrapper) adds type-annotation ergonomics but introduces an additional dependency layer without meaningful gain here.

**Alternatives considered**:
- `argparse` (stdlib) — verbose for subcommand trees; no built-in prompt utilities
- `typer` — wraps Click; acceptable but unnecessary indirection for this scope

---

## Decision 2: Multi-Provider AI Abstraction

**Decision**: Implement a thin `ProviderAdapter` protocol (structural subtyping) with one concrete class per provider. A `ProviderFactory` maps provider names to adapter instances at session start.

**Rationale**: LangGraph supports multiple model backends but adds graph-based orchestration overhead that is unnecessary for single-turn, single-provider queries. A simple adapter pattern keeps the abstraction testable, swappable per command, and avoids LangGraph's state-machine complexity for straightforward request/response flows. LangGraph should be reserved for multi-step workflows (e.g., the clarifying follow-up loop in symptom checking).

**Alternatives considered**:
- Direct SDK calls inline per provider — no abstraction, untestable
- LangChain provider wrappers — heavy dependency, rapid API churn
- LangGraph for all flows — appropriate for multi-hop agent loops, overkill for single-turn queries

---

## Decision 3: LangGraph Usage Scope

**Decision**: Use LangGraph only for the symptom-checker follow-up clarification loop (US1, Acceptance Scenario 2). All other flows are single-turn and use the adapter directly.

**Rationale**: The spec requires the agent to ask a follow-up clarifying question when input is ambiguous. This is a 2-node graph (initial analysis → clarification gate → final answer). LangGraph is well-suited for this bounded loop. Extending it to summarization or drug interaction (which are single-turn) would add unnecessary complexity.

**Alternatives considered**:
- Manual loop with while/input — feasible but not idiomatic for state-machine flows
- Full LangGraph for all features — over-engineered; state persistence would risk data leakage

---

## Decision 4: Document Chunking for Medical Records

**Decision**: Use LlamaIndex `SimpleNodeParser` with sentence-window splitting for medical record summarization. Merge chunk summaries with a reduce step using the same provider adapter.

**Rationale**: LlamaIndex is already a declared dependency. `SimpleNodeParser` handles plain-text chunking without requiring a vector store or index (which would persist data — violating FR-004). The map-reduce summary pattern is well-established for long documents and keeps all processing in-memory within the session.

**Alternatives considered**:
- Manual character-count chunking — fragile on sentence boundaries, loses context
- LlamaIndex with vector index — persists embeddings to disk, violates no-storage constraint
- Single prompt with full record — fails for records exceeding context window

---

## Decision 5: Configuration File Format and Location

**Decision**: Store provider configuration in `~/.config/healthcare-agent/config.toml`. File contains only provider name (no API keys or patient data). API keys are read exclusively from environment variables at runtime.

**Rationale**: TOML is human-readable and has first-class support in Python 3.11+ (`tomllib`). Storing the config in `~/.config/` follows XDG Base Directory conventions and is predictable across platforms. Keeping API keys out of the config file satisfies FR-004 (no patient data) and avoids accidental credential exposure.

**Alternatives considered**:
- `.env` file — conflicts with API key env vars, harder to parse for non-key config
- JSON config — less readable for end-users editing manually
- In-project config — makes the tool non-portable across different working directories

---

## Decision 6: Emergency Condition Detection

**Decision**: Implement a keyword/phrase classifier prompt step that runs before the full symptom analysis. If the classifier returns `emergency=true`, the agent prints the emergency prompt (standardised text + `911` / local emergency number placeholder) before any other output.

**Rationale**: Delegating emergency detection to the AI provider via a structured classification call is more reliable than hardcoded keyword lists. The two-step approach (classify then analyse) adds minimal latency (~1–2s) and ensures the emergency prompt always precedes the full response. The classifier prompt is a separate, short call that returns JSON.

**Alternatives considered**:
- Keyword list in code — brittle, misses paraphrases, language-dependent
- Post-process full response for emergency keywords — too late; full response is already displayed
- Single combined prompt with emergency flag — harder to guarantee flag position in streamed output

---

## Decision 7: Confirmation Prompt Strategy

**Decision**: Use `click.confirm()` for all critical-action gates (FR-005). Critical actions are: (a) severe drug interaction display, (b) first API call per session. The session tracks `first_call_confirmed` in memory to avoid repeated prompts within a session.

**Rationale**: `click.confirm()` is idiomatic, tested, and works correctly in both interactive terminals and piped input (raises `Abort` on non-interactive stdin, allowing graceful exit). Session-level tracking via a simple in-memory flag avoids re-prompting on every call without persisting state.

**Alternatives considered**:
- Custom input() prompts — requires reimplementing abort/non-interactive handling
- Prompt every API call — poor UX; users confirmed once per session is sufficient
- No first-call confirmation — removes an important disclosure moment for first-time users

---

## Decision 8: No-Storage Guarantee Mechanism

**Decision**: All patient data (symptoms, record text, drug lists) is passed as function arguments through the call stack and never assigned to module-level variables, written to files, or included in log messages. Logging is configured at `WARNING` level by default, and the log format excludes message payloads for healthcare commands.

**Rationale**: Python's structured logging allows filtering sensitive fields. By design, input data never touches the logging system. Enforcing this via code review checklist and a test that asserts log output contains no patient fixture data provides a verifiable guarantee for SC-004.

**Alternatives considered**:
- Runtime data-scrubbing of logs — complex, error-prone, still risks intermediate writes
- Encrypted temporary files — unnecessary complexity; in-memory is simpler and safer
