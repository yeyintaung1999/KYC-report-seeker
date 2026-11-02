import json
import re
import time
from datetime import UTC, datetime
from uuid import uuid4

import dotenv
from deepagents import create_deep_agent
from langchain_core.tools import tool

from ..client.bedrock_client import llm as model
from ..client.tavily_client import client as tavily
from ..langgraph_agent.prompt import SYSTEM_PROMPT
from ..schemas import KYCReport

dotenv.load_dotenv()

system_prompt = SYSTEM_PROMPT

def extract_json(raw_text: str) -> str:
    """Extracts the innermost/outermost raw JSON block from LLM output, ignoring preambles/conversational text."""
    text = raw_text.strip()
    
    if "```" in text:
        match = re.search(r"```(?:json)?\s*(\{[\s\S]*\})\s*```", text)
        if match:
            return match.group(1).strip()
            
    start_idx = text.find("{")
    end_idx = text.rfind("}")
    
    if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
        return text[start_idx : end_idx + 1].strip()
        
    return text

@tool
def search_adverse_media(query: str) -> str:
    """Search for adverse media, legal actions, regulatory penalties, data breaches, or operational incidents."""
    try:
        response = tavily.search(query=query, search_depth="advanced", max_results=5)
        results = response.get("results", [])
        clean_results = [
            {"title": r.get("title"), "url": r.get("url"), "content": r.get("content")}
            for r in results
        ]
        return json.dumps(clean_results, ensure_ascii=False)
    except Exception as e: #noqa
        return json.dumps({"error": str(e)})


agent = create_deep_agent(
    model=model,
    tools=[search_adverse_media],
    system_prompt=system_prompt,
)


input_payload = {
    "case_id": "cust_coremobile_001",
    "name": "Htet Wai Yan",
    "company_name": "株式会社コアモバイル",
    "company_address": "東京都台東区雷門2丁目17番2号 NEWNO浅草5階",
}


def main():
    start_time_ms = int(time.time() * 1000)
    session_id = str(uuid4())

    prompt = f"""
    Investigate the following compliance target entity:
    {json.dumps(input_payload, ensure_ascii=False)}

    Return a complete KYC report for this target matching the schema constraints.
    """

    print(f"Running KYC Report Seeker via Deep Agents (Bedrock backend)... [Session: {session_id}]")
    
    result = agent.invoke(
        {"messages": [{"role": "user", "content": prompt}]},
        config={"configurable": {"thread_id": session_id}}
    )

    duration_ms = int(time.time() * 1000) - start_time_ms
    completed_at = datetime.now(UTC).isoformat()

    final_message = result["messages"][-1].content

    cleaned_json = extract_json(str(final_message))

    try:
        data = json.loads(cleaned_json)
        data["duration_ms"] = duration_ms
        data["completed_at"] = completed_at
        data["agent_failed"] = False

        report_obj = KYCReport.model_validate(data)

        print("\n================ SUCCESSFUL KYC REPORT ================")
        print("Raw JSON Output:")
        print(report_obj.model_dump_json(indent=2))
        return report_obj

    except Exception as err: # noqa
        print(f"\n[Validation Error]: {err}")
        print(f"Raw Output Received:\n{final_message}")
        return None


if __name__ == "__main__":
    main()