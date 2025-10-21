import sys
import os
sys.path.insert(0, '/home/dibs/apps')

try:
    from config.settings import *
    print("✅ Settings import berhasil")
    print(f"Model: {DEFAULT_MODEL}")
    print(f"API Key: {'✅ Ada' if OPENROUTER_API_KEY and OPENROUTER_API_KEY != 'your_actual_api_key_here' else '❌ Tidak ada'}")
    print(f"Base URL: {OPENROUTER_BASE_URL}")
    
    # Test fungsi
    result = estimate_word_count(60)
    print(f"estimate_word_count(60): {result}")
    
except Exception as e:
    print(f"❌ Error: {e}")
