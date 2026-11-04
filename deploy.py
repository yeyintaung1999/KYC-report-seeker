import os
import subprocess

import dotenv
from bedrock_agentcore_starter_toolkit import Runtime

dotenv.load_dotenv()

def deploy():
    tavily_key = os.getenv("TAVILY_API_KEY")
    agentcore_runtime = Runtime()

    agentcore_runtime.configure(
        entrypoint="app/agentcore_app.py",
        requirements_file="requirements.txt",
        agent_name="kyc_report_seeker",
        region=os.getenv("AWS_REGION", "ap-northeast-1"),
        auto_create_ecr=True,
        auto_create_execution_role=True
    )

    print("Configuration Initialized. Starting deployment...")


    launch_result = agentcore_runtime.launch(
        auto_update_on_conflict=True
    )

    cmd = [
        "agentcore", "launch",
        "--env", f"TAVILY_API_KEY={tavily_key}"
    ]

    print("Launching AgentCore with environment configuration...")
    result = subprocess.run(cmd, capture_output=False, text=True, check=True)
    if result.returncode != 0:
        raise RuntimeError("Deployment failed during agentcore launch.")

    print(launch_result)
    print("🚀 KYC Report Seeker deployed successfully!")

if __name__ == "__main__":
    deploy()