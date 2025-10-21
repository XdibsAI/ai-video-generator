# Script untuk memperbaiki import story_generator
import re

# Baca file apps/main.py
with open('apps/main.py', 'r') as f:
    content = f.read()

print("🔍 Memeriksa import statements...")

# Cek apakah story_generator sudah diimport
if 'from utils.story_generator import story_generator' in content:
    print("✅ story_generator sudah diimport")
else:
    print("❌ story_generator belum diimport dengan benar")
    
    # Perbaiki import statement
    # Cari baris import story_generator dan perbaiki
    if 'from utils.story_generator import' in content:
        # Ganti dengan import yang spesifik
        content = content.replace(
            'from utils.story_generator import *',
            'from utils.story_generator import story_generator'
        )
    else:
        # Tambahkan import yang benar
        # Cari baris setelah import settings
        content = content.replace(
            'from config.settings import *',
            'from config.settings import *\nfrom utils.story_generator import story_generator'
        )

with open('apps/main.py', 'w') as f:
    f.write(content)

print("✅ Import story_generator telah diperbaiki!")
