from PIL import Image
import os
import uuid
import tempfile
import streamlit as st
from utils.compatibility import sanitize_filename
from utils.text_processor import text_processor
from utils.speech_to_text import speech_to_text
from utils.text_effects import get_text_effect_config  # ✅ NEW

# ... (existing imports tetap sama)

class VideoEditor:
    def __init__(self):
        self.temp_dir = tempfile.gettempdir()
    
    def create_video(self, media_files, audio_path, duration, video_format='short', 
                    subtitle_text="", font_size=60, text_color='white', 
                    text_position='middle', font_name='Arial-Bold',
                    background_music=None, music_volume=0.3,
                    mode='video', auto_subtitle=False, subtitle_language='id',
                    text_effect='none'):  # ✅ NEW: text_effect parameter
        """Create video dengan text effects"""
        
        try:
            if not MOVIEPY_AVAILABLE:
                return self._create_fallback_video(media_files, audio_path, duration, video_format)
            
            # ✅ GET TEXT EFFECT CONFIG
            effect_config = get_text_effect_config(text_effect)
            
            # Auto subtitle feature (existing)
            final_subtitle_text = subtitle_text
            if auto_subtitle and media_files and media_files[0].type.startswith('video'):
                st.info("🎤 Extracting subtitles from video...")
                transcribed_text = speech_to_text.transcribe_video(media_files[0], subtitle_language)
                if transcribed_text:
                    final_subtitle_text = transcribed_text
                    st.success(f"✅ Extracted {len(transcribed_text)} characters from video")
                    st.session_state.story_text = transcribed_text
                else:
                    st.warning("⚠️ Could not extract subtitles, using provided text")
            
            if mode == 'text_only':
                st.info("🎬 Creating TEXT-ONLY karaoke video...")
                return self._create_text_only_video(
                    audio_path, duration, video_format, final_subtitle_text,
                    font_size, text_color, text_position, background_music, music_volume,
                    text_effect  # ✅ PASS EFFECT
                )
            else:
                st.info("🎬 Starting video creation with audio synchronization...")
                return self._create_standard_video(
                    media_files, audio_path, duration, video_format,
                    final_subtitle_text, font_size, text_color, text_position,
                    background_music, music_volume, text_effect  # ✅ PASS EFFECT
                )
            
        except Exception as e:
            st.error(f"❌ Video creation failed: {str(e)}")
            import traceback
            st.error(f"Detailed error: {traceback.format_exc()}")
            return self._create_fallback_video(media_files, audio_path, duration, video_format)
    
    def _create_text_only_video(self, audio_path, duration, video_format, subtitle_text,
                               font_size, text_color, text_position, background_music, music_volume,
                               text_effect='none'):  # ✅ NEW parameter
        """Create text-only karaoke video dengan effects"""
        try:
            # Video settings
            if video_format == 'short':
                width, height = 1080, 1920  # 9:16
            else:
                width, height = 1920, 1080  # 16:9
            
            # Get effect config
            effect_config = get_text_effect_config(text_effect)
            
            # Get actual audio duration
            audio_duration = 0
            if audio_path and os.path.exists(audio_path):
                try:
                    audio_clip_test = AudioFileClip(audio_path)
                    audio_duration = audio_clip_test.duration
                    audio_clip_test.close()
                    st.info(f"🎵 Audio duration: {audio_duration:.1f}s / Target: {duration}s")
                except Exception as e:
                    st.warning(f"⚠️ Could not read audio duration: {str(e)}")
                    audio_duration = duration
            
            # Use the shorter duration between audio and target
            actual_duration = min(audio_duration, duration) if audio_duration > 0 else duration
            
            # Create solid color background (bisa diganti gradient nanti)
            background = ColorClip(size=(width, height), color=(0, 0, 0))  # Black background
            background = background.set_duration(actual_duration)
            
            final_clip = background
            
            # Add audio if available
            if audio_path and os.path.exists(audio_path):
                try:
                    audio_clip = AudioFileClip(audio_path)
                    
                    # Match audio duration to video duration
                    if audio_clip.duration > actual_duration:
                        audio_clip = audio_clip.subclip(0, actual_duration)
                        st.info("✂️ Audio trimmed to match video duration")
                    elif audio_clip.duration < actual_duration:
                        audio_clip = self._loop_audio(audio_clip, actual_duration)
                        st.info("🔁 Audio looped to match video duration")
                    
                    final_clip = final_clip.set_audio(audio_clip)
                    st.success("✅ Audio synchronized with text video")
                    
                except Exception as e:
                    st.warning(f"⚠️ Could not add audio: {str(e)}")
            
            # Add PUNCTUATION-AWARE karaoke subtitles DENGAN EFFECTS
            if subtitle_text:
                try:
                    final_clip = self._add_punctuation_aware_karaoke(
                        final_clip, subtitle_text, font_size, text_color, 
                        text_position, actual_duration, text_effect  # ✅ PASS EFFECT
                    )
                    st.success(f"✅ {effect_config['name']} karaoke added to text-only video!")
                except Exception as e:
                    st.warning(f"⚠️ Could not add karaoke: {str(e)}")
                    final_clip = self._add_normal_subtitle(final_clip, subtitle_text, font_size, text_color, text_position, text_effect)
            
            # Add background music
            if background_music and os.path.exists(background_music):
                try:
                    bg_music_clip = AudioFileClip(background_music).volumex(music_volume)
                    bg_music_clip = bg_music_clip.subclip(0, actual_duration)
                    
                    if final_clip.audio:
                        from moviepy.audio.AudioClip import CompositeAudioClip
                        final_audio = CompositeAudioClip([final_clip.audio, bg_music_clip])
                        final_clip = final_clip.set_audio(final_audio)
                    else:
                        final_clip = final_clip.set_audio(bg_music_clip)
                    st.success("✅ Background music added")
                except Exception as e:
                    st.warning(f"⚠️ Could not add background music: {str(e)}")
            
            # Export video
            output_filename = f"text_karaoke_{uuid.uuid4().hex[:8]}.mp4"
            output_path = os.path.join(self.temp_dir, sanitize_filename(output_filename))
            
            st.info("📤 Exporting text-only karaoke video...")
            
            final_clip.write_videofile(
                output_path,
                codec='libx264',
                audio_codec='aac',
                verbose=False,
                logger=None,
                fps=24,
                bitrate="1500k",
                threads=4
            )
            
            final_clip.close()
            
            st.success(f"✅ Text-only karaoke video created: {os.path.basename(output_path)}")
            return output_path
            
        except Exception as e:
            st.error(f"❌ Text-only video creation failed: {str(e)}")
            raise e

    def _add_punctuation_aware_karaoke(self, video_clip, text, font_size, text_color, text_position, audio_duration, text_effect='none'):
        """Add karaoke dengan text effects"""
        try:
            st.info("🎤 Creating punctuation-aware karaoke with effects...")
            
            # Get effect config
            effect_config = get_text_effect_config(text_effect)
            
            # Calculate position
            if text_position == 'middle':
                position = ('center', video_clip.h * 0.3)
            else:
                position = ('center', video_clip.h * 0.8)
            
            text_clips = []
            
            # Get punctuation-aware timings
            timings = text_processor.create_punctuation_aware_karaoke(text, audio_duration)
            
            st.info(f"📊 Karaoke segments: {len(timings)} | Effect: {effect_config['name']}")
            
            for i, timing in enumerate(timings):
                chunk_text = timing['text']
                start_time = timing['start_time']
                end_time = timing['end_time']
                has_punctuation = timing['has_punctuation']
                punctuation = timing['punctuation']
                
                if start_time >= audio_duration:
                    break
                    
                end_time = min(end_time, audio_duration)
                
                try:
                    # ✅ APPLY EFFECT SETTINGS
                    stroke_color = effect_config.get('stroke_color', 'black')
                    stroke_width = effect_config.get('stroke_width', 2)
                    font_color = effect_config.get('font_color', text_color)
                    
                    # Special styling untuk punctuation dengan effects
                    if has_punctuation and punctuation in ['.', '!', '?']:
                        if text_effect == 'glow':
                            font_color = effect_config.get('glow_color', '#FFD700')
                        elif text_effect == 'neon':
                            font_color = effect_config.get('neon_color', '#00FFFF')
                    
                    txt_clip = TextClip(
                        chunk_text,
                        fontsize=font_size,
                        color=font_color,
                        font='Arial-Bold',
                        stroke_color=stroke_color,
                        stroke_width=stroke_width,
                        size=(video_clip.w * 0.9, None),
                        method='caption'
                    ).set_position(position).set_start(start_time).set_duration(end_time - start_time)
                    
                    text_clips.append(txt_clip)
                    
                except Exception as e:
                    st.warning(f"⚠️ Error creating text for '{chunk_text}': {str(e)}")
                    continue
            
            if not text_clips:
                st.warning("⚠️ No text clips created, using normal subtitle")
                return self._add_normal_subtitle(video_clip, text, font_size, text_color, text_position, text_effect)
            
            st.info(f"🔄 Compositing {len(text_clips)} segments with {effect_config['name']}...")
            result = CompositeVideoClip([video_clip] + text_clips)
            
            return result
            
        except Exception as e:
            st.error(f"❌ Punctuation-aware karaoke error: {str(e)}")
            raise e

    def _add_normal_subtitle(self, video_clip, text, font_size, text_color, text_position, text_effect='none'):
        """Add normal static subtitle dengan effects"""
        try:
            # Get effect config
            effect_config = get_text_effect_config(text_effect)
            
            # Calculate position
            if text_position == 'middle':
                position = ('center', video_clip.h * 0.3)
            else:
                position = ('center', video_clip.h * 0.85)
            
            # Split text into manageable lines
            optimized_lines = text_processor.optimize_for_display(text, max_line_length=25)
            display_text = '\n'.join(optimized_lines[:3])
            
            # Apply effect settings
            stroke_color = effect_config.get('stroke_color', 'black')
            stroke_width = effect_config.get('stroke_width', 2)
            font_color = effect_config.get('font_color', text_color)
            
            # Create text clip
            txt_clip = TextClip(
                display_text,
                fontsize=font_size,
                color=font_color,
                font='Arial-Bold',
                stroke_color=stroke_color,
                stroke_width=stroke_width,
                size=(video_clip.w * 0.9, None),
                method='caption'
            )
            
            txt_clip = txt_clip.set_position(position).set_duration(video_clip.duration)
            
            result = CompositeVideoClip([video_clip, txt_clip])
            return result
            
        except Exception as e:
            st.warning(f"⚠️ Normal subtitle error: {str(e)}")
            return video_clip

    # ... (rest of existing methods remain the same)
