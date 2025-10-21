#!/bin/bash

# Tambahkan method helper untuk safe session state access
python3 << 'PYTHONCODE'
import re

with open('apps/main.py', 'r') as f:
    content = f.read()

# Tambahkan method helper di class VideoGeneratorApp
helper_methods = '''
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

# Cari class VideoGeneratorApp dan tambahkan methods setelah __init__
class_pattern = r'(class VideoGeneratorApp:.*?def __init__\(self\):.*?self\\.setup_session_state\(\\)\\n)'
class_match = re.search(class_pattern, content, re.DOTALL)

if class_match:
    class_content = class_match.group(1)
    new_class_content = class_content + '\\n' + helper_methods + '\\n'
    content = content.replace(class_content, new_class_content)

with open('apps/main.py', 'w') as f:
    f.write(content)

print("✅ Safe session access methods ditambahkan")
PYTHONCODE
