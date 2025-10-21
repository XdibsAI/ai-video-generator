#!/bin/bash

# Perbaiki UI untuk preview efek teks
python3 << 'PYTHONCODE'
import re

with open('apps/main.py', 'r') as f:
    content = f.read()

# Ganti method render_text_effects_section dengan yang lebih baik
new_text_effects_section = '''    def render_text_effects_section(self):
        """Render text effects selection dengan preview yang visual"""
        self.ensure_session_state()
        
        st.subheader("🎨 Efek Teks Karaoke")
        
        # Effect selection dengan preview visual
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.write("**Pilih Efek Teks:**")
            
            effect_options = [
                ('none', '⚪ Tanpa Efek', 'Teks standar tanpa efek khusus'),
                ('typewriter', '⌨️ Typewriter', 'Teks muncul seperti diketik'),
                ('highlight', '🟡 Highlight', 'Kata aktif disorot kuning'),
                ('glow', '✨ Glow', 'Teks bersinar dengan efek glow'),
                ('neon', '💡 Neon', 'Efek neon seperti papan reklame'),
                ('shadow', '👤 Shadow', 'Teks dengan bayangan'),
                ('gradient', '🌈 Gradient', 'Teks dengan gradien warna')
            ]
            
            selected_effect = st.radio(
                "Pilih efek:",
                options=[opt[0] for opt in effect_options],
                format_func=lambda x: next((opt[1] for opt in effect_options if opt[0] == x), x),
                key="effect_selection_radio"
            )
            
            # Update session state
            self.safe_session_set('selected_text_effect', selected_effect)
            
            # Effect description
            effect_desc = next((opt[2] for opt in effect_options if opt[0] == selected_effect), "")
            st.info(f"**Deskripsi:** {effect_desc}")
        
        with col2:
            st.write("**Preview Efek:**")
            
            # Custom preview area dengan styling
            preview_style = """
            <style>
            .preview-container {
                border: 2px solid #e0e0e0;
                border-radius: 10px;
                padding: 20px;
                margin: 10px 0;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 150px;
                display: flex;
                align-items: center;
                justify-content: center;
                text-align: center;
            }
            .preview-text {
                font-family: 'Arial Black', sans-serif;
                margin: 0;
            """
            
            # Effect-specific styles
            effect_styles = {
                'none': """
                .preview-text {
                    color: white;
                    text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
                }
                """,
                'typewriter': """
                .preview-text {
                    color: white;
                    background: linear-gradient(45deg, #ff6b6b, #feca57);
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                    border-right: 3px solid white;
                    animation: blink 1s infinite;
                }
                @keyframes blink {
                    0%, 50% { border-color: white; }
                    51%, 100% { border-color: transparent; }
                }
                """,
                'highlight': """
                .preview-text {
                    color: white;
                    background: linear-gradient(45deg, #ffd93d, #ff6b6b);
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                    font-weight: bold;
                }
                .highlight-word {
                    background: yellow;
                    color: black;
                    padding: 2px 5px;
                    border-radius: 3px;
                }
                """,
                'glow': """
                .preview-text {
                    color: white;
                    text-shadow: 
                        0 0 5px #fff,
                        0 0 10px #fff,
                        0 0 15px #ff6b6b,
                        0 0 20px #ff6b6b,
                        0 0 25px #ff6b6b;
                    animation: glow 2s ease-in-out infinite alternate;
                }
                @keyframes glow {
                    from { text-shadow: 0 0 5px #fff, 0 0 10px #fff, 0 0 15px #ff6b6b, 0 0 20px #ff6b6b; }
                    to { text-shadow: 0 0 10px #fff, 0 0 15px #ff6b6b, 0 0 20px #ff6b6b, 0 0 25px #ff6b6b; }
                }
                """,
                'neon': """
                .preview-text {
                    color: #00ffff;
                    text-shadow: 
                        0 0 5px #00ffff,
                        0 0 10px #00ffff,
                        0 0 15px #00ffff,
                        0 0 20px #00ffff;
                    font-weight: bold;
                    animation: neon 1.5s ease-in-out infinite alternate;
                }
                @keyframes neon {
                    from { opacity: 0.8; }
                    to { opacity: 1; }
                }
                """,
                'shadow': """
                .preview-text {
                    color: white;
                    text-shadow: 
                        3px 3px 0 #000,
                        6px 6px 0 rgba(0,0,0,0.2);
                    font-weight: bold;
                }
                """,
                'gradient': """
                .preview-text {
                    background: linear-gradient(45deg, #ff6b6b, #4ecdc4, #45b7d1, #96ceb4);
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                    background-size: 300% 300%;
                    animation: gradient 3s ease infinite;
                    font-weight: bold;
                }
                @keyframes gradient {
                    0% { background-position: 0% 50%; }
                    50% { background-position: 100% 50%; }
                    100% { background-position: 0% 50%; }
                }
                """
            }
            
            # Apply selected effect style
            preview_style += effect_styles.get(selected_effect, effect_styles['none'])
            preview_style += "</style>"
            
            # Preview text dengan efek yang dipilih
            preview_text = "Preview Efek Teks"
            if selected_effect == 'highlight':
                preview_text = 'Preview <span class="highlight-word">Efek</span> Teks'
            elif selected_effect == 'typewriter':
                preview_text = "Preview Efek Teks|"
            
            preview_html = f"""
            {preview_style}
            <div class="preview-container">
                <h2 class="preview-text">{preview_text}</h2>
            </div>
            """
            
            st.markdown(preview_html, unsafe_allow_html=True)
            
            # Font size control untuk preview
            font_size = st.slider(
                "Ukuran Font Preview:",
                min_value=24,
                max_value=72,
                value=48,
                key="preview_font_size"
            )
            
            # Update preview dengan font size
            st.markdown(f"""
            <style>
            .preview-text {{
                font-size: {font_size}px !important;
            }}
            </style>
            """, unsafe_allow_html=True)
        
        # Sample text input untuk testing efek
        st.markdown("---")
        st.write("**Custom Teks untuk Testing:**")
        sample_text = st.text_input(
            "Coba efek dengan teks custom:",
            value="Teks Karaoke Demo",
            key="effect_test_text"
        )
        
        if sample_text and sample_text != "Teks Karaoke Demo":
            # Update preview dengan custom text
            st.markdown(f"""
            <div class="preview-container">
                <h2 class="preview-text">{sample_text}</h2>
            </div>
            """, unsafe_allow_html=True)
        
        return selected_effect'''

# Replace the old method
old_method_pattern = r'def render_text_effects_section\(self\):.*?return selected_effect'
content = re.sub(old_method_pattern, new_text_effects_section, content, flags=re.DOTALL)

with open('apps/main.py', 'w') as f:
    f.write(content)

print("✅ UI preview efek teks diperbaiki")
PYTHONCODE
