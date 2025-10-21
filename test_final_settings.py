import sys
import os
sys.path.insert(0, '/home/dibs/apps')

try:
    from config.settings import *
    print("🎯 FINAL SETTINGS CHECK:")
    print("=" * 50)
    print(f"✅ Model: {DEFAULT_MODEL}")
    print(f"✅ API Key: {'✅ ADA (' + str(len(OPENROUTER_API_KEY)) + ' chars)' if OPENROUTER_API_KEY and OPENROUTER_API_KEY.startswith('sk-or-') else '❌ MASALAH'}")
    print(f"✅ Base URL: {OPENROUTER_BASE_URL}")
    print(f"✅ Debug Mode: {DEBUG}")
    
    # Test fungsi
    result = estimate_word_count(60)
    print(f"✅ estimate_word_count(60): {result}")
    
    print("=" * 50)
    if OPENROUTER_API_KEY and OPENROUTER_API_KEY.startswith('sk-or-'):
        print("🎉 SEMUA SETTING READY UNTUK GROK-4-FAST!")
    else:
        print("⚠️  Periksa kembali API Key di .env file")
    
except Exception as e:
    print(f"❌ Error: {e}")
