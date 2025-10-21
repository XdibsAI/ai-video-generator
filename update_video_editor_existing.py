#!/bin/bash

# Update video creation untuk handle existing video mode
python3 << 'PYTHONCODE'
import re

with open('apps/main.py', 'r') as f:
    content = f.read()

# Update bagian video creation untuk existing video
old_video_creation = '''                # ✅ USE THE SELECTED MODE dengan auto-subtitle dan effects
                video_path = video_editor.create_video(
                    media_files=st.session_state.uploaded_files,
                    audio_path=audio_path,
                    duration=settings['duration'],
                    video_format=settings['video_format'],
                    subtitle_text=st.session_state.story_text,
                    font_size=settings['font_size'],
                    text_color=settings['text_color'],
                    text_position=settings['text_position'],
                    background_music=st.session_state.background_music_path,
                    music_volume=settings['music_volume'],
                    mode=video_mode,
                    auto_subtitle=auto_subtitle,
                    subtitle_language=settings['language'],
                    text_effect=selected_effect
                )'''

new_video_creation = '''                # ✅ USE THE SELECTED MODE dengan auto-subtitle dan effects
                video_path = video_editor.create_video(
                    media_files=st.session_state.uploaded_files,
                    audio_path=audio_path,
                    duration=settings['duration'],
                    video_format=settings['video_format'],
                    subtitle_text=st.session_state.story_text,
                    font_size=settings['font_size'],
                    text_color=settings['text_color'],
                    text_position=settings['text_position'],
                    background_music=st.session_state.background_music_path,
                    music_volume=settings['music_volume'],
                    mode=video_mode,
                    auto_subtitle=auto_subtitle,
                    subtitle_language=settings['language'],
                    text_effect=selected_effect,
                    use_original_video=(video_mode == 'add_text_to_video')
                )'''

content = content.replace(old_video_creation, new_video_creation)

# Update button text berdasarkan mode
old_button_text = '''        generate_video_clicked = st.button("🚀 Generate Video dengan Karaoke", 
                                         use_container_width=True, 
                                         type="primary",
                                         key="generate_video_btn")'''

new_button_text = '''        # Dynamic button text based on mode
        button_texts = {
            'add_text_to_video': "🚀 Tambah Teks ke Video + Generate",
            'video': "🚀 Generate Video Baru dengan Karaoke", 
            'text_only': "🚀 Generate Teks Karaoke Only"
        }
        
        generate_video_clicked = st.button(button_texts.get(video_mode, "🚀 Generate Video"), 
                                         use_container_width=True, 
                                         type="primary",
                                         key="generate_video_btn")'''

content = content.replace(old_button_text, new_button_text)

with open('apps/main.py', 'w') as f:
    f.write(content)

print("✅ Video editor diupdate untuk handle existing video")
PYTHONCODE
