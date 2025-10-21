#!/bin/bash

# Update story generator untuk skip jika sudah ada auto-subtitle
python3 << 'PYTHONCODE'
import re

with open('apps/main.py', 'r') as f:
    content = f.read()

# Tambahkan pengecekan di awal story generator
story_generator_start = '''    def render_story_generator(self, settings):
        """Render story generation section"""
        st.header("📖 Generate Cerita (3 Pilihan)")'''

story_generator_with_check = '''    def render_story_generator(self, settings):
        """Render story generation section"""
        st.header("📖 Generate Cerita (3 Pilihan)")
        
        # Skip jika sudah menggunakan auto-subtitle
        if st.session_state.get('auto_subtitle_used'):
            st.info("""
            🎯 **Anda sedang menggunakan mode Auto-Subtitle**
            
            Teks sudah diambil dari audio video yang diupload.
            Langsung ke tab **Buat Video** untuk generate video dengan efek teks.
            """)
            return'''

content = content.replace(story_generator_start, story_generator_with_check)

with open('apps/main.py', 'w') as f:
    f.write(content)

print("✅ Story generator skip jika auto-subtitle aktif")
PYTHONCODE
