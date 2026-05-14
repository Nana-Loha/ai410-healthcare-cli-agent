"""
state.py — Sprint 3 Healthcare Stateful Agent
Defines the shared state passed between all LangGraph nodes.
"""

from typing import TypedDict, Optional
from langgraph.graph import add_messages
from langchain_core.messages import BaseMessage
from typing import Annotated


class AgentState(TypedDict):
    """
    Shared state across all nodes in the LangGraph graph.
    Think of this as the 'patient chart' — every node reads and writes here.
    """

    # --- User Input ---
    user_input: str                        # Raw input from user

    # --- Clinical Data ---
    clinical_note: Optional[str]           # Raw clinical note text
    soap_summary: Optional[str]            # Generated SOAP summary
    icd10_codes: Optional[list]            # Suggested ICD-10 codes
    phi_removed_note: Optional[str]        # De-identified clinical note

    # --- Patient Context (Memory across turns) ---
    allergies: list                        # Known allergies
    current_medications: list              # Current medications
    conditions: list                       # Known conditions

    # --- Routing & Control ---
    task_type: Optional[str]               # "soap", "icd10", "drug_check", "symptom"
    risk_level: str                        # "low", "medium", "high"
    needs_human: bool                      # True = HITL checkpoint required
    human_approved: bool                   # True = human approved the output

    # --- Self-Correction ---
    retry_count: int                       # Number of retries so far
    max_retries: int                       # Maximum allowed retries (default: 3)
    last_error: Optional[str]             # Last error message for logging

    # --- Output ---
    final_response: Optional[str]         # Final response to show user

    # --- Conversation History ---
    messages: Annotated[list[BaseMessage], add_messages]  # Full chat history