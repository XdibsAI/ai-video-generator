"""
FFmpeg availability checker and utilities
"""
import os
import subprocess
import streamlit as st
import logging

logger = logging.getLogger(__name__)

def check_ffmpeg():
    """
    Check if FFmpeg is available in the system PATH
    Returns True if available, False otherwise
    """
    try:
        result = subprocess.run(['ffmpeg', '-version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            logger.info("FFmpeg is available")
            return True
        else:
            logger.warning("FFmpeg check returned non-zero exit code")
            return False
    except FileNotFoundError:
        logger.warning("FFmpeg not found in system PATH")
        return False
    except subprocess.TimeoutExpired:
        logger.warning("FFmpeg check timed out")
        return False
    except Exception as e:
        logger.error(f"Error checking FFmpeg: {e}")
        return False

def get_ffmpeg_info():
    """
    Get detailed FFmpeg information
    """
    try:
        # Get version
        version_result = subprocess.run(['ffmpeg', '-version'], 
                                      capture_output=True, text=True, timeout=10)
        
        # Get codecs
        codecs_result = subprocess.run(['ffmpeg', '-codecs'], 
                                     capture_output=True, text=True, timeout=10)
        
        # Get formats
        formats_result = subprocess.run(['ffmpeg', '-formats'], 
                                      capture_output=True, text=True, timeout=10)
        
        info = {
            'available': version_result.returncode == 0,
            'version': version_result.stdout.split('\n')[0] if version_result.returncode == 0 else "Not available",
            'codecs_available': codecs_result.returncode == 0,
            'formats_available': formats_result.returncode == 0
        }
        
        return info
    except Exception as e:
        logger.error(f"Error getting FFmpeg info: {e}")
        return {'available': False, 'error': str(e)}

def check_ffmpeg_codecs():
    """
    Check if essential codecs are available
    """
    essential_codecs = ['libx264', 'aac', 'mp3']
    available_codecs = []
    
    try:
        result = subprocess.run(['ffmpeg', '-codecs'], 
                              capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            output = result.stdout.lower()
            for codec in essential_codecs:
                if codec in output:
                    available_codecs.append(codec)
            
            return available_codecs
        else:
            return []
    except Exception as e:
        logger.error(f"Error checking codecs: {e}")
        return []

def install_ffmpeg_instructions():
    """
    Return platform-specific FFmpeg installation instructions
    """
    import platform
    
    system = platform.system().lower()
    
    instructions = {
        'linux': """
        **Linux Installation:**
        - Ubuntu/Debian: `sudo apt update && sudo apt install ffmpeg`
        - CentOS/RHEL: `sudo yum install ffmpeg` or `sudo dnf install ffmpeg`
        - Arch: `sudo pacman -S ffmpeg`
        - Or download from: https://ffmpeg.org/download.html
        """,
        'darwin': """
        **macOS Installation:**
        - Using Homebrew: `brew install ffmpeg`
        - Using MacPorts: `sudo port install ffmpeg`
        - Or download from: https://ffmpeg.org/download.html
        """,
        'windows': """
        **Windows Installation:**
        1. Download from: https://www.gyan.dev/ffmpeg/builds/
        2. Extract to C:\\\\ffmpeg
        3. Add C:\\\\ffmpeg\\\\bin to your system PATH
        4. Restart your terminal/IDE
        """
    }
    
    return instructions.get(system, """
    **General Installation:**
    Visit https://ffmpeg.org/download.html for platform-specific instructions
    """)

def setup_ffmpeg_warning():
    """
    Display FFmpeg warning with installation instructions
    """
    st.warning("""
    ⚠️ **FFmpeg Not Found**
    
    FFmpeg is required for video processing features. Some functionality may be limited.
    """)
    
    with st.expander("📋 FFmpeg Installation Instructions"):
        st.markdown(install_ffmpeg_instructions())
        
        st.markdown("""
        **After installation:**
        1. Restart this application
        2. Verify installation by running `ffmpeg -version` in your terminal
        """)

def validate_ffmpeg_setup():
    """
    Comprehensive FFmpeg validation
    Returns tuple (is_available, warnings)
    """
    is_available = check_ffmpeg()
    warnings = []
    
    if not is_available:
        warnings.append("FFmpeg not found in system PATH")
        return False, warnings
    
    # Check essential codecs
    available_codecs = check_ffmpeg_codecs()
    essential_codecs = ['libx264', 'aac']
    
    for codec in essential_codecs:
        if codec not in available_codecs:
            warnings.append(f"Essential codec '{codec}' not available")
    
    return True, warnings

# Create a simple alias for the main check function
def is_ffmpeg_available():
    """Simple alias for check_ffmpeg"""
    return check_ffmpeg()
