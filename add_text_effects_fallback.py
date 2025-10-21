#!/bin/bash

# Tambahkan fallback text_effects sebelum class VideoGeneratorApp
python3 << 'PYTHONCODE'
import re

with open('apps/main.py', 'r') as f:
    content = f.read()

# Cari class VideoGeneratorApp
class_pos = content.find('class VideoGeneratorApp:')
if class_pos != -1:
    # Tambahkan fallback text_effects sebelum class
    fallback_text = '''
# ✅ FALLBACK TEXT_EFFECTS
class FallbackTextEffects:
    def render_effects_gallery(self, selected_effect, sample_text, font_size):
        st.info("🎨 Preview Efek Teks")
        st.write(f"Teks: {sample_text}")
        st.write(f"Ukuran Font: {font_size}px")
        st.write("Efek: Standar")
    
    def get_effect_display_info(self, effect_name):
        return "Efek Standar", "Teks akan ditampilkan dengan efek standar"

# Initialize fallback
text_effects = FallbackTextEffects()
'''
    
    new_content = content[:class_pos] + fallback_text + '\n' + content[class_pos:]
    
    with open('apps/main.py', 'w') as f:
        f.write(new_content)
    print("✅ Fallback text_effects ditambahkan")
else:
    print("❌ Tidak bisa menemukan class VideoGeneratorApp")

PYTHONCODE
