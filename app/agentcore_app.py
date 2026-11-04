import json
from datetime import UTC, datetime

from bedrock_agentcore.runtime import BedrockAgentCoreApp

from app.main import KYCReport, agent, extract_json

app = BedrockAgentCoreApp()

@app.entrypoint
def handle_kyc_investigation(payload: dict) -> dict:
    """
    Flexible AgentCore Runtime entrypoint.
    Accepts:
    1. Raw entity payload: {"case_id": "...", "company_name": "...", ...}
    2. Prompt wrapper payload: {"prompt": "...", "session_id": "..."}
    """
    if "prompt" in payload:
        prompt = payload.get("prompt")
        session_id = payload.get("session_id", "default-session")
    else:
        case_id = payload.get("case_id", "cust_default")
        session_id = case_id
        prompt = f"""
        Investigate the following compliance target entity:
        {json.dumps(payload, ensure_ascii=False)}

        Return a complete KYC report for this target matching the schema constraints.
        """

    result = agent.invoke(
        {"messages": [{"role": "user", "content": prompt}]},
        config={"configurable": {"thread_id": session_id}}
    )

    raw_message = result["messages"][-1].content
    cleaned_json = extract_json(str(raw_message))

    try:
        data = json.loads(cleaned_json)
        data["completed_at"] = datetime.now(UTC).isoformat()
        data["agent_failed"] = False
        
        validated_report = KYCReport.model_validate(data)
        return validated_report.model_dump()
        
    except Exception as err: # noqa
        return {
            "error": "Validation failed",
            "details": str(err),
            "raw_output": str(raw_message)
        }

if __name__ == "__main__":
    app.run()