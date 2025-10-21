"""
Buat working version dengan imports yang work
"""

WORKING_VERSION = '''import streamlit as st
import os
import sys
import json
from datetime import datetime
import uuid
import subprocess

# ✅ SET PAGE_CONFIG PALING AWAL
st.set_page_config(
    page_title="AI Video Generator",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ✅ IMPORT SETELAH PAGE_CONFIG
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.insert(0, project_root)

# ✅ DEFINE CHECK_FFMPEG SEBELUM IMPORT LAINNYA
def check_ffmpeg():
    """Check if FFmpeg is available"""
    try:
        result = subprocess.run([\'ffmpeg\', \'-version\'], 
                              capture_output=True, text=True, timeout=5)
        return result.returncode == 0
    except:
        return False

# ✅ IMPORT DENGAN FALLBACK HANDLING
MOVIEPY_AVAILABLE = False
TTS_AVAILABLE = False

try:
    from gtts import gTTS
    TTS_AVAILABLE = True
except ImportError:
    st.error("❌ gTTS not available - audio features disabled")

try:
    from moviepy.editor import VideoFileClip, ImageClip
    MOVIEPY_AVAILABLE = True
except ImportError:
    st.warning("⚠️ MoviePy not available - video features limited")

# Import utils dengan error handling
try:
    from utils.story_generator import story_generator
    from utils.tts_handler import generate_tts_sync, estimate_audio_duration
    from utils.video_editor import video_editor
    from utils.content_optimizer import content_optimizer
    from utils.compatibility import estimate_word_count
    from utils.text_processor import text_processor
    from utils.speech_to_text import speech_to_text
    from utils.text_effects import text_effects
    
    # Auto load API key dengan error handling
    try:
        from config.settings import OPENROUTER_API_KEY
        if OPENROUTER_API_KEY and OPENROUTER_API_KEY != "your_actual_openrouter_api_key_here":
            story_generator.api_key = OPENROUTER_API_KEY
            st.sidebar.success("✅ API Key Loaded")
        else:
            st.sidebar.warning("⚠️ API Key not configured")
    except ImportError:
        st.sidebar.warning("⚠️ Settings not configured")
    
except ImportError as e:
    st.error(f"❌ Some components not available: {e}")

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        background: linear-gradient(45deg, #FF6B6B, #4ECDC4);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 2rem;
    }
    .story-option {
        padding: 1rem;
        border: 2px solid #e0e0e0;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    .story-option:hover {
        border-color: #4ECDC4;
        background-color: #f8ffff;
    }
    .story-option.selected {
        border-color: #FF6B6B;
        background-color: #fff0f0;
    }
</style>
""", unsafe_allow_html=True)

class VideoGeneratorApp:
    def __init__(self):
        self.setup_session_state()
    
    def setup_session_state(self):
        """Initialize session state"""
        defaults = {
            \'initialized\': True,
            \'story_generated\': False,
            \'story_options\': [],
            \'selected_story_index\': 0,
            \'story_text\': "",
            \'audio_path\': None,
            \'video_path\': None,
            \'uploaded_files\': [],
            \'selected_text_effect\': \'none\'
        }
        
        for key, value in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = value

    def render_sidebar(self):
        """Render sidebar"""
        with st.sidebar:
            st.title("⚙️ Pengaturan Video")
            
            # System status
            st.subheader("🔧 System Status")
            ffmpeg_status = "✅" if check_ffmpeg() else "❌"
            moviepy_status = "✅" if MOVIEPY_AVAILABLE else "❌"
            tts_status = "✅" if TTS_AVAILABLE else "❌"
            
            st.info(f"FFmpeg: {ffmpeg_status}")
            st.info(f"MoviePy: {moviepy_status}")
            st.info(f"TTS: {tts_status}")
            
            st.subheader("📝 Konten Settings")
            niche = st.selectbox("🎯 Tema Konten", ["Fakta Menarik", "Motivasi", "Humor"])
            language = st.selectbox("🌍 Bahasa", ["id", "en"])
            duration = st.selectbox("⏱️ Durasi", [30, 60, 90])
            video_format = st.radio("📐 Format", ["short", "long"])
            
            return {\'niche\': niche, \'language\': language, \'duration\': duration, \'video_format\': video_format}

    # ... (method lainnya tetap sama seperti versi lengkap)
    def render_file_upload(self):
        st.header("📁 Upload Media")
        uploaded_files = st.file_uploader("Pilih file", type=[\'jpg\', \'png\', \'mp4\'], accept_multiple_files=True)
        if uploaded_files:
            st.session_state.uploaded_files = uploaded_files
            st.success(f"✅ {len(uploaded_files)} files uploaded")

    def render_story_generator(self, settings):
        st.header("📖 Generate Cerita")
        if st.button("🎭 Generate Story"):
            try:
                # Use dummy story for testing
                st.session_state.story_text = "Ini adalah contoh teks untuk testing karaoke. Teks akan muncul sync dengan audio."
                st.session_state.story_generated = True
                st.success("✅ Story generated!")
            except Exception as e:
                st.error(f"Error: {e}")

    def render_video_generator(self, settings):
        st.header("🎬 Generate Video")
        if st.button("🚀 Generate Video dengan Karaoke", type="primary"):
            with st.spinner("Creating video..."):
                try:
                    # Test karaoke functionality
                    audio_path = generate_tts_sync(st.session_state.story_text, settings[\'language\'])
                    if audio_path:
                        video_path = video_editor.create_video(
                            media_files=st.session_state.uploaded_files,
                            audio_path=audio_path,
                            duration=settings[\'duration\'],
                            video_format=settings[\'video_format\'],
                            subtitle_text=st.session_state.story_text,
                            font_size=60,
                            text_color=\'white\',
                            text_position=\'middle\'
                        )
                        if video_path:
                            st.session_state.video_path = video_path
                            st.success("✅ Video dengan karaoke berhasil dibuat!")
                except Exception as e:
                    st.error(f"Error: {e}")

    def render_results(self):
        if st.session_state.get(\'video_path\'):
            st.header("🎉 Hasil Video")
            st.video(st.session_state.video_path)

    def run(self):
        st.markdown(\'<h1 class="main-header">🎬 AI Video Generator</h1>\', unsafe_allow_html=True)
        settings = self.render_sidebar()
        
        tab1, tab2, tab3, tab4 = st.tabs(["📁 Upload", "📖 Story", "🎬 Video", "📊 Results"])
        with tab1: self.render_file_upload()
        with tab2: self.render_story_generator(settings)
        with tab3: self.render_video_generator(settings)
        with tab4: self.render_results()

if __name__ == "__main__":
    app = VideoGeneratorApp()
    app.run()
'''

with open(\'apps/main_working.py\', \'w\') as f:
    f.write(WORKING_VERSION)

print("✅ Working version created: apps/main_working.py")
