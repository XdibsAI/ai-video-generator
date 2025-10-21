#!/bin/bash

# Perbaiki session state secara komprehensif
python3 << 'PYTHONCODE'
import re

with open('apps/main.py', 'r') as f:
    content = f.read()

# Ganti seluruh method setup_session_state dengan yang lebih robust
new_setup_session_state = '''    def setup_session_state(self):
        """Initialize ALL session state variables dengan cara yang robust"""
        try:
            import streamlit as st
            
            # Daftar semua session state variables yang digunakan di aplikasi
            session_vars = {
                # Story generation
                'story_generated': False,
                'story_options': [],
                'selected_story_index': 0,
                'story_text': "",
                
                # File management
                'uploaded_files': [],
                'other_media_files': [],
                'video_with_audio': None,
                
                # Video generation
                'audio_path': None,
                'video_path': None,
                'optimized_content': None,
                'background_music_path': None,
                
                # Settings
                'selected_color': "#FFFFFF",
                'selected_text_effect': 'none',
                'video_mode': 'video',
                'auto_subtitle_used': False,
                'audio_language': 'id',
                
                # Form values (untuk menghindari key errors)
                'niche': 'Fakta Menarik',
                'language': 'id', 
                'duration': 60,
                'video_format': 'short',
                'text_position': 'middle',
                'font_size': 60,
                'text_color': '#FFFFFF',
                'music_volume': 0.3,
                'user_description': '',
                
                # System flags
                'initialized': True
            }
            
            # Initialize semua variables
            for key, default_value in session_vars.items():
                if key not in st.session_state:
                    st.session_state[key] = default_value
            
            # Try persistent session management
            try:
                from utils.session_manager import setup_persistent_session
                setup_persistent_session()
            except:
                pass
                
        except Exception as e:
            # Fallback jika streamlit tidak tersedia (saat testing)
            print(f"Session state initialization warning: {e}")'''

# Replace setup_session_state method
content = re.sub(
    r'def setup_session_state\(self\):.*?pass',
    new_setup_session_state,
    content,
    flags=re.DOTALL
)

# Pastikan setup_session_state dipanggil di __init__
if 'def __init__(self):' in content:
    init_pattern = r'(def __init__\(self\):.*?)(?=\\n    def|\\nclass|\\Z)'
    init_match = re.search(init_pattern, content, re.DOTALL)
    if init_match:
        init_content = init_match.group(1)
        if 'self.setup_session_state()' not in init_content:
            # Tambahkan pemanggilan setup_session_state
            new_init = init_content.rstrip() + '\\n        self.setup_session_state()\\n'
            content = content.replace(init_content, new_init)

with open('apps/main.py', 'w') as f:
    f.write(content)

print("✅ Session state initialization diperbaiki secara komprehensif")
PYTHONCODE
