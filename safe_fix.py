# Backup file asli dulu
import shutil
import os

if os.path.exists('apps/main.py.backup'):
    shutil.copy('apps/main.py.backup', 'apps/main.py')
    print("✅ Restore dari backup")

# Buat backup
shutil.copy('apps/main.py', 'apps/main.py.backup')
print("✅ Backup dibuat: apps/main.py.backup")

# Baca file
with open('apps/main.py', 'r') as f:
    content = f.read()

# Hapus semua fungsi estimate_word_count yang mungkin salah
import re

# Hapus fungsi estimate_word_count yang ada
content = re.sub(r'def estimate_word_count\(.*?\):.*?return.*?\)\)', '', content, flags=re.DOTALL)

# Tambahkan fungsi di tempat yang tepat - setelah semua imports
lines = content.split('\n')
new_content = []
imports_done = False

for line in lines:
    new_content.append(line)
    
    # Setelah baris kosong pertama setelah imports, tambahkan fungsi
    if not imports_done and line.strip() == '' and len(new_content) > 10:
        # Cek jika sebelumnya ada import statements
        prev_lines = new_content[-5:]  # Check last 5 lines
        has_imports = any('import' in l or 'from' in l for l in prev_lines if l.strip())
        
        if has_imports:
            new_content.append('')
            new_content.append('def estimate_word_count(duration_seconds):')
            new_content.append('    """')
            new_content.append('    Estimate word count based on duration in seconds')
            new_content.append('    """')
            new_content.append('    if duration_seconds == 30:')
            new_content.append('        return (50, 80)')
            new_content.append('    elif duration_seconds == 60:')
            new_content.append('        return (100, 150)')
            new_content.append('    elif duration_seconds == 90:')
            new_content.append('        return (150, 200)')
            new_content.append('    else:')
            new_content.append('        words_per_second = 2.5')
            new_content.append('        estimated_words = int(duration_seconds * words_per_second)')
            new_content.append('        return (estimated_words - 20, estimated_words + 20)')
            new_content.append('')
            imports_done = True

# Gabungkan kembali
content = '\n'.join(new_content)

# Pastikan pemanggilan fungsi benar
content = content.replace(
    "word_range = story_generator._estimate_word_count(settings['duration'])",
    "word_range = estimate_word_count(settings['duration'])"
)

with open('apps/main.py', 'w') as f:
    f.write(content)

print("✅ File telah diperbaiki dengan aman!")
