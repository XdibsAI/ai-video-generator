#!/bin/bash

# Update method create_video utama untuk handle existing video
python3 << 'PYTHONCODE'
import re

# Baca video_editor.py
with open('utils/video_editor.py', 'r') as f:
    content = f.read()

# Cari method create_video dan update parameter
if 'def create_video(' in content:
    # Tambahkan parameter use_original_video
    old_method_def = '''    def create_video(self, media_files, audio_path, duration, video_format="short",
                     subtitle_text="", font_size=60, text_color="#FFFFFF", 
                     text_position="middle", background_music=None, music_volume=0.3,
                     mode="video", auto_subtitle=False, subtitle_language="id",
                     text_effect="none"):'''
    
    new_method_def = '''    def create_video(self, media_files, audio_path, duration, video_format="short",
                     subtitle_text="", font_size=60, text_color="#FFFFFF", 
                     text_position="middle", background_music=None, music_volume=0.3,
                     mode="video", auto_subtitle=False, subtitle_language="id",
                     text_effect="none", use_original_video=False):'''
    
    content = content.replace(old_method_def, new_method_def)
    
    # Tambahkan logika untuk existing video di dalam method
    old_video_logic = '''        # Determine video dimensions based on format
        if video_format == "short":
            width, height = 1080, 1920  # Vertical/Short format
        else:
            width, height = 1920, 1080  # Horizontal/Long format'''
    
    new_video_logic = '''        # Handle existing video mode
        if use_original_video and media_files:
            # Use the first video file as base
            video_file = next((f for f in media_files if hasattr(f, 'type') and f.type.startswith('video')), None)
            if video_file:
                # Save uploaded file to temp path
                import tempfile
                original_video_path = os.path.join(tempfile.gettempdir(), f"original_{uuid.uuid4().hex[:8]}_{video_file.name}")
                with open(original_video_path, 'wb') as f:
                    f.write(video_file.getvalue())
                
                # Add text to existing video
                result_path = self.add_text_to_existing_video(
                    original_video_path,
                    subtitle_text,
                    output_path,
                    font_size,
                    text_color,
                    text_position,
                    text_effect
                )
                
                # Cleanup temp file
                try:
                    os.remove(original_video_path)
                except:
                    pass
                
                return result_path
        
        # Determine video dimensions based on format
        if video_format == "short":
            width, height = 1080, 1920  # Vertical/Short format
        else:
            width, height = 1920, 1080  # Horizontal/Long format'''
    
    content = content.replace(old_video_logic, new_video_logic)

with open('utils/video_editor.py', 'w') as f:
    f.write(content)

print("✅ Main create_video method diupdate untuk existing video")
PYTHONCODE
