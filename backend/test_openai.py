"""Quick test to verify OpenAI API key is working"""
import os
from dotenv import load_dotenv
from openai import AsyncOpenAI
import asyncio

load_dotenv(override=True)

async def test_api():
    api_key = os.getenv('OPENAI_API_KEY', '')
    print(f"API Key Length: {len(api_key)}")
    print(f"API Key starts with: {api_key[:15]}...")
    print(f"API Key ends with: ...{api_key[-10:]}")
    
    if not api_key or api_key == 'sk-your-openai-api-key-here':
        print("❌ Invalid API key!")
        return
    
    try:
        client = AsyncOpenAI(api_key=api_key)
        print("\n✅ Client created successfully")
        
        print("\n⏳ Testing API call with gpt-4o-mini...")
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "Say 'test successful' if you can read this."}],
            max_tokens=20
        )
        
        print(f"✅ API Response: {response.choices[0].message.content}")
        print(f"✅ Tokens used: {response.usage.total_tokens}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_api())
