# Prompt Log — Week 6 (Sprint 3 Build Phase)

**Project:** AI410 Healthcare AI Agent  
**Student:** Pitchanan Lohavanichbutr  
**Date:** May 14, 2026  
**Focus:** LangGraph stateful orchestration, HITL checkpoints, self-correction loops

---

## Session Overview

This log documents key prompts, decisions, and reasoning during the Week 6 Sprint 3 build phase. The session covered LangGraph workflow verification, model selection rationale, tool implementation fixes, and HITL design decisions.

---

## Entry 1 — Model Selection for Drug Interaction Tool

**Prompt intent:** Decide which AI model to use for `check_drug_interaction` tool.

**Decision:** Changed from `claude-sonnet-4-6` to `claude-opus-4-6`

**Reasoning:**  
Per Week 3 model comparison research, Claude Opus 4.6 achieves the highest SWE-bench Verified score (80.8%) and is best suited for safety-critical reasoning tasks. Drug interaction analysis is a high-stakes clinical decision where reasoning quality outweighs latency and cost concerns. Claude Sonnet 4.6 is retained for symptom checking and SOAP summarization where balanced performance is sufficient.

**Code change:**
```python
# check_drug_interaction in tools.py
model="claude-opus-4-6"  # was claude-sonnet-4-6
```

---

## Entry 2 — JSON Parse Fix (_parse_json helper)

**Prompt intent:** Fix "Unable to analyze" fallback appearing despite successful API calls.

**Root cause:** Claude API occasionally wraps JSON responses in markdown code blocks (` ```json ... ``` `), causing `json.loads()` to fail silently and return the fallback dict.

**Decision:** Extracted a shared `_parse_json()` helper that strips markdown fences before parsing.

**Reasoning:**  
Rather than fixing each tool independently (3 separate try/except blocks), a single helper function ensures consistent behavior across all tools and reduces code duplication. The regex `re.sub(r'```json\s*|\s*```', '', text)` safely strips both opening and closing fences.

**Code change:**
```python
def _parse_json(text: str) -> dict:
    text = re.sub(r'```json\s*|\s*```', '', text).strip()
    return json.loads(text)
```

---

## Entry 3 — HITL Checkpoint Design

**Prompt intent:** Design human-in-the-loop checkpoints for the healthcare agent.

**Decision:** HITL is triggered at 3 boundaries only:
1. Emergency symptom detection (`risk_level=high` or `emergency=true`)
2. Severe drug interaction (`severity=severe`)
3. All-provider failure after retry exhaustion

**Reasoning:**  
Research on HITL design (Gemini feedback, Week 5) warns against Click Fatigue — users ignoring confirmation prompts when they appear too frequently. By reserving HITL exclusively for genuine high-risk boundaries, each checkpoint carries real clinical weight and is more likely to receive genuine human attention. Low and medium risk outputs bypass HITL entirely.

**HITL wording correction:** Initial document described HITL as "pausing before displaying" results. Corrected to "requires confirmation before returning the result as the final agent response" to accurately reflect the implementation where the result preview is shown before the confirmation prompt.

---

## Entry 4 — User-Friendly Error Messages

**Prompt intent:** Improve error messages in tool_node and evaluator_node for non-technical users.

**Problem:** Raw API error messages (401 authentication errors with request IDs) were exposed directly to users, which is not appropriate for a clinical tool.

**Decision:** Replace raw error strings with user-friendly messages:
- `❌ Tool error: Error code: 401 - {...}` → `❌ Unable to reach AI provider. Retrying...`
- `Retry 1/3: Error code: 401 - {...}` → `Retry 1/3: Unable to reach AI provider`
- Error escalation message no longer exposes raw exception details

**Reasoning:**  
Healthcare staff using this tool do not need to see API error codes. The user-friendly message communicates the same information (provider unavailable, retrying) without exposing internal implementation details. Technical error details are still stored in `last_error` state for developer debugging.

---

## Entry 5 — Self-Correction Loop Verification

**Prompt intent:** Verify that the retry loop behaves correctly under provider failure.

**Test method:** Set `ANTHROPIC_API_KEY = "invalid-key"` and submitted a symptom query.

**Observed behavior:**
```
🔧 Tool Node → ❌ Unable to reach AI provider. Retrying...
✅ Evaluator → Retry 1/3: Unable to reach AI provider
🔧 Tool Node → ❌ Unable to reach AI provider. Retrying...
✅ Evaluator → Retry 2/3: Unable to reach AI provider
🔧 Tool Node → ❌ Unable to reach AI provider. Retrying...
✅ Evaluator → Max retries reached. Escalating to human.
🚨 HITL Node → Human approval required!
```

**Decision:** Self-correction loop confirmed working. Max retries = 3, escalation to HITL after exhaustion confirmed. No infinite loop behavior observed.

---

## Entry 6 — Architecture Diagram

**Prompt intent:** Create architecture diagram for Week 6 checkpoint submission.

**Decision:** Created SVG-based flowchart showing all 4 nodes, conditional routing paths, and retry loop using the claude.ai Visualizer tool.

**Key design choices documented:**
- Retry loop shown as dashed line returning from evaluator → tool node
- HITL path shown as separate branch with explicit END
- Color coding: purple = planner, teal = tool, amber = evaluator, coral = HITL

---

## Key Technical Decisions Summary

| Decision | Choice | Rationale |
|---|---|---|
| Drug interaction model | Claude Opus 4.6 | Safety-critical — highest reasoning |
| Symptom/SOAP model | Claude Sonnet 4.6 | Balanced performance + cost |
| JSON parsing | `_parse_json()` helper | Handles markdown fences consistently |
| HITL trigger points | 3 boundaries only | Avoid Click Fatigue |
| Error messages | User-friendly strings | Clinical tool — hide technical details |
| Max retries | 3 | Balances reliability vs latency |

---

## References

- ReAct paper (Yao et al., 2022) — foundation for evaluator/retry loop design
- LangGraph documentation — stateful graph API reference
- AI410 Week 3 Model Workflow Comparison Memo — model selection rationale
- Gemini feedback on HITL Click Fatigue — HITL design constraint