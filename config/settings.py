import os
from dotenv import load_dotenv

load_dotenv()

# API Configuration
OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')
OPENROUTER_BASE_URL = os.getenv('OPENROUTER_BASE_URL', 'https://openrouter.ai/api/v1')
DEFAULT_MODEL = os.getenv('DEFAULT_MODEL', 'x-ai/grok-4-fast')

# App Configuration
MAX_VIDEO_DURATION = int(os.getenv('MAX_VIDEO_DURATION', 180))
TEMP_FILE_TIMEOUT = int(os.getenv('TEMP_FILE_TIMEOUT', 3600))
PORT = 8505

# ✅ PERBAIKAN PATH: Update BASE_DIR untuk struktur baru
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_DIR = os.path.join(BASE_DIR, 'apps', 'static')
AUDIO_DIR = os.path.join(STATIC_DIR, 'assets', 'audio')
VIDEO_DIR = os.path.join(STATIC_DIR, 'assets', 'video')
OUTPUT_DIR = os.path.join(STATIC_DIR, 'assets', 'output')
TEMP_DIR = os.path.join(STATIC_DIR, 'assets', 'temp')

# Create directories if they don't exist
for directory in [AUDIO_DIR, VIDEO_DIR, OUTPUT_DIR, TEMP_DIR]:
    os.makedirs(directory, exist_ok=True)

# Video Configuration
VIDEO_SETTINGS = {
    'short': {'width': 1080, 'height': 1920, 'aspect_ratio': '9:16'},
    'long': {'width': 1920, 'height': 1080, 'aspect_ratio': '16:9'}
}

# Narration Settings
NICHE_OPTIONS = [
    "Fakta Menarik", "Motivasi", "Humor", "Petualangan", 
    "Pendidikan", "Teknologi", "Sejarah", "Sains", "Bisnis"
]

LANGUAGE_OPTIONS = [
    {"code": "id", "name": "Indonesia"},
    {"code": "en", "name": "English"},
    {"code": "es", "name": "Spanish"},
    {"code": "fr", "name": "French"}
]

DURATION_OPTIONS = [
    {"seconds": 30, "label": "30 Detik", "word_range": (50, 80)},
    {"seconds": 60, "label": "1 Menit", "word_range": (100, 150)},
    {"seconds": 180, "label": "3 Menit", "word_range": (300, 400)}
]

STYLE_OPTIONS = ["Serius", "Lucu", "Inspiratif", "Dramatis", "Informal"]

# Font Settings
FONT_OPTIONS = [
    {"name": "Arial", "file": "arial.ttf"},
    {"name": "Roboto", "file": "Roboto-Regular.ttf"},
    {"name": "Montserrat", "file": "Montserrat-Regular.ttf"},
    {"name": "Open Sans", "file": "OpenSans-Regular.ttf"}
]

# ✅ PERBAIKAN: Color options dengan nama dan preview
COLOR_OPTIONS = [
    {"name": "Putih", "value": "#FFFFFF", "preview": "⚪"},
    {"name": "Emas", "value": "#FFD700", "preview": "🟡"}, 
    {"name": "Hijau Terang", "value": "#00FF00", "preview": "🟢"},
    {"name": "Merah Oranye", "value": "#FF4500", "preview": "🔴"},
    {"name": "Biru Dodger", "value": "#1E90FF", "preview": "🔵"},
    {"name": "Merah Muda", "value": "#FF69B4", "preview": "🌸"},
    {"name": "Hijau Lime", "value": "#32CD32", "preview": "💚"},
    {"name": "Oranye", "value": "#FFA500", "preview": "🟠"}
]

TEXT_POSITIONS = [
    {"value": "middle", "label": "Tengah"},
    {"value": "bottom", "label": "Bawah"}
]
