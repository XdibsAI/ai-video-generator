"""
Buat minimal working version untuk testing karaoke
"""
MINIMAL_APP = '''import streamlit as st
import os
import sys
import tempfile
import uuid
from datetime import datetime

# Setup
st.set_page_config(page_title="AI Video Generator", layout="wide")
st.title("🎬 AI Video Generator - Minimal Test")

# Simple session state
if 'story_text' not in st.session_state:
    st.session_state.story_text = ""
if 'uploaded_files' not in st.session_state:
    st.session_state.uploaded_files = []

# Tab layout
tab1, tab2, tab3 = st.tabs(["📝 Input", "🎨 Settings", "🎬 Generate"])

with tab1:
    st.header("📝 Input Teks dan Media")
    
    # Text input
    story_text = st.text_area(
        "Masukkan teks untuk karaoke:",
        value="Ini adalah contoh teks karaoke. Teks akan muncul sync dengan audio.",
        height=100
    )
    st.session_state.story_text = story_text
    
    # File upload
    uploaded_files = st.file_uploader(
        "Upload media (optional):",
        type=['jpg', 'png', 'mp4'],
        accept_multiple_files=True
    )
    st.session_state.uploaded_files = uploaded_files

with tab2:
    st.header("🎨 Pengaturan Karaoke")
    
    col1, col2 = st.columns(2)
    
    with col1:
        font_size = st.slider("Ukuran Font:", 30, 100, 60)
        text_color = st.selectbox("Warna Teks:", ["white", "yellow", "green", "red", "blue"])
        
    with col2:
        text_position = st.radio("Posisi Teks:", ["Tengah", "Bawah"])
        text_effect = st.selectbox("Efek Teks:", ["none", "shadow", "glow", "neon"])

with tab3:
    st.header("🎬 Generate Video")
    
    if st.button("🚀 Generate Video dengan Karaoke", type="primary"):
        if not st.session_state.story_text:
            st.error("❌ Masukkan teks terlebih dahulu")
        else:
            with st.spinner("Membuat video..."):
                try:
                    # Import inside to avoid startup errors
                    try:
                        from utils.video_editor import video_editor
                        from utils.tts_handler import generate_tts_sync
                        
                        # Generate audio
                        audio_path = generate_tts_sync(st.session_state.story_text, "id")
                        
                        if audio_path and os.path.exists(audio_path):
                            st.success("✅ Audio generated!")
                            
                            # Create video
                            video_path = video_editor.create_video(
                                media_files=st.session_state.uploaded_files,
                                audio_path=audio_path,
                                duration=30,
                                video_format='short',
                                subtitle_text=st.session_state.story_text,
                                font_size=font_size,
                                text_color=text_color,
                                text_position='middle' if text_position == 'Tengah' else 'bottom',
                                text_effect=text_effect
                            )
                            
                            if video_path and os.path.exists(video_path):
                                st.success("✅ Video dengan karaoke berhasil dibuat!")
                                
                                # Show video
                                with open(video_path, 'rb') as f:
                                    video_bytes = f.read()
                                st.video(video_bytes)
                                
                                # Download button
                                st.download_button(
                                    "📥 Download Video",
                                    data=video_bytes,
                                    file_name=f"karaoke_video_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4",
                                    mime="video/mp4"
                                )
                            else:
                                st.error("❌ Gagal membuat video")
                        else:
                            st.error("❌ Gagal generate audio")
                            
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
                        import traceback
                        st.code(traceback.format_exc())
                        
                except Exception as e:
                    st.error(f"❌ System error: {str(e)}")

st.sidebar.info("""
**Testing Features:**
- ✅ Karaoke text sync
- ✅ Text effects  
- ✅ Audio generation
- ✅ Video composition
""")
'''
with open('apps/main_minimal.py', 'w') as f:
    f.write(MINIMAL_APP)

print("✅ Minimal test app created: apps/main_minimal.py")
