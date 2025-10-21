#!/bin/bash

# Backup
cp apps/main.py apps/main.py.backup_final2

# Gunakan Python untuk perbaikan yang lebih presisi
python3 << 'PYTHONCODE'
import re

with open('apps/main.py', 'r') as f:
    content = f.read()

# 1. Hapus import estimate_word_count dari compatibility
content = re.sub(
    r'from utils.compatibility import estimate_word_count.*\n',
    '# from utils.compatibility import estimate_word_count  # ❌ Removed due to import issues\n',
    content
)

# 2. Pastikan fungsi estimate_word_count ada di main.py
if 'def estimate_word_count(' not in content:
    # Tambahkan setelah custom CSS
    css_end = content.find('</style>""", unsafe_allow_html=True)')
    if css_end != -1:
        insert_pos = content.find('\n', css_end) + 1
        estimate_function = '''
# ✅ ESTIMATE WORD COUNT FUNCTION
def estimate_word_count(duration_seconds):
    """
    Estimate word count based on duration in seconds
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
        content = content[:insert_pos] + estimate_function + content[insert_pos:]

# 3. Handle text_effects fallback
if 'text_effects = FallbackTextEffects()' not in content:
    # Tambahkan fallback text_effects sebelum class
    class_pos = content.find('class VideoGeneratorApp:')
    if class_pos != -1:
        text_effects_fallback = '''
# ✅ FALLBACK TEXT_EFFECTS
class FallbackTextEffects:
    def render_effects_gallery(self, selected_effect, sample_text, font_size):
        st.info("🎨 Preview Efek Teks (Fallback Mode)")
        st.write(f"**Teks:** {sample_text}")
        st.write(f"**Font Size:** {font_size}px")
        st.write("**Efek Terpilih:** Standar")
    
    def get_effect_display_info(self, effect_name):
        return "Efek Standar", "Teks akan ditampilkan dengan efek standar"

text_effects = FallbackTextEffects()
'''
        content = content[:class_pos] + text_effects_fallback + '\n' + content[class_pos:]

with open('apps/main.py', 'w') as f:
    f.write(content)

print("✅ Semua import dan fallback diperbaiki")
PYTHONCODE
