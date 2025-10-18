#!/usr/bin/env python3
"""
Test script untuk OpenRouter API
"""

import os
import sys
from dotenv import load_dotenv

# Add project root to path
sys.path.append('.')

load_dotenv()

def test_api():
    """Test OpenRouter API connection"""
    
    api_key = os.getenv('OPENROUTER_API_KEY')
    
    if not api_key or api_key == "your_actual_openrouter_api_key_here":
        print("❌ API key belum dikonfigurasi")
        print("💡 Edit file .env dengan API key yang valid")
        return False
    
    try:
        import requests
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "x-ai/grok-4-fast",
            "messages": [
                {
                    "role": "user",
                    "content": "Hello, please respond with 'API Test Successful' if you can read this."
                }
            ],
            "max_tokens": 50
        }
        
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            message = result['choices'][0]['message']['content']
            print(f"✅ API Test Successful: {message}")
            return True
        else:
            print(f"❌ API Error {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    test_api()
