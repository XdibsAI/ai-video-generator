#!/bin/bash

# Backup file
cp apps/main.py apps/main.py.backup

# Baca file dan split pada class definition
content=$(cat apps/main.py)

# Split pada class VideoGeneratorApp
before_class=$(echo "$content" | sed -n '/class VideoGeneratorApp:/q;p')
class_and_after=$(echo "$content" | sed -n '/class VideoGeneratorApp:/,$p')

# Buat file baru dengan fungsi tambahan
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

# ✅ IMPORT DENGAN FALLBACK HANDLING
MOVIEPY_AVAILABLE = False
TTS_AVAILABLE = False

try:
    # Try to import main dependencies
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
    from config.settings import *
    from utils.story_generator import story_generator
    from utils.tts_handler import generate_tts_sync, estimate_audio_duration
    from utils.video_editor import video_editor
    from utils.content_optimizer import content_optimizer
    from utils.cleanup import cleanup_manager
    from utils.compatibility import estimate_word_count  # ✅ FIX: Import yang benar
    from utils.session_manager import setup_persistent_session, show_session_info
    from utils.text_processor import text_processor
    from utils.speech_to_text import speech_to_text
    from utils.text_effects import text_effects
    
    # ✅ AUTO LOAD API KEY
    if OPENROUTER_API_KEY:
        story_generator.api_key = OPENROUTER_API_KEY
        st.sidebar.success("✅ API Key Loaded")
    else:
        st.sidebar.warning("⚠️ API Key not configured")
        
except ImportError as e:
    st.error(f"❌ Import Error: {e}")

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

# ✅ FALLBACK FUNCTION untuk estimate_word_count
def estimate_word_count(duration_seconds):
    """
    Estimate word count based on duration in seconds
    Fallback function if import from utils.compatibility fails
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

PYTHONEOF

# Tambahkan bagian class dan seterusnya
echo "$class_and_after" >> apps/main.py

echo "✅ Fungsi estimate_word_count telah ditambahkan ke apps/main.py"
