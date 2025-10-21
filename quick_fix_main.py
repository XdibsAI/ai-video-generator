# Quick fix - ganti dengan method dari story_generator yang sudah terimport
with open('apps/main.py', 'r') as f:
    content = f.read()

# Ganti pemanggilan estimate_word_count dengan story_generator._estimate_word_count
content = content.replace(
    "word_range = estimate_word_count(settings['duration'])",
    "word_range = story_generator._estimate_word_count(settings['duration'])"
)

with open('apps/main.py', 'w') as f:
    f.write(content)

print("✅ Quick fix applied - menggunakan story_generator method!")
