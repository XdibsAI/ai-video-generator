from PIL import Image
import os
import uuid
import tempfile
import streamlit as st
from utils.compatibility import sanitize_filename
from utils.text_processor import text_processor
from utils.speech_to_text import speech_to_text  # ✅ NEW

# ... (existing imports and compatibility code tetap sama)

class VideoEditor:
    def __init__(self):
        self.temp_dir = tempfile.gettempdir()
    
    def create_video(self, media_files, audio_path, duration, video_format='short', 
                    subtitle_text="", font_size=60, text_color='white', 
                    text_position='middle', font_name='Arial-Bold',
                    background_music=None, music_volume=0.3,
                    mode='video', auto_subtitle=False, subtitle_language='id'):  # ✅ NEW parameters
        """Create video dengan optional auto-subtitle"""
        
        try:
            if not MOVIEPY_AVAILABLE:
                return self._create_fallback_video(media_files, audio_path, duration, video_format)
            
            # ✅ AUTO SUBTITLE FEATURE
            final_subtitle_text = subtitle_text
            if auto_subtitle and media_files and media_files[0].type.startswith('video'):
                st.info("🎤 Extracting subtitles from video...")
                transcribed_text = speech_to_text.transcribe_video(media_files[0], subtitle_language)
                if transcribed_text:
                    final_subtitle_text = transcribed_text
                    st.success(f"✅ Extracted {len(transcribed_text)} characters from video")
                    # Update session state dengan transcribed text
                    st.session_state.story_text = transcribed_text
                else:
                    st.warning("⚠️ Could not extract subtitles, using provided text")
            
            if mode == 'text_only':
                st.info("🎬 Creating TEXT-ONLY karaoke video...")
                return self._create_text_only_video(
                    audio_path, duration, video_format, final_subtitle_text,
                    font_size, text_color, text_position, background_music, music_volume
                )
            else:
                st.info("🎬 Starting video creation with audio synchronization...")
                return self._create_standard_video(
                    media_files, audio_path, duration, video_format,
                    final_subtitle_text, font_size, text_color, text_position,
                    background_music, music_volume
                )
            
        except Exception as e:
            st.error(f"❌ Video creation failed: {str(e)}")
            import traceback
            st.error(f"Detailed error: {traceback.format_exc()}")
            return self._create_fallback_video(media_files, audio_path, duration, video_format)

    # ... (rest of the existing methods remain the same)
