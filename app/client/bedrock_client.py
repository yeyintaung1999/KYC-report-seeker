import os

from dotenv import load_dotenv
from langchain_aws import ChatBedrockConverse

load_dotenv()

aws_region = os.getenv("AWS_REGION","ap-northeast-1")
model_id = os.getenv("MODEL_ID", "jp.anthropic.claude-sonnet-4-6")

llm = ChatBedrockConverse(
    model=model_id,
    region_name=aws_region,
    disable_streaming=True
)