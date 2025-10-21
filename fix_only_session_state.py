#!/bin/bash

# Perbaiki session state di file original tanpa menghapus fitur
python3 << 'PYTHONCODE'
import re

with open('apps/main.py', 'r') as f:
    content = f.read()

# 1. Perbaiki setup_session_state method
new_setup_session_state = '''    def setup_session_state(self):
        """Initialize session state dengan persistent management"""
        # Initialize default values
        defaults = {
            'initialized': True,
            'story_generated': False,
            'story_options': [],
            'selected_story_index': 0,
            'story_text': "",
            'audio_path': None,
            'video_path': None,
            'uploaded_files': [],
            'optimized_content': None,
            'selected_color': "#FFFFFF",
            'background_music': None,
            'background_music_path': None,
            'selected_text_effect': 'none',
            'video_mode': 'video',
            'auto_subtitle_used': False,
            'video_with_audio': None,
            'audio_language': 'id',
            'other_media_files': []
        }
        
        for key, value in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = value
        
        # Try to setup persistent session
        try:
            from utils.session_manager import setup_persistent_session
            setup_persistent_session()
        except:
            pass'''

# Replace setup_session_state method
content = re.sub(
    r'def setup_session_state\(self\):.*?pass',
    new_setup_session_state,
    content,
    flags=re.DOTALL
)

# 2. Tambahkan safe session methods
safe_methods = '''
    def safe_session_get(self, key, default=None):
        """Safely get value from session state"""
        try:
            import streamlit as st
            return st.session_state.get(key, default)
        except:
            return default
    
    def safe_session_set(self, key, value):
        """Safely set value in session state"""
        try:
            import streamlit as st
            st.session_state[key] = value
            return True
        except:
            return False
    
    def ensure_session_state(self):
        """Ensure all required session state variables exist"""
        self.setup_session_state()'''

# Tambahkan methods setelah __init__
if 'def setup_session_state(self):' in content:
    # Cari akhir setup_session_state method
    setup_end = content.find('def render_', content.find('def setup_session_state(self):'))
    if setup_end != -1:
        content = content[:setup_end] + safe_methods + '\\n\\n' + content[setup_end:]

# 3. Tambahkan ensure_session_state di setiap render method
methods_to_protect = [
    'def render_text_effects_section',
    'def render_sidebar', 
    'def render_file_upload',
    'def render_story_generator',
    'def render_video_generator',
    'def render_results',
    'def render_header'
]

for method in methods_to_protect:
    pattern = f'({method}\(.*?):.*?(?=def |\\Z)'
    match = re.search(pattern, content, re.DOTALL)
    if match:
        method_content = match.group(0)
        # Tambahkan ensure_session_state di awal method
        if 'self.ensure_session_state()' not in method_content:
            first_line_end = method_content.find('\\n') + 1
            new_method_content = method_content[:first_line_end] + '        self.ensure_session_state()\\n' + method_content[first_line_end:]
            content = content.replace(method_content, new_method_content)

with open('apps/main.py', 'w') as f:
    f.write(content)

print("✅ Session state diperbaiki tanpa menghilangkan fitur")
PYTHONCODE
