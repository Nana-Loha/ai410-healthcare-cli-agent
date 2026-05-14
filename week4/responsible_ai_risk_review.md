# Lab 4.4 Responsible AI Risk Review

| Risk | Description | Mitigation |
| :--- | :--- | :--- |
| Hallucination and Clinical Inaccuracy | The model may generate inaccurate, incomplete, or misleading medical information, including false drug interactions or incorrect symptom interpretations. | Require human review for high-risk outputs, include uncertainty language, cite sources (FR-006), and enforce confirmation workflows for severe interactions (FR-005). |
| Privacy and API Transmission Risk | Medical records may contain sensitive patient information (PHI). Even without local storage, external AI providers may still receive patient data during API calls. | Enforce FR-004 no-data-storage policy, process data in-memory where possible, disable sensitive logging, redact identifiers before processing, and use zero-retention provider configurations when external APIs are required. |
| Over-Refusal | The model may refuse clinically appropriate requests due to overly conservative safety policies, blocking valid workflows. | Add fallback escalation to an alternative model or human reviewer; log refusals for analysis; clarify clinical context in system prompts. |
| Unsafe Output with Excessive Confidence | The model may provide harmful recommendations (e.g., dangerous drug interactions) with high apparent confidence and no uncertainty markers. | Enforce uncertainty language for high-risk outputs (FR-006), require human-in-the-loop review for severe interactions (FR-005), and apply structured guardrails for safety-critical responses. |
| Overreliance on AI / Automation Bias | Users may trust AI-generated recommendations without sufficient verification because responses appear confident and authoritative. | Clearly state that the system provides decision support only (FR-003 disclaimer), require confirmation for severe findings, and maintain human clinical accountability for final decisions. |
| Demographic and Dataset Bias | Model performance may vary across demographic groups, uncommon conditions, or underrepresented populations. | Evaluate models on diverse benchmark scenarios, document limitations clearly, and escalate uncertain or out-of-distribution cases to human review. |

## Summary

Medical AI systems introduce significant responsible AI challenges, particularly around hallucination, privacy, automation bias, and unsafe recommendations. Strong reasoning capability alone does not guarantee safe deployment behavior — responsible AI safeguards must be applied independently of model performance scores.

To reduce these risks, the system should enforce:
- human oversight
- no-data-storage safeguards
- responsible AI disclaimers
- validation workflows
- fallback escalation procedures

These mitigations improve trustworthiness and align the system with responsible AI deployment principles for healthcare-oriented AI systems.