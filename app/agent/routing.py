from typing import Literal

from langchain_core.messages import AIMessage
from langgraph.graph import END, START, StateGraph

from ..agent.state import AgentState
from .nodes import agent_node, tool_node, validate_node


def should_continue(state: AgentState) -> Literal["tools", "validate"]:
    last_message = state["messages"][-1]
    
    if isinstance(last_message, AIMessage) and last_message.tool_calls:
        return "tools"
    return "validate"


def check_validation_result(state: AgentState) -> Literal["end", "agent"]:
    """If Pydantic validation passes, terminate graph. Otherwise, loop back to agent with error feedback."""
    if state.get("validated_report") is not None:
        return "end"
    if state.get("retry_count", 0) >= 10:
        print("Max validation retries reached.")
        return "end"
    return "agent"


workflow = StateGraph(AgentState)

workflow.add_node("agent", agent_node)
workflow.add_node("tools", tool_node)
workflow.add_node("validate", validate_node)

workflow.add_edge(START, "agent")

workflow.add_conditional_edges(
    "agent",
    should_continue,
    {
        "tools": "tools",
        "validate": "validate",
    },
)

workflow.add_edge("tools", "agent")

workflow.add_conditional_edges(
    "validate",
    check_validation_result,
    {
        "end": END,
        "agent": "agent",
    },
)

app = workflow.compile()