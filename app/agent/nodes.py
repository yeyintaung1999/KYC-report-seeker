import json
import time
from datetime import datetime, timezone

from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.tools import tool
from pydantic import ValidationError

from ..agent.state import AgentState
from ..client.bedrock_client import llm
from ..client.tavily_client import client as tavily
from ..schemas import KYCReport


@tool
def search_adverse_media(query: str) -> str:
    """Search for adverse media, legal actions, regulatory penalties, data breaches, or operational incidents."""
    try:
        print(query)
        response = tavily.search(query=query, search_depth="advanced", max_results=5)
        results = response.get("results", [])
        clean_results = [
            {
                "title": r.get("title"),
                "url": r.get("url"),
                "content": r.get("content"),
            }
            for r in results
        ]
        return json.dumps(clean_results, ensure_ascii=False)
    except Exception as e:   # noqa: BLE001
        return json.dumps({"error": str(e)})

tools = [search_adverse_media]
tools_by_name = {t.name: t for t in tools}
tools = [search_adverse_media]
tools_by_name = {t.name: t for t in tools}
llm = llm.bind_tools(tools)

def agent_node(state: AgentState) -> dict:
    """Executes the LLM step."""
    response = llm.invoke(state["messages"])
    return {"messages": [response]}


def tool_node(state: AgentState) -> dict:
    last_message = state["messages"][-1]
    tool_messages = []

    if isinstance(last_message, AIMessage):
        for tool_call in last_message.tool_calls:
            tool_func = tools_by_name[tool_call["name"]]
            observation = tool_func.invoke(tool_call["args"])
            tool_messages.append(
                {
                    "role": "tool",
                    "content": str(observation),
                    "tool_call_id": tool_call["id"],
                }
            )

    return {"messages": tool_messages}


def validate_node(state: AgentState) -> dict:
    """Parses and validates the final LLM response against the Pydantic KYCReport model."""
    last_message = state["messages"][-1].content
    
    cleaned_json = str(last_message).strip()
    if cleaned_json.startswith("```json"):     # noqa: FURB188
        cleaned_json = cleaned_json[7:]
    if cleaned_json.startswith("```"):         # noqa: FURB188
        cleaned_json = cleaned_json[3:]
    if cleaned_json.endswith("```"):           # noqa: FURB188
        cleaned_json = cleaned_json[:-3]
    cleaned_json = cleaned_json.strip()

    duration_ms = int(time.time() * 1000) - state["start_time_ms"]
    completed_at = datetime.now(timezone.utc).isoformat()       # noqa: UP017

    try:
        data = json.loads(cleaned_json)
        data["duration_ms"] = duration_ms
        data["completed_at"] = completed_at
        data["agent_failed"] = False

        report_obj = KYCReport.model_validate(data)
        return {"validated_report": report_obj}

    except (json.JSONDecodeError, ValidationError) as err:
        print(f"[Validation Failed - Retry {state['retry_count'] + 1}]: {err}")
        feedback_msg = HumanMessage(
            content=(
                f"Your output failed JSON/Pydantic validation: {str(err)}.\n"   # noqa: RUF010
                "Please fix the formatting and output ONLY valid raw JSON matching the required schema."
            )
        )
        return {
            "messages": [feedback_msg],
            "retry_count": state["retry_count"] + 1,
        }