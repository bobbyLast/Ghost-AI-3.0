from dotenv import load_dotenv
import os
import openai

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
if api_key:
    print(f"Loaded API key: {api_key[:4]}...{api_key[-4:]}")
else:
    print("❌ No API key loaded from .env!")
client = openai.OpenAI(api_key=api_key)

prompt = "Say hello from Ghost AI. What is the meaning of intelligence?"

try:
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=64,
        temperature=0.2
    )
    print("✅ ChatGPT API test successful!")
    print("Response:")
    print(response.choices[0].message.content)
except Exception as e:
    print(f"❌ ChatGPT API test failed: {e}") 