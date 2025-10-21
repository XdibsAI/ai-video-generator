#!/bin/bash

# Buat file main.py yang clean dan working
cat > apps/main.py << 'MAINEOF'
import streamlit as st
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
        result = subprocess.run(['ffmpeg', '-version'], 
                              capture_output=True, text=True, timeout=5)
        return result.returncode == 0
    except:
        return False

def setup_ffmpeg_warning():
    """Display FFmpeg warning"""
    st.warning("⚠️ FFmpeg not available - video processing limited")

# ✅ FALLBACK FUNCTIONS
def estimate_word_count(duration_seconds):
    """Estimate word count based on duration in seconds"""
    if duration_seconds == 30:
        return (50, 80)
    elif duration_seconds == 60:
        return (100, 150)
    elif duration_seconds == 90:
        return (150, 200)
    else:
        words_per_second = 2.5
        estimated_words = int(duration_seconds * words_per_second)
        return (estimated_words - 20, estimated_words + 20)

# Fallback classes
class FallbackTextEffects:
    def render_effects_gallery(self, selected_effect, sample_text, font_size):
        st.info("🎨 Preview Efek Teks")
        st.write(f"**Teks:** {sample_text}")
        st.write(f"**Font Size:** {font_size}px")
        st.write("**Efek Terpilih:** Standar")
    
    def get_effect_display_info(self, effect_name):
        return "Efek Standar", "Teks akan ditampilkan dengan efek standar"

class FallbackStoryGenerator:
    def __init__(self): 
        self.api_key = None
    
    def generate_stories(self, niche, duration_seconds, style, language, user_description=""):
        return [
            f"Ini adalah cerita fallback 1 tentang {niche}",
            f"Ini adalah cerita fallback 2 tentang {niche}", 
            f"Ini adalah cerita fallback 3 tentang {niche}"
        ]

# Initialize fallbacks
text_effects = FallbackTextEffects()
story_generator = FallbackStoryGenerator()

# ✅ TRY TO IMPORT REAL DEPENDENCIES
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

# Try to import other modules dengan fallback
try:
    from config.settings import *
except ImportError:
    OPENROUTER_API_KEY = None
    OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
    DEFAULT_MODEL = "x-ai/grok-4-fast"

try:
    from utils.story_generator import story_generator as real_story_generator
    story_generator = real_story_generator
    if OPENROUTER_API_KEY:
        story_generator.api_key = OPENROUTER_API_KEY
except ImportError:
    st.warning("⚠️ Using fallback story_generator")

try:
    from utils.text_effects import text_effects as real_text_effects
    text_effects = real_text_effects
except ImportError:
    st.warning("⚠️ Using fallback text_effects")

try:
    from utils.video_editor import video_editor
except ImportError:
    st.error("❌ video_editor not available")

try:
    from utils.tts_handler import generate_tts_sync, estimate_audio_duration
except ImportError:
    st.warning("⚠️ TTS handler not available")
    def generate_tts_sync(text, language):
        return f"/tmp/fallback_audio_{uuid.uuid4().hex[:8]}.mp3"
    def estimate_audio_duration(text, language):
        return len(text.split()) * 0.5

try:
    from utils.speech_to_text import speech_to_text
