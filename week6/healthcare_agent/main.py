"""
main.py — Sprint 3 Healthcare Stateful Agent
CLI chat loop. Run with: uv run python main.py
"""

import os
import sys

# Force UTF-8 output so emoji in nodes.py and prompts render on Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from langchain_core.messages import HumanMessage
from graph import healthcare_graph
from state import AgentState


DISCLAIMER = (
    "\n⚕️  Disclaimer: This tool is NOT a substitute for professional medical advice.\n"
    "   Always consult a qualified healthcare provider for medical decisions.\n"
)

BANNER = """\
╔══════════════════════════════════════════════╗
║   Healthcare AI Agent  —  Sprint 3 Demo      ║
║   Type 'quit' or 'exit' to stop              ║
╚══════════════════════════════════════════════╝
"""


def make_initial_state(user_input: str, previous: AgentState | None = None) -> AgentState:
    """Build a fresh AgentState for each turn, carrying over patient context."""
    base: AgentState = {
        # User input
        "user_input": user_input,
        # Clinical data — reset each turn
        "clinical_note": None,
        "soap_summary": None,
        "icd10_codes": [],
        "phi_removed_note": None,
        # Patient context — persisted across turns
        "allergies": previous["allergies"] if previous else [],
        "current_medications": previous["current_medications"] if previous else [],
        "conditions": previous["conditions"] if previous else [],
        # Routing
        "task_type": None,
        "risk_level": "low",
        "needs_human": False,
        "human_approved": False,
        # Self-correction
        "retry_count": 0,
        "max_retries": 3,
        "last_error": None,
        # Output
        "final_response": None,
        # Conversation history — persisted across turns
        "messages": (previous["messages"] if previous else []) + [HumanMessage(content=user_input)],
    }
    return base


def run_chat() -> None:
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("❌  ANTHROPIC_API_KEY is not set. Export it and re-run.")
        sys.exit(1)

    print(BANNER)
    print(DISCLAIMER)
    print("Examples:")
    print("  • I have chest pain and shortness of breath")
    print("  • Patient note: 45yo male with hypertension...")
    print("  • I'm taking warfarin and aspirin\n")

    state: AgentState | None = None

    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n\nGoodbye!")
            break

        if not user_input:
            continue
        if user_input.lower() in {"quit", "exit", "q"}:
            print("Goodbye!")
            break

        state = make_initial_state(user_input, previous=state)

        try:
            result: AgentState = healthcare_graph.invoke(state)
        except Exception as e:
            print(f"\n❌  Agent error: {e}\n")
            continue

        response = result.get("final_response") or result.get("soap_summary") or "No response generated."
        print(f"\nAgent:\n{response}")
        print(DISCLAIMER)

        # Persist updated patient context for next turn
        state = result


if __name__ == "__main__":
    run_chat()
