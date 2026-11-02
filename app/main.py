import json
import time
from datetime import UTC, datetime
from uuid import uuid4

from .deepagent.deep_agent import agent, extract_json
from .schemas import KYCReport

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



# import json
# import time
# from uuid import uuid4

# from langchain_core.messages import HumanMessage, SystemMessage
# from langchain_core.runnables import RunnableConfig

# from .langgraph_agent.prompt import SYSTEM_PROMPT
# from .langgraph_agent.routing import app
# from .langgraph_agent.state import AgentState

# input_payload = {
#   "case_id": "cust_coremobile_001",
#   "name": "山川 壽史",
#   "company_name": "株式会社コアモバイル",
#   "company_address": "東京都台東区雷門2丁目17番2号 NEWNO浅草5階"
# }

# def main():
#     start_time_ms = int(time.time() * 1000)

#     initial_prompt = f"""
#     Investigate the following compliance target entity:
#     {json.dumps(input_payload, ensure_ascii=False)}

#     Return a complete KYC report for this target matching the schema constraints.
#     """

#     initial_state: AgentState = {
#         "messages": [
#             SystemMessage(content=SYSTEM_PROMPT),
#             HumanMessage(content=initial_prompt),
#         ],
#         "input_payload": input_payload,
#         "validated_report": None,
#         "start_time_ms": start_time_ms,
#         "retry_count": 0,
#     }

#     config: RunnableConfig = {
#         "configurable": {
#             "thread_id": str(uuid4())
#         }
#     }

#     print("Running LangGraph KYC Investigation Workflow via AWS Bedrock...")
#     final_state = app.invoke(initial_state, config=config)

#     report = final_state.get("validated_report")

#     if report:
#         print("\n================ SUCCESSFUL KYC REPORT ================")
#         print(f"Case ID:        {report.case_id}")
#         print(f"Target Name:    {report.name}")
#         print(f"Company:        {report.company_name}")
#         print(f"Risk Score:     {report.report.score}%")
#         print(f"Summary:        {report.report.summary}")
#         print(f"Adverse Sources Count: {len(report.report.sources)}")
#         print(f"Duration:       {report.duration_ms} ms")
#         print("========================================================\n")
#         print("Raw JSON Output:")
#         print(report.model_dump_json(indent=2))
#         return report
#     else:
#         print("\nWorkflow failed to produce a valid report.")
#         return None


# if __name__ == "__main__":
#     main()