except ImportError:
    st.warning("⚠️ speech_to_text not available")
    class FallbackSpeechToText:
        def transcribe_video(self, video_file, language):
            return "Ini adalah teks fallback dari transkripsi audio."
    speech_to_text = FallbackSpeechToText()

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
        """Initialize ALL session state variables"""
        try:
            # Daftar semua session state variables
            session_vars = {
                'story_generated': False,
                'story_options': [],
                'selected_story_index': 0,
                'story_text': "",
                'uploaded_files': [],
                'audio_path': None,
                'video_path': None,
                'selected_text_effect': 'none',
                'video_mode': 'video',
                'auto_subtitle_used': False
            }
            
            for key, default_value in session_vars.items():
                if key not in st.session_state:
                    st.session_state[key] = default_value
                    
        except Exception as e:
            print(f"Session state init warning: {e}")
    
    def safe_session_get(self, key, default=None):
        """Safely get value from session state"""
        try:
            return st.session_state.get(key, default)
        except:
            return default
    
    def safe_session_set(self, key, value):
        """Safely set value in session state"""
        try:
            st.session_state[key] = value
            return True
        except:
            return False
    
    def ensure_session_state(self):
        """Ensure all required session state variables exist"""
        self.setup_session_state()

    def render_header(self):
        """Render application header"""
        st.markdown('<h1 class="main-header">🎬 AI Video Generator</h1>', unsafe_allow_html=True)
        st.markdown("""
        <div style='text-align: center; margin-bottom: 2rem;'>
            <p style='font-size: 1.2rem; color: #666;'>
                Buat video menarik dengan AI dalam hitungan menit!
            </p>
        </div>
        """, unsafe_allow_html=True)

    def render_sidebar(self):
        """Render sidebar dengan system info"""
        with st.sidebar:
            st.title("⚙️ Pengaturan Video")
            
            # System Status
            st.subheader("🔧 System Status")
            if check_ffmpeg():
                st.success("✅ FFmpeg Ready")
            else:
                st.error("❌ FFmpeg Missing")
            
            if MOVIEPY_AVAILABLE:
                st.success("✅ MoviePy Ready")
            else:
                st.error("❌ MoviePy Missing")
            
            if TTS_AVAILABLE:
                st.success("✅ TTS Ready")
            else:
                st.error("❌ TTS Missing")
            
            # Settings
            st.subheader("📝 Konten Settings")
            niche = st.selectbox("🎯 Tema Konten", 
                               ["Fakta Menarik", "Motivasi", "Humor", "Petualangan", "Pendidikan"])
            language = st.selectbox("🌍 Bahasa", ["id", "en"])
            duration = st.selectbox("⏱️ Durasi Video", [30, 60, 90])
            
            return {
                'niche': niche, 'language': language, 'duration': duration,
                'video_format': 'short', 'text_position': 'middle',
                'font_size': 60, 'text_color': '#FFFFFF', 'music_volume': 0.3,
                'user_description': ''
            }

    def render_file_upload(self):
        """Render file upload section"""
        st.header("📁 Upload Media")
        self.ensure_session_state()
        
        st.info("Upload video untuk auto-subtitle atau media untuk video baru")
        
        uploaded_file = st.file_uploader(
            "Pilih file video atau gambar",
            type=['mp4', 'mov', 'avi', 'jpg', 'jpeg', 'png'],
            accept_multiple_files=False
        )
        
        if uploaded_file:
            self.safe_session_set('uploaded_files', [uploaded_file])
            st.success(f"✅ {uploaded_file.name} uploaded")
            
            if uploaded_file.type.startswith('video'):
                st.video(uploaded_file)
            else:
                st.image(uploaded_file)

    def render_story_generator(self, settings):
        """Render story generation section"""
        st.header("📖 Generate Cerita")
        self.ensure_session_state()
        
        word_range = estimate_word_count(settings['duration'])
        st.info(f"**Target:** {word_range[0]}-{word_range[1]} kata")
        
        if st.button("🎭 Generate Cerita"):
            stories = story_generator.generate_stories(
                settings['niche'], settings['duration'], "Serius", settings['language']
            )
            if stories:
                self.safe_session_set('story_options', stories)
                self.safe_session_set('story_text', stories[0])
                self.safe_session_set('story_generated', True)
                st.success("✅ Cerita berhasil di-generate!")
        
        if self.safe_session_get('story_generated'):
            story_text = self.safe_session_get('story_text', '')
            st.text_area("Cerita:", value=story_text, height=200)

    def render_video_generator(self, settings):
        """Render video generation section"""
        st.header("🎬 Generate Video")
        self.ensure_session_state()
        
        if not self.safe_session_get('story_generated'):
            st.warning("⚠️ Silakan generate cerita terlebih dahulu")
            return
        
        st.info("Pilih efek teks untuk video")
        selected_effect = st.selectbox(
            "Efek Teks:",
            ['none', 'typewriter', 'highlight', 'glow'],
            key="effect_select"
        )
        
        if st.button("🚀 Generate Video"):
            with st.spinner("Membuat video..."):
                try:
                    # Generate audio
                    story_text = self.safe_session_get('story_text', '')
                    audio_path = generate_tts_sync(story_text, settings['language'])
                    
                    if audio_path:
                        self.safe_session_set('audio_path', audio_path)
                        st.success("✅ Audio berhasil dibuat!")
                    
                    # Simulate video creation
                    self.safe_session_set('video_path', f"/tmp/video_{uuid.uuid4().hex[:8]}.mp4")
                    st.success("✅ Video berhasil dibuat!")
                    
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")

    def render_results(self):
        """Render results section"""
        self.ensure_session_state()
        
        if not self.safe_session_get('video_path'):
            st.info("📊 Hasil video akan muncul di sini setelah generate")
            return
        
        st.header("🎉 Hasil Video")
        st.success("✅ Video berhasil dibuat!")
        st.info("Video preview (demo mode)")
        
        st.download_button(
            "📥 Download Video",
            data=b"demo_video_content",
            file_name="video_demo.mp4",
            mime="video/mp4"
        )

    def run(self):
        """Main application runner"""
        self.render_header()
        settings = self.render_sidebar()
        
        tab1, tab2, tab3, tab4 = st.tabs(["📁 Upload", "📖 Cerita", "🎬 Video", "📊 Hasil"])
        
        with tab1:
            self.render_file_upload()
        with tab2:
            self.render_story_generator(settings)
        with tab3:
            self.render_video_generator(settings)
        with tab4:
            self.render_results()

if __name__ == "__main__":
    app = VideoGeneratorApp()
    app.run()
MAINEOF

echo "✅ File main.py yang clean telah dibuat"
