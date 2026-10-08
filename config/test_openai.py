import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

api_key = os.getenv("GROQ_API_KEY") or os.getenv("OPENAI_API_KEY")
base_url = "https://api.groq.com/openai/v1" if os.getenv("GROQ_API_KEY") else None

client = OpenAI(
    api_key=api_key,
    base_url=base_url
)

model = "openai/gpt-oss-20b" if base_url else "gpt-5.6-luna"

response = client.responses.create(
    model=model,
    input="Explain Python in 2 simple sentences."
)

print(response.output_text.encode('ascii', errors='ignore').decode('ascii'))