#!/usr/bin/env python3
"""
Run script for AI Video Generator
"""

import os
import subprocess
import sys

def check_dependencies():
    """Check if all dependencies are installed"""
    try:
        import streamlit
        import moviepy
        import PIL
        import requests
        print("✅ All dependencies are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        return False

def main():
    """Run the Streamlit application"""
    print("🎬 AI Video Generator - Starting...")
    
    if not check_dependencies():
        print("💡 Installing dependencies...")
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    
    # ✅ PERBAIKAN: Update path to apps/main.py
    print("🚀 Launching application...")
    os.system("streamlit run apps/main.py --server.port 8505")

if __name__ == "__main__":
    main()
