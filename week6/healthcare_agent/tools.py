"""
tools.py — Sprint 3 Healthcare Stateful Agent
External tools called by the Tool Node.
2 tools required by Sprint 3 syllabus:
  1. check_symptoms  — symptom analysis
  2. check_drug_interaction — drug interaction checker (from Sprint 1)
"""

import os
import anthropic

client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

# ─────────────────────────────────────────
# Tool 1 — Symptom Checker
# ─────────────────────────────────────────

def check_symptoms(symptoms: str) -> dict:
    """
    Analyze symptoms and return possible conditions + risk level.
    External tool #1 (Sprint 3 requirement).
    """
    prompt = f"""You are a clinical assistant. Analyze these symptoms: {symptoms}

Return a JSON with:
- conditions: list of possible conditions (max 3)
- risk_level: "low", "medium", or "high"
- recommendation: what the patient should do
- emergency: true if life-threatening symptoms detected

Respond ONLY with valid JSON. No extra text."""

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=500,
        messages=[{"role": "user", "content": prompt}]
    )

    import json
    try:
        result = json.loads(response.content[0].text)
    except Exception:
        result = {
            "conditions": ["Unable to analyze"],
            "risk_level": "medium",
            "recommendation": "Please consult a healthcare provider.",
            "emergency": False
        }

    return result


# ─────────────────────────────────────────
# Tool 2 — Drug Interaction Checker
# (ported from Sprint 1 interactions logic)
# ─────────────────────────────────────────

def check_drug_interaction(drugs: list) -> dict:
    """
    Check drug interactions for a list of drugs.
    External tool #2 (Sprint 3 requirement).
    Ported from Sprint 1 Healthcare CLI Agent.
    """
    if len(drugs) < 2:
        return {
            "severity": "none",
            "interactions": [],
            "precautions": [],
            "needs_human": False
        }

    drugs_str = ", ".join(drugs)
    prompt = f"""You are a clinical pharmacist. Check interactions between: {drugs_str}

Return a JSON with:
- severity: "none", "mild", "moderate", or "severe"
- interactions: list of interaction descriptions
- precautions: list of precautions to take
- needs_human: true if severity is severe (requires human review)

Respond ONLY with valid JSON. No extra text."""

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=500,
        messages=[{"role": "user", "content": prompt}]
    )

    import json
    try:
        result = json.loads(response.content[0].text)
    except Exception:
        result = {
            "severity": "unknown",
            "interactions": ["Unable to check interactions"],
            "precautions": ["Please consult a pharmacist"],
            "needs_human": True
        }

    return result


# ─────────────────────────────────────────
# Tool 3 — SOAP Summarizer
# (from ai400-clinical-soap-nlp pipeline)
# ─────────────────────────────────────────

def generate_soap_summary(clinical_note: str) -> dict:
    """
    Generate SOAP summary from clinical note.
    Connects to ai400-clinical-soap-nlp pipeline.
    """
    prompt = f"""You are a clinical documentation specialist.
Generate a structured SOAP note from this clinical note:

{clinical_note}

Return a JSON with:
- subjective: patient's complaints and history
- objective: vital signs and examination findings
- assessment: diagnosis or differential diagnosis
- plan: treatment plan and follow-up
- icd10_suggestions: list of top 3 ICD-10 codes with descriptions

Respond ONLY with valid JSON. No extra text."""

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1000,
        messages=[{"role": "user", "content": prompt}]
    )

    import json
    try:
        result = json.loads(response.content[0].text)
    except Exception:
        result = {
            "subjective": "Unable to parse",
            "objective": "Unable to parse",
            "assessment": "Unable to parse",
            "plan": "Please consult a healthcare provider",
            "icd10_suggestions": []
        }

    return result