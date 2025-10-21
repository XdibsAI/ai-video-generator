#!/bin/bash

# Comment out imports yang bermasalah
sed -i 's/from utils.compatibility import estimate_word_count/# from utils.compatibility import estimate_word_count  # ❌ Commented out due to import issues/' apps/main.py

# Juga comment out text_effects jika masih error
sed -i 's/from utils.text_effects import text_effects/# from utils.text_effects import text_effects  # ❌ Commented out/' apps/main.py

echo "✅ Problematic imports commented out"
