#!/bin/bash

# Update video generator untuk handle direct auto-subtitle
python3 << 'PYTHONCODE'
import re

with open('apps/main.py', 'r') as f:
    content = f.read()

# Perbaiki video generator untuk skip story generation jika auto-subtitle
# Cari bagian pengecekan story_generated
old_story_check = '''        if not st.session_state.story_generated and not auto_subtitle:
            st.warning("⚠️ Silakan generate cerita atau aktifkan auto-subtitle terlebih dahulu")
            return'''

new_story_check = '''        # Check if we have content for video - either from story OR auto-subtitle
        has_content = st.session_state.story_generated or auto_subtitle or st.session_state.get('auto_subtitle_used', False)
        
        if not has_content:
            st.warning("""
            ⚠️ Belum ada konten untuk video. Pilih salah satu:
            
            1. **Tab Upload Media**: Upload video dengan audio untuk auto-subtitle
            2. **Tab Generate Cerita**: Buat cerita baru dengan AI
            """)
            return'''

# Replace the check
content = content.replace(old_story_check, new_story_check)

# Also update the mode selection info
old_mode_info = '''        with col2:
            if video_mode == 'video':
                st.info("""
                **🎬 Video dengan Media:**
                - Gunakan gambar/video yang diupload
                - Teks karaoke muncul di atas media
                - Cocok untuk content yang visual
                """)
            else:
                st.info("""
                **📝 Teks Karaoke Only:**
                - Background hitam polos
                - Fokus pada teks karaoke
                - Cocok untuk lyric video atau quotes
                - Lebih cepat render
                """)'''

new_mode_info = '''        with col2:
            if video_mode == 'video':
                if st.session_state.get('auto_subtitle_used'):
                    st.info("""
                    **🎬 Mode Auto-Subtitle:**
                    - Gunakan video yang sudah diupload
                    - Teks karaoke sync dengan audio original
                    - Efek teks applied pada video existing
                    """)
                else:
                    st.info("""
                    **🎬 Video dengan Media:**
                    - Gunakan gambar/video yang diupload
                    - Teks karaoke muncul di atas media
                    - Cocok untuk content yang visual
                    """)
            else:
                st.info("""
                **📝 Teks Karaoke Only:**
                - Background hitam polos
                - Fokus pada teks karaoke
                - Cocok untuk lyric video atau quotes
                - Lebih cepat render
                """)'''

content = content.replace(old_mode_info, new_mode_info)

with open('apps/main.py', 'w') as f:
    f.write(content)

print("✅ Video generator diupdate untuk direct auto-subtitle")
PYTHONCODE
