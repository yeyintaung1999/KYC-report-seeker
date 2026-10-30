import os

from dotenv import load_dotenv
from tavily import TavilyClient

load_dotenv()

api_key=os.getenv("TAVILY_API_KEY", "default tavily api key")

client = TavilyClient(api_key=api_key)