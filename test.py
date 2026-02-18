from openai import OpenAI

NOVA_API_KEY = "b789d453-7af6-4667-9298-e8488ddcebc7"

client = OpenAI(api_key=NOVA_API_KEY, base_url="https://api.nova.amazon.com/v1")

response = client.chat.completions.create(
    model="nova-2-lite-v1",
    messages=[
        {"role": "system", "content": "You are a helpful assistant"},
        {
            "role": "user",
            "content": "Hello! What can you for me today?",
        },
    ],
    stream=False,
)

print(response.choices[0].message.content)
