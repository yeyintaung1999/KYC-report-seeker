from typing import Annotated, TypedDict

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

from app.schemas import KYCReport


class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    input_payload: dict
    validated_report: KYCReport | None
    start_time_ms: int
    retry_count: int