import os

from langchain_amazon_nova import ChatAmazonNova

client = ChatAmazonNova(
    model=os.environ["NOVA_MODEL_ID"],
    api_key=os.environ["NOVA_API_KEY"],
    streaming=True,  # Enable streaming responses
)
