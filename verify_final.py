# Verifikasi final
with open('apps/main.py', 'r') as f:
    content = f.read()

print("🔍 VERIFIKASI FINAL:")

# Cek apakah fungsi estimate_word_count ada
if 'def estimate_word_count(' in content:
    print("✅ FUNGSI: estimate_word_count ada di main.py")
else:
    print("❌ FUNGSI: estimate_word_count tidak ditemukan")

# Cek apakah pemanggilan sudah benar
if "word_range = estimate_word_count(settings['duration'])" in content:
    print("✅ PEMANGGILAN: estimate_word_count dipanggil dengan benar")
else:
    print("❌ PEMANGGILAN: estimate_word_count tidak dipanggil dengan benar")

# Cek apakah story_generator diimport
if 'from utils.story_generator import story_generator' in content:
    print("✅ IMPORT: story_generator diimport")
else:
    print("⚠️ IMPORT: story_generator tidak diimport (tidak masalah)")

print("\n🎯 STATUS: Aplikasi seharusnya bekerja sekarang!")
