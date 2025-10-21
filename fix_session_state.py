#!/bin/bash

# Perbaiki session state initialization di main.py
python3 << 'PYTHONCODE'
import re

with open('apps/main.py', 'r') as f:
    content = f.read()

# Perbaiki method setup_session_state untuk inisialisasi yang lebih komprehensif
old_setup_session_state = '''    def setup_session_state(self):
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
            'video_mode': 'video'
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

new_setup_session_state = '''    def setup_session_state(self):
        """Initialize session state dengan persistent management"""
        # Initialize ALL session state variables yang digunakan di aplikasi
        defaults = {
            'initialized': True,
            'story_generated': False,
            'story_options': [],
            'selected_story_index': 0,
            'story_text': "",
            'audio_path': None,
            'video_path': None,
            'uploaded_files': [],
            'other_media_files': [],
            'optimized_content': None,
            'selected_color': "#FFFFFF",
            'background_music': None,
            'background_music_path': None,
            'selected_text_effect': 'none',
            'video_mode': 'video',
            'auto_subtitle_used': False,
            'video_with_audio': None,
            'audio_language': 'id',
            # Tambahkan semua keys yang mungkin digunakan
            'niche': 'Fakta Menarik',
            'language': 'id',
            'duration': 60,
            'video_format': 'short',
            'text_position': 'middle',
            'font_size': 60,
            'text_color': '#FFFFFF',
            'music_volume': 0.3,
            'user_description': ''
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

content = content.replace(old_setup_session_state, new_setup_session_state)

# Pastikan setup_session_state dipanggil di __init__
if 'def __init__(self):' in content:
    init_pattern = r'(def __init__\(self\):.*?)(?=def|\\Z)'
    init_match = re.search(init_pattern, content, re.DOTALL)
    if init_match:
        init_content = init_match.group(1)
        if 'self.setup_session_state()' not in init_content:
            # Tambahkan pemanggilan setup_session_state
            new_init = init_content.rstrip() + '\\n        self.setup_session_state()\\n'
            content = content.replace(init_content, new_init)

with open('apps/main.py', 'w') as f:
    f.write(content)

print("✅ Session state initialization diperbaiki")
PYTHONCODE
