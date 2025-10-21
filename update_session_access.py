#!/bin/bash

# Update semua akses session state untuk menggunakan safe methods
python3 << 'PYTHONCODE'
import re

with open('apps/main.py', 'r') as f:
    content = f.read()

# Update render_story_generator untuk menggunakan safe access
old_story_access = '''        # Safety check untuk session state
        if 'story_generated' not in st.session_state:
            st.session_state.story_generated = False
        if 'story_options' not in st.session_state:
            st.session_state.story_options = []
        if 'story_text' not in st.session_state:
            st.session_state.story_text = ""'''

new_story_access = '''        # Ensure session state is initialized
        self.ensure_session_state()'''

content = content.replace(old_story_access, new_story_access)

# Update render_video_generator untuk menggunakan safe access  
old_video_access = '''        # Safety check untuk session state
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

new_video_access = '''        # Ensure session state is initialized
        self.ensure_session_state()
        
        # System capability check'''

content = content.replace(old_video_access, new_video_access)

# Update render_file_upload untuk menggunakan safe access
old_upload_access = '''        # Safety check untuk session state
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

new_upload_access = '''        # Ensure session state is initialized
        self.ensure_session_state()
        
        st.info("""
        **Fitur Add Text to Video:**'''

content = content.replace(old_upload_access, new_upload_access)

# Update semua akses session state di render_story_generator
content = content.replace('st.session_state.story_generated', 'self.safe_session_get("story_generated", False)')
content = content.replace('st.session_state.story_options', 'self.safe_session_get("story_options", [])')
content = content.replace('st.session_state.story_text', 'self.safe_session_get("story_text", "")')
content = content.replace('st.session_state.selected_story_index', 'self.safe_session_get("selected_story_index", 0)')

# Update assignment session state di render_story_generator
content = content.replace('st.session_state.story_generated = True', 'self.safe_session_set("story_generated", True)')
content = content.replace('st.session_state.story_options = story_options', 'self.safe_session_set("story_options", story_options)')
content = content.replace('st.session_state.story_text = story_options[0]', 'self.safe_session_set("story_text", story_options[0])')
content = content.replace('st.session_state.selected_story_index = 0', 'self.safe_session_set("selected_story_index", 0)')

with open('apps/main.py', 'w') as f:
    f.write(content)

print("✅ Semua akses session state diupdate ke safe methods")
PYTHONCODE
