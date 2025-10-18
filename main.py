import streamlit as st
import os
import asyncio
import time
import sys
from datetime import datetime

# ✅ PERBAIKAN IMPORT: Add project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import *
from utils.story_generator import story_generator
from utils.tts_handler import generate_tts_sync
from utils.video_editor import video_editor
from utils.content_optimizer import content_optimizer
from utils.cleanup import cleanup_manager
from utils.compatibility import check_ffmpeg, estimate_word_count

# ... (rest of the main.py content remains the same)

# Add this import at the top of main.py with other imports
from utils.ffmpeg_checker import check_ffmpeg, setup_ffmpeg_warning

# Alternatively, if you want to replace the existing check_ffmpeg call, 
# find this section in your main.py and replace it:

def run(self):
    # Check dependencies
    if not check_ffmpeg():
        setup_ffmpeg_warning()
        # Continue anyway for basic functionality
        st.info("Basic TTS functionality will work, but video features are limited.")
    
    # Rest of your code...
