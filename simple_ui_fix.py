#!/bin/bash

# Patch sederhana untuk memperbaiki UI tanpa mengubah struktur
python3 << 'PYTHONCODE'
import re

with open('apps/main.py', 'r') as f:
    content = f.read()

# 1. Perbaiki method render_text_effects_section dengan yang sederhana
simple_text_effects = '''    def render_text_effects_section(self):
        """Render text effects selection dengan preview sederhana"""
        self.ensure_session_state()
        
        st.subheader("🎨 Efek Teks Karaoke")
        
        # Effect selection sederhana
        effect_options = [
            ('none', '⚪ Tanpa Efek'),
            ('typewriter', '⌨️ Typewriter'), 
            ('highlight', '🟡 Highlight'),
            ('glow', '✨ Glow'),
            ('shadow', '👤 Shadow')
        ]
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            selected_effect = st.radio(
                "Pilih efek teks:",
                options=[opt[0] for opt in effect_options],
                format_func=lambda x: next((opt[1] for opt in effect_options if opt[0] == x), x),
                key="effect_radio"
            )
            self.safe_session_set('selected_text_effect', selected_effect)
        
        with col2:
            st.write("**Preview:**")
            
            # Simple preview box
            preview_style = """
            <style>
            .preview-box {
                border: 2px solid #e0e0e0;
                border-radius: 10px;
                padding: 20px;
                background: #f8f9fa;
                text-align: center;
                min-height: 100px;
                display: flex;
                align-items: center;
                justify-content: center;
                margin: 10px 0;
            }
            """
            
            # Effect preview text
            preview_text = "Preview Efek Teks"
            if selected_effect == 'glow':
                preview_style += """
                .preview-text { 
                    color: white;
                    text-shadow: 0 0 10px #ff6b6b, 0 0 20px #ff6b6b;
                    font-weight: bold;
                    font-size: 24px;
                }
                .preview-box { background: linear-gradient(135deg, #667eea, #764ba2); }
                """
            elif selected_effect == 'typewriter':
                preview_style += """
                .preview-text { 
                    color: #333;
                    font-family: monospace;
                    font-size: 20px;
                    border-right: 3px solid #333;
                    animation: blink 1s infinite;
                }
                @keyframes blink {
                    0%, 50% { border-color: #333; }
                    51%, 100% { border-color: transparent; }
                }
                """
            elif selected_effect == 'highlight':
                preview_style += """
                .preview-text { 
                    color: #333;
                    font-weight: bold;
                    font-size: 22px;
                }
                .highlight { background: yellow; padding: 2px 5px; }
                """
                preview_text = 'Preview <span class="highlight">Efek</span> Teks'
            else:
                preview_style += """
                .preview-text { 
                    color: #333;
                    font-size: 22px;
                    font-weight: bold;
                }
                """
            
            preview_html = f"""
            {preview_style}
            <div class="preview-box">
                <div class="preview-text">{preview_text}</div>
            </div>
            </style>
            """
            
            st.markdown(preview_html, unsafe_allow_html=True)
            
            # Font size control
            font_size = st.slider(
                "Ukuran font:",
                min_value=16,
                max_value=48, 
                value=24,
                key="font_size_slider"
            )
        
        return selected_effect'''

# Replace text effects method
if 'def render_text_effects_section(self):' in content:
    # Cari method dan ganti dengan yang sederhana
    pattern = r'def render_text_effects_section\(self\):.*?return selected_effect'
    content = re.sub(pattern, simple_text_effects, content, flags=re.DOTALL)

# 2. Pastikan safe_session methods ada
if 'def safe_session_get(self, key, default=None):' not in content:
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
    
    # Tambahkan setelah setup_session_state
    if 'def setup_session_state(self):' in content:
        setup_end = content.find('def render_', content.find('def setup_session_state(self):'))
        if setup_end != -1:
            content = content[:setup_end] + safe_methods + '\\n\\n' + content[setup_end:]

# 3. Tambahkan ensure_session_state call di method yang perlu
methods_to_fix = ['render_text_effects_section', 'render_file_upload', 'render_story_generator', 'render_video_generator', 'render_results']

for method in methods_to_fix:
    pattern = f'def {method}\(.*?\):'
    match = re.search(pattern, content)
    if match:
        method_start = match.end()
        # Cari baris pertama setelah method definition
        next_line_start = content.find('\\n', method_start) + 1
        if next_line_start > 0 and 'self.ensure_session_state()' not in content[match.start():match.start()+200]:
            # Tambahkan ensure_session_state call
            indent = '        '
            content = content[:next_line_start] + f'{indent}self.ensure_session_state()\\n' + content[next_line_start:]

with open('apps/main.py', 'w') as f:
    f.write(content)

print("✅ Simple UI fix applied")
PYTHONCODE
