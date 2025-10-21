#!/bin/bash

# Backup file
cp apps/main.py apps/main.py.backup_final

# Buat file baru dengan import yang robust
cat > apps/main.py << 'PYTHONEOF'
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

# ✅ FALLBACK FUNCTIONS UNTUK DEPENDENCIES YANG BERMASALAH
def estimate_word_count(duration_seconds):
    """
    Estimate word count based on duration in seconds
    """
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

# Fallback text_effects
class FallbackTextEffects:
    def render_effects_gallery(self, selected_effect, sample_text, font_size):
        st.info("🎨 Preview Efek Teks (Fallback Mode)")
        st.write(f"**Teks:** {sample_text}")
        st.write(f"**Font Size:** {font_size}px")
        st.write("**Efek Terpilih:** Standar")
    
    def get_effect_display_info(self, effect_name):
        return "Efek Standar", "Teks akan ditampilkan dengan efek standar"

# Fallback story_generator  
class FallbackStoryGenerator:
    def __init__(self):
        self.api_key = None
    
    def generate_stories(self, niche, duration_seconds, style, language, user_description=""):
        return [
            f"Ini adalah cerita fallback 1 tentang {niche}",
            f"Ini adalah cerita fallback 2 tentang {niche}", 
            f"Ini adalah cerita fallback 3 tentang {niche}"
        ]
    
    def _estimate_word_count(self, duration_seconds):
        return estimate_word_count(duration_seconds)

# Fallback functions lainnya
def generate_tts_sync(text, language):
    return f"/tmp/fallback_audio_{uuid.uuid4().hex[:8]}.mp3"

def estimate_audio_duration(text, language):
    return len(text.split()) * 0.5

class FallbackVideoEditor:
    def create_video(self, *args, **kwargs):
        return f"/tmp/fallback_video_{uuid.uuid4().hex[:8]}.mp4"

class FallbackContentOptimizer:
    def optimize_content(self, text, niche, language):
        return {
            'title': f'Video tentang {niche}',
            'description': text[:100] + '...',
            'hooks': ['Video menarik untuk ditonton!'],
            'hashtags': [niche, 'video', 'content'],
            'optimal_posting_times': ['08:00', '12:00', '18:00']
        }

class FallbackSpeechToText:
    def transcribe_video(self, video_file, language):
        return "Ini adalah teks fallback dari transkripsi audio."

# ✅ INITIALIZE DENGAN FALLBACK VALUES
MOVIEPY_AVAILABLE = False
TTS_AVAILABLE = False
story_generator = FallbackStoryGenerator()
text_effects = FallbackTextEffects()
video_editor = FallbackVideoEditor()
content_optimizer = FallbackContentOptimizer()
speech_to_text = FallbackSpeechToText()
OPENROUTER_API_KEY = None

# ✅ TRY TO IMPORT REAL DEPENDENCIES
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

try:
    # Try to import from .env via settings
    from config.settings import *
    
    # Update story_generator dengan API key yang benar
    if OPENROUTER_API_KEY and OPENROUTER_API_KEY != "your_actual_openrouter_api_key_here":
        story_generator.api_key = OPENROUTER_API_KEY
        st.sidebar.success("✅ API Key Loaded from Settings")
    else:
        st.sidebar.warning("⚠️ API Key not configured in settings")
        
except ImportError as e:
    st.error(f"❌ Settings import error: {e}")

# ✅ TRY TO IMPORT UTILS MODULES
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
    from utils.video_editor import video_editor as real_video_editor  
    video_editor = real_video_editor
except ImportError:
    st.warning("⚠️ Using fallback video_editor")

try:
    from utils.content_optimizer import content_optimizer as real_content_optimizer
    content_optimizer = real_content_optimizer
except ImportError:
    st.warning("⚠️ Using fallback content_optimizer")

try:
    from utils.speech_to_text import speech_to_text as real_speech_to_text
    speech_to_text = real_speech_to_text
except ImportError:
    st.warning("⚠️ Using fallback speech_to_text")

try:
    from utils.tts_handler import generate_tts_sync as real_generate_tts_sync
    from utils.tts_handler import estimate_audio_duration as real_estimate_audio_duration
    generate_tts_sync = real_generate_tts_sync
    estimate_audio_duration = real_estimate_audio_duration
except ImportError:
    st.warning("⚠️ Using fallback TTS functions")

# Custom CSS (tetap sama)
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
    .karaoke-info {
        background: linear-gradient(45deg, #667eea, #764ba2);
        color: white;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .warning-box {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 1rem 0;
    }
    .effect-preview {
        border: 2px solid #e0e0e0;
        border-radius: 10px;
        padding: 20px;
        margin: 10px;
        text-align: center;
        background: #f9f9f9;
    }
</style>
""", unsafe_allow_html=True)

PYTHONEOF

# Tambahkan bagian class VideoGeneratorApp dan seterusnya
tail -n +170 apps/main.py.backup_final >> apps/main.py

echo "✅ Semua import telah diperbaiki dengan fallback system!"
