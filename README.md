# 🎬 AI Video Generator

Aplikasi web untuk menghasilkan video otomatis dengan AI menggunakan Streamlit.

## ✨ Fitur

- 🎯 Generate cerita otomatis berdasarkan niche
- 🔊 Text-to-Speech dengan multiple engine
- 🎨 Video editing dengan transisi dan efek
- 📝 Subtitle karaoke yang sinkron
- 📊 Optimasi konten untuk platform sosial
- 🧹 Auto-cleanup file temporary
- 📱 Responsive UI

## 🚀 Instalasi

1. **Clone repository**
```bash
git clone <repository-url>
cd ai-video-generator
1. Install dependencies

```bash
pip install -r requirements.txt
```

1. Install FFmpeg

· Ubuntu/Debian: sudo apt install ffmpeg
· Windows: Download dari ffmpeg.org
· Mac: brew install ffmpeg

1. Setup environment

```bash
cp .env.example .env
# Edit .env dengan API key OpenRouter jika ada
```

1. Jalankan aplikasi

```bash
python run.py
# atau
streamlit run app/main.py --server.port 8505
```

📁 Struktur Project

```
ai-video-generator/
├── app/
│   ├── main.py                 # Main Streamlit app
│   ├── utils/                  # Utility modules
│   │   ├── compatibility.py    # Compatibility fixes
│   │   ├── story_generator.py  # AI story generation
│   │   ├── tts_handler.py      # Text-to-speech
│   │   ├── video_editor.py     # Video processing
│   │   ├── content_optimizer.py # Content optimization
│   │   └── cleanup.py          # File cleanup
│   └── static/                 # Static assets
│       └── assets/
│           ├── audio/          # Generated audio files
│           ├── video/          # Uploaded videos
│           ├── output/         # Final videos
│           └── temp/           # Temporary files
├── config/
│   └── settings.py            # App configuration
├── tests/                     # Test files
├── requirements.txt           # Dependencies
├── .env.example              # Environment template
└── README.md                 # Documentation
```

⚙️ Konfigurasi

Edit file .env:

```env
OPENROUTER_API_KEY=your_api_key_here
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
DEFAULT_MODEL=x-ai/grok-4-fast
MAX_VIDEO_DURATION=180
TEMP_FILE_TIMEOUT=3600
```

🎮 Penggunaan

1. Upload Media: Pilih gambar atau video
2. Pilih Pengaturan: Tentukan niche, bahasa, durasi, dll.
3. Generate Cerita: AI akan membuat narasi otomatis
4. Edit Cerita: Sesuaikan teks sesuai keinginan
5. Generate Video: Proses pembuatan video otomatis
6. Download: Ambil hasil video dan konten optimasi

🔧 Teknologi

· Frontend: Streamlit
· Video Processing: MoviePy, FFmpeg
· AI Text Generation: OpenRouter API
· Text-to-Speech: edge-tts, gTTS
· Image Processing: Pillow

📊 Spesifikasi

· RAM: Optimal untuk VPS 4GB
· Storage: Auto-cleanup setiap 1 jam
· Output: MP4 (H.264 + AAC)
· Resolusi: 720p maksimal
· Format: 9:16 (Short) & 16:9 (Long)

🐛 Troubleshooting

Error FFmpeg tidak ditemukan:

· Pastikan FFmpeg terinstall dan ada di PATH

Error memory:

· Kurangi jumlah file upload
· Kurangi durasi video

Error API:

· Cek koneksi internet
· Verifikasi API key di .env

📄 Lisensi

MIT License
