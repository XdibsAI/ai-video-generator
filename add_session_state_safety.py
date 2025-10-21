#!/bin/bash

# Tambahkan safety check untuk session state di berbagai method
python3 << 'PYTHONCODE'
import re

with open('apps/main.py', 'r') as f:
    content = f.read()

# Tambahkan safety check di render_story_generator
story_generator_check = '''    def render_story_generator(self, settings):
        """Render story generation section"""
        st.header("📖 Generate Cerita (3 Pilihan)")
        
        # Skip jika sudah menggunakan auto-subtitle
        if st.session_state.get('auto_subtitle_used'):
            st.info("""
            🎯 **Anda sedang menggunakan mode Auto-Subtitle**
            
            Teks sudah diambil dari audio video yang diupload.
            Langsung ke tab **Buat Video** untuk generate video dengan efek teks.
            """)
            return
        
        # Safety check untuk session state
        if 'story_generated' not in st.session_state:
            st.session_state.story_generated = False
        if 'story_options' not in st.session_state:
            st.session_state.story_options = []
        if 'story_text' not in st.session_state:
            st.session_state.story_text = ""'''

content = re.sub(r'def render_story_generator\(self, settings\):.*?st\.header\("📖 Generate Cerita \(3 Pilihan\)"\)', story_generator_check, content, flags=re.DOTALL)

# Tambahkan safety check di render_video_generator
video_generator_check = '''    def render_video_generator(self, settings):
        """Render video generation section dengan text effects"""
        st.header("🎬 Generate Video")
        
        # Safety check untuk session state
        if 'story_generated' not in st.session_state:
            st.session_state.story_generated = False
        if 'story_text' not in st.session_state:
            st.session_state.story_text = ""
        if 'uploaded_files' not in st.session_state:
            st.session_state.uploaded_files = []
        if 'auto_subtitle_used' not in st.session_state:
            st.session_state.auto_subtitle_used = False
        if 'selected_text_effect' not in st.session_state:
            st.session_state.selected_text_effect = 'none'
        if 'video_mode' not in st.session_state:
            st.session_state.video_mode = 'video'
        
        # System capability check'''

content = re.sub(r'def render_video_generator\(self, settings\):.*?st\.header\("🎬 Generate Video"\)', video_generator_check, content, flags=re.DOTALL)

# Tambahkan safety check di render_file_upload
file_upload_check = '''    def render_file_upload(self):
        """Render file upload section untuk tambahkan teks ke video existing"""
        st.header("📁 Upload Video (Tambahkan Teks ke Video Existing)")
        
        # Safety check untuk session state
        if 'uploaded_files' not in st.session_state:
            st.session_state.uploaded_files = []
        if 'other_media_files' not in st.session_state:
            st.session_state.other_media_files = []
        if 'auto_subtitle_used' not in st.session_state:
            st.session_state.auto_subtitle_used = False
        if 'video_with_audio' not in st.session_state:
            st.session_state.video_with_audio = None
        if 'audio_language' not in st.session_state:
            st.session_state.audio_language = 'id'
        
        st.info("""
        **Fitur Add Text to Video:**'''

content = re.sub(r'def render_file_upload\(self\):.*?st\.header\("📁 Upload Video \(Tambahkan Teks ke Video Existing\)"\)', file_upload_check, content, flags=re.DOTALL)

with open('apps/main.py', 'w') as f:
    f.write(content)

print("✅ Safety check untuk session state ditambahkan")
PYTHONCODE
