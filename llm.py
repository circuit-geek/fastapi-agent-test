from openai import AsyncAzureOpenAI
from dotenv import load_dotenv
import os

load_dotenv()
client = AsyncAzureOpenAI(
    api_key=os.getenv("OPENAI_API_TOKEN"),
    azure_endpoint=os.getenv("ENDPOINT"),
    api_version=os.getenv("OPENAI_API_VERSION"),
)

model = os.getenv("DEPLOYMENT")