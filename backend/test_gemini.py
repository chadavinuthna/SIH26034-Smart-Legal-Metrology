import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise RuntimeError("GEMINI_API_KEY not found")

client = genai.Client(api_key=api_key)

print("Gemini connection initialized.")
print("Available models:")

for model in client.models.list():
    print(model.name)