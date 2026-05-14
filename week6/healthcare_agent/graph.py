"""
graph.py — Sprint 3 Healthcare Stateful Agent
Builds the LangGraph StateGraph and wires all nodes + conditional routing.
"""

from langgraph.graph import StateGraph, END
from state import AgentState
from nodes import planner_node, tool_node, evaluator_node, hitl_node


# ─────────────────────────────────────────
# Conditional Edge Functions
# ─────────────────────────────────────────

def route_after_evaluator(state: AgentState) -> str:
    """
    After evaluator_node decide next step:
      - retry  → back to tool_node if error and retries remain
      - hitl   → human checkpoint if high-risk or needs approval
      - end    → done
    """
    if state.get("last_error") and state.get("retry_count", 0) < state.get("max_retries", 3):
        return "retry"
    if state.get("needs_human"):
        return "hitl"
    return "end"


def route_after_hitl(state: AgentState) -> str:
    return "end"


# ─────────────────────────────────────────
# Graph Builder
# ─────────────────────────────────────────

def build_graph():
    graph = StateGraph(AgentState)

    graph.add_node("planner", planner_node)
    graph.add_node("tool", tool_node)
    graph.add_node("evaluator", evaluator_node)
    graph.add_node("hitl", hitl_node)

    graph.set_entry_point("planner")
    graph.add_edge("planner", "tool")
    graph.add_edge("tool", "evaluator")

    # Self-correction retry loop + HITL branching
    graph.add_conditional_edges(
        "evaluator",
        route_after_evaluator,
        {
            "retry": "tool",
            "hitl": "hitl",
            "end": END,
        },
    )

    graph.add_conditional_edges(
        "hitl",
        route_after_hitl,
        {"end": END},
    )

    return graph.compile()


healthcare_graph = build_graph()
