"""
Compatibility utilities for file handling and system compatibility
"""
import os
import re
import platform
import streamlit as st

def sanitize_filename(filename):
    """
    Sanitize filename to be safe for all operating systems
    """
    # Remove or replace invalid characters
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    # Remove leading/trailing spaces and dots
    filename = filename.strip(' .')
    
    # Limit length
    if len(filename) > 200:
        name, ext = os.path.splitext(filename)
        filename = name[:200-len(ext)] + ext
    
    # Ensure filename is not empty
    if not filename:
        filename = "unnamed_file"
    
    return filename

def get_system_info():
    """
    Get system information for debugging
    """
    return {
        'platform': platform.system(),
        'platform_release': platform.release(),
        'platform_version': platform.version(),
        'architecture': platform.architecture(),
        'processor': platform.processor(),
        'python_version': platform.python_version()
    }

def check_ffmpeg_available():
    """
    Check if FFmpeg is available in the system
    """
    try:
        import subprocess
        result = subprocess.run(['ffmpeg', '-version'], 
                              capture_output=True, text=True, timeout=5)
        return result.returncode == 0
    except:
        return False

def get_video_codecs():
    """
    Get available video codecs information
    """
    try:
        import subprocess
        result = subprocess.run(['ffmpeg', '-codecs'], 
                              capture_output=True, text=True, timeout=10)
        return result.stdout
    except:
        return "FFmpeg not available"

def safe_file_delete(filepath):
    """
    Safely delete a file with error handling
    """
    try:
        if filepath and os.path.exists(filepath):
            os.remove(filepath)
            return True
    except Exception as e:
        st.warning(f"Could not delete file {filepath}: {e}")
        return False
    return False

def get_temp_directory():
    """
    Get safe temporary directory
    """
    temp_dir = os.path.join(os.path.expanduser("~"), ".streamlit_tts_temp")
    os.makedirs(temp_dir, exist_ok=True)
    return temp_dir


def estimate_word_count(duration_seconds):
    """
    Estimate word count based on duration in seconds
    Consistent with story_generator implementation
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

