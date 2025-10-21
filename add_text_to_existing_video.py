#!/bin/bash

# Buat mode khusus untuk menambah teks ke video existing
python3 << 'PYTHONCODE'
import re

with open('apps/main.py', 'r') as f:
    content = f.read()

# Update bagian upload untuk mode add text to existing video
old_upload_intro = '''    def render_file_upload(self):
        """Render file upload section dengan direct auto-subtitle to video"""
        st.header("📁 Upload Video dengan Audio (Auto Subtitle)")
        
        st.info("""
        **Workflow Cepat:**
        1. Upload video yang sudah ada audio
        2. Sistem otomatis extract teks dari audio  
        3. Langsung ke tab Generate Video dengan efek teks
        *Tidak perlu melalui Generate Cerita*
        """)'''

new_upload_intro = '''    def render_file_upload(self):
        """Render file upload section untuk tambahkan teks ke video existing"""
        st.header("📁 Upload Video (Tambahkan Teks ke Video Existing)")
        
        st.info("""
        **Fitur Add Text to Video:**
        1. Upload video yang sudah ada audio narasi
        2. Sistem extract teks dari audio otomatis
        3. Tambahkan teks karaoke ke video yang sama
        4. Hasil: Video original + teks subtitle yang sync dengan audio
        """)'''

content = content.replace(old_upload_intro, new_upload_intro)

# Update bagian video generator untuk mode add text to existing video
old_mode_selection = '''        # ✅ MODE SELECTION
        st.subheader("🎯 Pilih Mode Video")
        
        col1, col2 = st.columns(2)
        
        with col1:
            video_mode = st.radio(
                "Pilih jenis video:",
                options=['video', 'text_only'],
                format_func=lambda x: "🎬 Video dengan Media" if x == 'video' else "📝 Teks Karaoke Only",
                index=0,
                key="video_mode_radio"
            )'''

new_mode_selection = '''        # ✅ MODE SELECTION - TAMBAH SPECIAL MODE UNTUK EXISTING VIDEO
        st.subheader("🎯 Pilih Mode Video")
        
        # Determine available modes based on uploaded content
        has_video_with_audio = st.session_state.get('auto_subtitle_used', False)
        has_other_media = st.session_state.get('uploaded_files') or st.session_state.get('other_media_files')
        
        mode_options = []
        mode_descriptions = {}
        
        if has_video_with_audio:
            mode_options.append('add_text_to_video')
            mode_descriptions['add_text_to_video'] = "🎬 Tambah Teks ke Video Existing"
        
        if has_other_media or not has_video_with_audio:
            mode_options.append('video')
            mode_descriptions['video'] = "🎬 Video Baru dengan Media"
        
        mode_options.append('text_only')
        mode_descriptions['text_only'] = "📝 Teks Karaoke Only"
        
        col1, col2 = st.columns(2)
        
        with col1:
            video_mode = st.radio(
                "Pilih jenis video:",
                options=mode_options,
                format_func=lambda x: mode_descriptions[x],
                index=0,
                key="video_mode_radio"
            )'''

content = content.replace(old_mode_selection, new_mode_selection)

# Update mode info section
old_mode_info = '''        with col2:
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

new_mode_info = '''        with col2:
            if video_mode == 'add_text_to_video':
                st.info("""
                **🎬 Tambah Teks ke Video Existing:**
                - Gunakan video yang sudah diupload
                - Teks karaoke sync dengan audio original
                - Hasil: Video sama + teks subtitle
                - Perfect untuk video narasi yang butuh teks
                """)
            elif video_mode == 'video':
                st.info("""
                **🎬 Video Baru dengan Media:**
                - Buat video baru dengan media yang diupload
                - Teks karaoke dengan audio TTS
                - Cocok untuk content baru
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

print("✅ Mode 'Add Text to Existing Video' telah ditambahkan")
PYTHONCODE
