# Update settings.py dengan model Grok-4-Fast
cat > config/settings.py << 'SETTINGSEOF'
import os
import streamlit as st
from dotenv import load_dotenv

# Load environment variables dari .env file
load_dotenv()

# Try to get API key from environment variable (for Streamlit Cloud)
OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY', '')

# If not in environment, try to get from Streamlit secrets
try:
    if not OPENROUTER_API_KEY:
        OPENROUTER_API_KEY = st.secrets.get("OPENROUTER_API_KEY", "")
except:
    pass

# Fallback to empty string if still not found
if not OPENROUTER_API_KEY:
    OPENROUTER_API_KEY = ""

# OpenRouter Settings - GROK MODEL
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
DEFAULT_MODEL = "x-ai/grok-4-fast"  # ✅ Model Grok-4-Fast

# Application Settings
APP_NAME = "AI Video Generator"
APP_VERSION = "2.0.0"
MAX_VIDEO_DURATION = 300  # 5 minutes
SUPPORTED_LANGUAGES = ['id', 'en', 'es', 'fr', 'de', 'ja', 'ko', 'zh']

# TTS Settings
TTS_ENGINE = "gtts"

# Video Settings
DEFAULT_VIDEO_FORMAT = "short"
DEFAULT_FONT_SIZE = 60
DEFAULT_TEXT_COLOR = "#FFFFFF"

# Debug mode
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'

# Print debug info
if DEBUG:
    print(f"API Key loaded: {'Yes' if OPENROUTER_API_KEY else 'No'}")
    print(f"API Key length: {len(OPENROUTER_API_KEY)}")
    print(f"Using model: {DEFAULT_MODEL}")

# Fallback function untuk compatibility
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
SETTINGSEOF

echo "✅ Model telah diupdate ke Grok-4-Fast"
