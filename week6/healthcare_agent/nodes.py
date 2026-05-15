"""
nodes.py — Sprint 3 Healthcare Stateful Agent
Defines all 4 nodes in the LangGraph graph:
  1. Planner Node   — understands user intent
  2. Tool Node      — calls external tools
  3. Evaluator Node — checks output quality + self-correction
  4. HITL Node      — human-in-the-loop checkpoint
"""

import os
import anthropic
from state import AgentState
from tools import check_symptoms, check_drug_interaction, generate_soap_summary

client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))


# ─────────────────────────────────────────
# Node 1 — Planner Node
# ─────────────────────────────────────────

def planner_node(state: AgentState) -> AgentState:
    """
    Understands user intent and decides what to do next.
    Updates: task_type, clinical_note
    """
    print("\n🧠 [Planner Node] Analyzing user intent...")

    user_input = state["user_input"]

    # Detect task type from user input
    user_lower = user_input.lower()

    if any(word in user_lower for word in ["soap", "clinical note", "summarize", "patient"]):
        task_type = "soap"
        clinical_note = user_input
    elif any(word in user_lower for word in ["drug", "medication", "interaction", "taking"]):
        task_type = "drug_check"
        clinical_note = None
    else:
        task_type = "symptom"
        clinical_note = None

    print(f"   → Task detected: {task_type}")

    return {
        **state,
        "task_type": task_type,
        "clinical_note": clinical_note,
        "risk_level": "low",
        "needs_human": False,
        "human_approved": False,
        "retry_count": state.get("retry_count", 0),
        "max_retries": 3,
    }


# ─────────────────────────────────────────
# Node 2 — Tool Node
# ─────────────────────────────────────────

def tool_node(state: AgentState) -> AgentState:
    """
    Calls the appropriate external tool based on task_type.
    Updates: soap_summary, icd10_codes, risk_level, needs_human
    """
    print("\n🔧 [Tool Node] Calling external tool...")

    task_type = state["task_type"]
    user_input = state["user_input"]

    try:
        if task_type == "soap":
            result = generate_soap_summary(state["clinical_note"])
            soap_summary = f"""
SOAP Summary
────────────
S (Subjective): {result.get('subjective', 'N/A')}
O (Objective):  {result.get('objective', 'N/A')}
A (Assessment): {result.get('assessment', 'N/A')}
P (Plan):       {result.get('plan', 'N/A')}
"""
            icd10_codes = result.get("icd10_suggestions", [])
            risk_level = "medium"
            needs_human = True   # Always confirm ICD-10 with human

            print(f"   → SOAP generated. ICD-10 codes: {icd10_codes}")

            return {
                **state,
                "soap_summary": soap_summary,
                "icd10_codes": icd10_codes,
                "risk_level": risk_level,
                "needs_human": needs_human,
                "last_error": None,
            }

        elif task_type == "drug_check":
            # Extract drug names from input
            words = user_input.replace(",", " ").split()
            drugs = [w for w in words if len(w) > 3][:5]  # simple extraction

            result = check_drug_interaction(drugs)
            severity = result.get("severity", "unknown")
            needs_human = result.get("needs_human", False)
            risk_level = "high" if severity == "severe" else "medium" if severity == "moderate" else "low"

            response = f"""
Drug Interaction Report
───────────────────────
Drugs checked: {', '.join(drugs)}
Severity: {severity.upper()}
Interactions: {'; '.join(result.get('interactions', []))}
Precautions: {'; '.join(result.get('precautions', []))}
"""
            print(f"   → Drug check complete. Severity: {severity}")

            return {
                **state,
                "final_response": response,
                "risk_level": risk_level,
                "needs_human": needs_human,
                "last_error": None,
            }

        else:  # symptom check
            result = check_symptoms(user_input)
            risk_level = result.get("risk_level", "low")
            emergency = result.get("emergency", False)
            needs_human = emergency or risk_level == "high"

            response = f"""
Symptom Analysis
────────────────
Possible conditions: {', '.join(result.get('conditions', []))}
Risk level: {risk_level.upper()}
Recommendation: {result.get('recommendation', 'Consult a healthcare provider')}
"""
            if emergency:
                response = "⚠️  EMERGENCY: Call 911 immediately!\n" + response

            print(f"   → Symptom check complete. Risk: {risk_level}")

            return {
                **state,
                "final_response": response,
                "risk_level": risk_level,
                "needs_human": needs_human,
                "last_error": None,
            }

    except Exception as e:
        print(f"   → ❌ Unable to reach AI provider. Retrying...")
        return {
            **state,
            "last_error": str(e),
            "retry_count": state.get("retry_count", 0) + 1,
        }


# ─────────────────────────────────────────
# Node 3 — Evaluator Node (Self-Correction)
# ─────────────────────────────────────────

def evaluator_node(state: AgentState) -> AgentState:
    """
    Checks output quality. Triggers retry if needed.
    This is the self-correction loop required by Sprint 3.
    """
    print("\n✅ [Evaluator Node] Checking output quality...")

    # If there was an error → check retry count
    if state.get("last_error"):
        retry_count = state.get("retry_count", 0)
        max_retries = state.get("max_retries", 3)

        if retry_count < max_retries:
            print(f"   → Retry {retry_count}/{max_retries}: Unable to reach AI provider")
            return {**state, "needs_human": False}
        else:
            print("   → Max retries reached. Escalating to human.")
            return {
                **state,
                "needs_human": True,
                "final_response": f"⚠️ Unable to complete request after {max_retries} attempts. Please consult a healthcare provider directly."
            }

    # Check output quality
    has_soap = state.get("soap_summary") is not None
    has_response = state.get("final_response") is not None

    if not has_soap and not has_response:
        print("   → Output missing. Triggering retry...")
        return {
            **state,
            "last_error": "No output generated",
            "retry_count": state.get("retry_count", 0) + 1,
        }

    print("   → Output quality OK ✅")
    return {**state, "last_error": None}


# ─────────────────────────────────────────
# Node 4 — HITL Node (Human-in-the-Loop)
# ─────────────────────────────────────────

def hitl_node(state: AgentState) -> AgentState:
    """
    Pauses execution and waits for human approval.
    NOTE: input() is used for CLI mode.
    When integrating with Streamlit, replace input()
    with st.button() and st.session_state for approval flow.
    """
    print("\n🚨 [HITL Node] Human approval required!")
    print("─" * 50)

    task_type = state.get("task_type")

    if task_type == "soap":
        print("\n📋 ICD-10 codes suggested:")
        for code in state.get("icd10_codes", []):
            print(f"   • {code}")
        print(state.get("soap_summary", ""))
        approval = input("\n⚕️  Clinician: Approve these ICD-10 codes? [y/N]: ").strip().lower()

    else:
        print(state.get("final_response", ""))
        approval = input("\n⚠️  High-risk result detected. Confirm showing to patient? [y/N]: ").strip().lower()

    if approval == "y":
        print("   → ✅ Approved by human.")
        return {
            **state,
            "human_approved": True,
        }
    else:
        print("   → ❌ Rejected by human. Stopping.")
        return {
            **state,
            "human_approved": False,
            "final_response": "⚕️  Output was not approved. Please consult a healthcare provider directly."
        }