import os

from openai import OpenAI

client = OpenAI(
    api_key=os.environ["NOVA_API_KEY"],
    base_url="https://api.nova.amazon.com/v1",
)
