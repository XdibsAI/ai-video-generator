import sys
import os
sys.path.insert(0, '/home/dibs/apps')

try:
    from config.settings import *
    from utils.story_generator import story_generator
    
    print("🧪 TEST STORY GENERATOR DENGAN GROK:")
    print("=" * 50)
    
    # Set API key
    story_generator.api_key = OPENROUTER_API_KEY
    story_generator.model = DEFAULT_MODEL
    
    print(f"✅ Model: {story_generator.model}")
    print(f"✅ API Key Set: {'✅' if story_generator.api_key and story_generator.api_key.startswith('sk-or-') else '❌'}")
    print(f"✅ Base URL: {story_generator.base_url}")
    
    # Test kecil - generate cerita sederhana
    if story_generator.api_key and story_generator.api_key.startswith('sk-or-'):
        print("🚀 Mencoba generate cerita demo...")
        try:
            stories = story_generator.generate_stories(
                niche="Fakta Menarik",
                duration_seconds=60,
                style="Serius", 
                language="id",
                user_description="Tentang teknologi AI"
            )
            if stories:
                print(f"✅ Berhasil generate {len(stories)} cerita!")
                for i, story in enumerate(stories[:1]):  # Tampilkan hanya 1 untuk test
                    print(f"Cerita {i+1}: {story[:100]}...")
            else:
                print("❌ Gagal generate cerita")
        except Exception as e:
            print(f"⚠️  Error saat generate: {e}")
            print("Ini normal untuk test pertama")
    else:
        print("❌ API Key tidak valid, skip generate test")
        
    print("=" * 50)
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
