from openai import OpenAI
import base64

NOVA_API_KEY = "b789d453-7af6-4667-9298-e8488ddcebc7"

client = OpenAI(api_key=NOVA_API_KEY, base_url="https://api.nova.amazon.com/v1")

# https://codeload.github.com/Mmagdy908/chat-api-genai/zip/refs/heads/main
with open("codebase.txt", "rb") as input_file:
    # Read the file content (bytes)
    file_bytes = input_file.read()
    # Encode the bytes to Base64 bytes
    encoded_bytes = base64.b64encode(file_bytes)

response = client.chat.completions.create(
    model="nova-2-lite-v1",
    messages=[
        {
            "role": "system",
            "content": """

                You are The Architect, an elite software engineering agent. You have been provided with a full codebase in the context.
            
                Your task is to analyze the codebase and provide insights, answer questions, and generate diagrams based on the code. You have access to the entire codebase and can understand its structure, components, and interactions. Use this information to assist users in understanding the codebase and making informed decisions about it.

                You need to provide context if needed with the code file and line number to support your answer. You can also generate diagrams to illustrate the architecture and interactions within the codebase.
            """,
        },
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "Give me an overview about this repo"},
                {
                    "type": "file",
                    "file": {
                        "file_data": encoded_bytes.decode("utf-8"),
                    },
                },
            ],
        },
        # {
        #     "role": "user",
        #     "content": "What are the main components of this codebase and how do they interact with each other?",
        # },
        # {
        #     "role": "user",
        #     "content": "If we scale this system to 1M users, what breaks first?",
        # },
        {
            "role": "user",
            "content": "where in the code is files uploading configured and how can I change the max file size to 100MB?",
        },
        {
            "role": "user",
            "content": "where is the multer configuration object?",
        },
        # {
        #     "role": "user",
        #     "content": "generate me a sequence diagram that shows the interaction between the main components of this codebase when a user makes a request to the system",
        # },
    ],
    extra_body={
        "system_tools": [
            "nova_grounding",
        ]
    },
    stream=False,
)

print(response.choices[0].message.content)
