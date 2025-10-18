#!/bin/bash

# AI Video Generator Setup Script
echo "🎬 AI Video Generator - Setup Script"

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 tidak terinstall. Silakan install Python 3.8 atau lebih tinggi."
    exit 1
fi

# Create virtual environment
echo "📦 Membuat virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "🔧 Mengaktifkan virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📚 Menginstall dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Check FFmpeg
echo "🎥 Mengecek FFmpeg..."
if ! command -v ffmpeg &> /dev/null; then
    echo "⚠️  FFmpeg tidak ditemukan. Silakan install FFmpeg:"
    echo "Ubuntu/Debian: sudo apt install ffmpeg"
    echo "Windows: Download dari https://ffmpeg.org/"
    echo "Mac: brew install ffmpeg"
else
    echo "✅ FFmpeg terdeteksi"
fi

# Create environment file
if [ ! -f .env ]; then
    echo "📄 Membuat file .env..."
    cp .env.example .env
    echo "⚠️  Edit file .env dengan API key OpenRouter jika diperlukan"
fi

# ✅ PERBAIKAN: Update directory creation for new structure
echo "📁 Membuat struktur folder..."
mkdir -p apps/static/assets/{audio,video,output,temp}
mkdir -p utils
mkdir -p config

echo "✅ Setup selesai!"
echo "🚀 Jalankan aplikasi dengan: python run.py"
echo "📖 Baca README.md untuk informasi lebih lanjut"
