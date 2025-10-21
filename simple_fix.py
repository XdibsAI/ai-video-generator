#!/bin/bash

# Backup
cp apps/main.py apps/main.py.backup_simple_fix

# Tambahkan fungsi estimate_word_count di tempat yang tepat
python3 << 'PYTHONCODE'
import re

with open('apps/main.py', 'r') as f:
    content = f.read()

# Cari posisi setelah Custom CSS dan sebelum class VideoGeneratorApp
css_end = content.find('</style>""", unsafe_allow_html=True)')
if css_end != -1:
    # Tempat untuk menambahkan fungsi
    insert_pos = content.find('\n', css_end) + 1
    
    # Fungsi yang akan ditambahkan
    estimate_function = '''
# ✅ FALLBACK FUNCTION untuk estimate_word_count
def estimate_word_count(duration_seconds):
    """
    Estimate word count based on duration in seconds
    Fallback function if import from utils.compatibility fails
    """
    if duration_seconds == 30:
        return (50, 80)
    elif duration_seconds == 60:
        return (100, 150)
    elif duration_seconds == 90:
        return (150, 200)
    else:
        words_per_second = 2.5
        estimated_words = int(duration_seconds * words_per_second)
        return (estimated_words - 20, estimated_words + 20)

'''
    
    # Sisipkan fungsi
    new_content = content[:insert_pos] + estimate_function + content[insert_pos:]
    
    with open('apps/main.py', 'w') as f:
        f.write(new_content)
    print("✅ Fungsi estimate_word_count ditambahkan")
else:
    print("❌ Tidak bisa menemukan posisi untuk menambahkan fungsi")

PYTHONCODE
