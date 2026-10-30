import os

from dotenv import load_dotenv
from langchain_aws import ChatBedrockConverse

load_dotenv()

aws_region = os.getenv("AWS_REGION","default region name")
model_id = os.getenv("MODEL_ID", "default model id")

llm = ChatBedrockConverse(
    model=model_id,
    region_name=aws_region
)