# Script untuk memperbaiki import estimate_word_count
import re

# Baca file apps/main.py
with open('apps/main.py', 'r') as f:
    content = f.read()

# Perbaiki baris import - pastikan estimate_word_count diimport dengan benar
# Cari baris import dari utils.compatibility
if 'from utils.compatibility import estimate_word_count' in content:
    print("✅ Import statement sudah benar")
else:
    # Tambahkan import yang spesifik
    content = content.replace(
        'from utils.compatibility import *',
        'from utils.compatibility import estimate_word_count, sanitize_filename, get_system_info, check_ffmpeg_available, get_video_codecs, safe_file_delete, get_temp_directory'
    )
    
    # Atau jika tidak ada import compatibility sama sekali, tambahkan
    if 'from utils.compatibility import' not in content:
        # Tambahkan setelah import session_manager
        content = content.replace(
            'from utils.session_manager import setup_persistent_session, show_session_info',
            'from utils.session_manager import setup_persistent_session, show_session_info\nfrom utils.compatibility import estimate_word_count'
        )

with open('apps/main.py', 'w') as f:
    f.write(content)

print("✅ Import statement telah diperbaiki!")
