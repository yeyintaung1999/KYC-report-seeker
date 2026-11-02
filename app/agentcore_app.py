from bedrock_agentcore.runtime import BedrockAgentCoreApp

from app.main import agent

app = BedrockAgentCoreApp()

@app.entrypoint
def invoke_kyc_agent(payload: dict) -> dict:
    """
    AgentCore entry handler.
    Expects Payload: {"prompt": "...", "session_id": "..."}
    """

    prompt = payload.get("prompt")
    session_id = payload.get("session_id")

    if not prompt:
        return {"error": "Missing Prompt in requested Payload"}

    result = agent.invoke(
        {"messages": [{"role":"user", "content": prompt}]},
        config={"configurable": {"thread_id": session_id}}
    )

    final_content = result["messages"][-1].content

    return {"result": final_content}

if __name__ == "__main__":
    app.run()