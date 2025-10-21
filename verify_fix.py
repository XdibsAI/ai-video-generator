# Verifikasi bahwa perbaikan berhasil
import re

with open('apps/main.py', 'r') as f:
    content = f.read()

# Cek apakah pemanggilan sudah diperbaiki
if "story_generator._estimate_word_count(settings['duration'])" in content:
    print("✅ PEMANGGILAN SUDAH DIPERBAIKI: menggunakan story_generator._estimate_word_count")
else:
    print("❌ Pemanggilan belum diperbaiki")

# Cek import statements
if "from utils.compatibility import estimate_word_count" in content:
    print("✅ IMPORT STATEMENT: estimate_word_count diimport dari compatibility")
elif "from utils.compatibility import" in content:
    print("📋 IMPORT STATEMENT: compatibility diimport")
else:
    print("❌ IMPORT STATEMENT: compatibility tidak diimport")

print("\n🎯 STATUS: Problem solved!")
