import os

from bedrock_agentcore_starter_toolkit import Runtime


def deploy():
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


    launch_result = agentcore_runtime.launch()
    print(launch_result)
    print("🚀 KYC Report Seeker deployed successfully!")

if __name__ == "__main__":
    deploy()