"""
Streamlit Cloud Entry Point
This file redirects to the main app in apps/ folder
"""
import sys
import os

# Add apps directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'apps'))

# Import and run the main app
from main import app

if __name__ == "__main__":
    app.run()
