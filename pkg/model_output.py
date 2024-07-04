import os
from openai import OpenAI

DS_API_KEY = "sk-0e8f868835e34335bdb9c6bbd10eedf8"

client = OpenAI(api_key=DS_API_KEY, base_url="https://api.deepseek.com")

response = client.chat.completions.create(
    model="deepseek-chat",
    messages=[
        {"role": "system", "content": "You are a helpful assistant"},
        {"role": "user", "content": "Hello"},
    ],
    stream=False,
)

print(response.choices[0].message.content)
