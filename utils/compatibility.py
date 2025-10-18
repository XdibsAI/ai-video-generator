from PIL import Image
import streamlit as st
import subprocess
import os
import re

# Compatibility fix for Pillow >=10
if not hasattr(Image, 'ANTIALIAS'):
    Image.ANTIALIAS = Image.Resampling.LANCZOS

def check_ffmpeg():
    """Check if FFmpeg is available"""
    try:
        result = subprocess.run(['ffmpeg', '-version'], 
                              capture_output=True, 
                              text=True, 
                              check=True,
                              timeout=10)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        st.error("""
        ❌ FFmpeg tidak ditemukan. Silakan install FFmpeg terlebih dahulu.
        
        **Ubuntu/Debian:**
        ```bash
        sudo apt update && sudo apt install ffmpeg
        ```
        """)
        return False

def sanitize_filename(filename):
    """Sanitize filename to prevent path traversal"""
    filename = re.sub(r'[^a-zA-Z0-9_.-]', '_', filename)
    return filename[:255]

def format_duration(seconds):
    """Format duration in seconds to human readable format"""
    if seconds < 60:
        return f"{seconds} detik"
    elif seconds < 3600:
        minutes = seconds // 60
        return f"{minutes} menit"
    else:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        return f"{hours} jam {minutes} menit"

def estimate_word_count(duration_seconds):
    """Estimate word count based on duration"""
    if duration_seconds == 30:
        return (50, 80)
    elif duration_seconds == 60:
        return (100, 150)
    elif duration_seconds == 90:
        return (150, 200)
    elif duration_seconds == 180:
        return (300, 400)
    else:
        words_per_second = 2.5
        estimated_words = int(duration_seconds * words_per_second)
        return (estimated_words - 20, estimated_words + 20)
