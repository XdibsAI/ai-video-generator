from PIL import Image
import os
import uuid
import tempfile
import streamlit as st
from utils.compatibility import sanitize_filename
from utils.text_processor import text_processor
from utils.speech_to_text import speech_to_text
from utils.text_effects import get_text_effect_config
from datetime import datetime

# Compatibility fix for Pillow >=10
if not hasattr(Image, 'ANTIALIAS'):
    Image.ANTIALIAS = Image.Resampling.LANCZOS

# Try to import MoviePy with multiple fallbacks
MOVIEPY_AVAILABLE = False
try:
    from moviepy.editor import VideoFileClip, ImageClip, concatenate_videoclips, CompositeVideoClip, AudioFileClip, TextClip, ColorClip
    from moviepy.audio.AudioClip import CompositeAudioClip, concatenate_audioclips
    MOVIEPY_AVAILABLE = True
except ImportError as e:
    st.warning(f"⚠️ MoviePy not available: {e}")

class VideoEditor:
    def __init__(self):
        self.temp_dir = tempfile.gettempdir()

    def create_video(self, media_files, audio_path, duration, video_format='short',
                    subtitle_text="", font_size=60, text_color='white',
                    text_position='middle', font_name='Arial-Bold',
                    background_music=None, music_volume=0.3,
                    mode='video', auto_subtitle=False, subtitle_language='id',
                    text_effect='none'):
        """Create video with text effects"""
        try:
            if not MOVIEPY_AVAILABLE:
                return self._create_fallback_video(media_files, audio_path, duration, video_format)

            # Get text effect config
            effect_config = get_text_effect_config(text_effect)

            # Auto subtitle feature
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
                    text_effect
                )
            else:
                st.info("🎬 Starting video creation with audio synchronization...")
                return self._create_standard_video(
                    media_files, audio_path, duration, video_format,
                    final_subtitle_text, font_size, text_color, text_position,
                    background_music, music_volume, text_effect
                )

        except Exception as e:
            st.error(f"❌ Video creation failed: {str(e)}")
            import traceback
            st.error(f"Detailed error: {traceback.format_exc()}")
            return self._create_fallback_video(media_files, audio_path, duration, video_format)

    def _create_text_only_video(self, audio_path, duration, video_format, subtitle_text,
                               font_size, text_color, text_position, background_music, music_volume,
                               text_effect='none'):
        """Create text-only karaoke video with effects"""
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

            # Create solid color background
            background = ColorClip(size=(width, height), color=(0, 0, 0))
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

            # Add punctuation-aware karaoke subtitles with effects
            if subtitle_text:
                try:
                    final_clip = self._add_punctuation_aware_karaoke(
                        final_clip, subtitle_text, font_size, text_color,
                        text_position, actual_duration, text_effect
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

    def _create_standard_video(self, media_files, audio_path, duration, video_format,
                              subtitle_text, font_size, text_color, text_position,
                              background_music, music_volume, text_effect='none'):
        """Create standard video with media files"""
        # Video settings
        if video_format == 'short':
            width, height = 1080, 1920
        else:
            width, height = 1920, 1080

        clips = []
        temp_files = []

        # Process each media file
        for media_file in media_files:
            try:
                # Save uploaded file temporarily
                temp_path = os.path.join(self.temp_dir, f"temp_{uuid.uuid4().hex[:8]}_{media_file.name}")
                with open(temp_path, 'wb') as f:
                    f.write(media_file.getvalue())
                temp_files.append(temp_path)

                # Create clip based on file type
                if media_file.type.startswith('video'):
                    clip = VideoFileClip(temp_path)
                    clip_duration = min(10, clip.duration)
                    clip = clip.subclip(0, clip_duration)
                else:
                    clip = ImageClip(temp_path)
                    clip_duration = 5
                    clip = clip.set_duration(clip_duration)

                # Resize to target dimensions
                clip = clip.resize(newsize=(width, height))
                clips.append(clip)

            except Exception as e:
                st.warning(f"⚠️ Skipped {media_file.name}: {str(e)}")
                continue

        if not clips:
            st.error("❌ No valid media files processed")
            return self._create_fallback_video(media_files, audio_path, duration, video_format)

        # Create final video clip
        if len(clips) == 1:
            final_clip = clips[0]
        else:
            final_clip = concatenate_videoclips(clips, method="compose")

        # Get actual audio duration
        audio_duration = 0
        if audio_path and os.path.exists(audio_path):
            try:
                audio_clip_test = AudioFileClip(audio_path)
                audio_duration = audio_clip_test.duration
                audio_clip_test.close()
                st.info(f"🎵 Audio duration: {audio_duration:.1f}s / Video target: {duration}s")
            except Exception as e:
                st.warning(f"⚠️ Could not read audio duration: {str(e)}")
                audio_duration = duration

        # Adjust video duration based on audio
        if audio_duration > 0:
            actual_duration = min(audio_duration, duration)

            if final_clip.duration > actual_duration:
                final_clip = final_clip.subclip(0, actual_duration)
            elif final_clip.duration < actual_duration:
                final_clip = self._loop_clip(final_clip, actual_duration)

            st.info(f"📊 Using synchronized duration: {actual_duration:.1f}s")
        else:
            if final_clip.duration > duration:
                final_clip = final_clip.subclip(0, duration)
            elif final_clip.duration < duration:
                final_clip = self._loop_clip(final_clip, duration)

        # Add audio if available
        final_audio_duration = final_clip.duration
        if audio_path and os.path.exists(audio_path):
            try:
                audio_clip = AudioFileClip(audio_path)

                if audio_clip.duration > final_audio_duration:
                    audio_clip = audio_clip.subclip(0, final_audio_duration)
                    st.info("✂️ Audio trimmed to match video duration")
                elif audio_clip.duration < final_audio_duration:
                    audio_clip = self._loop_audio(audio_clip, final_audio_duration)
                    st.info("🔁 Audio looped to match video duration")

                final_clip = final_clip.set_audio(audio_clip)
                st.success("✅ Audio synchronized with video")

            except Exception as e:
                st.warning(f"⚠️ Could not add audio: {str(e)}")
                final_audio_duration = final_clip.duration
        else:
            final_audio_duration = final_clip.duration

        # Add punctuation-aware karaoke subtitles
        if subtitle_text:
            try:
                final_clip = self._add_punctuation_aware_karaoke(
                    final_clip, subtitle_text, font_size, text_color,
                    text_position, final_audio_duration, text_effect
                )
                st.success("✅ Punctuation-aware karaoke added!")
            except Exception as e:
                st.warning(f"⚠️ Could not add karaoke: {str(e)}")
                final_clip = self._add_normal_subtitle(final_clip, subtitle_text, font_size, text_color, text_position, text_effect)

        # Add background music
        if background_music and os.path.exists(background_music):
            try:
                bg_music_clip = AudioFileClip(background_music).volumex(music_volume)
                bg_music_clip = bg_music_clip.subclip(0, final_audio_duration)

                if final_clip.audio:
                    final_audio = CompositeAudioClip([final_clip.audio, bg_music_clip])
                    final_clip = final_clip.set_audio(final_audio)
                else:
                    final_clip = final_clip.set_audio(bg_music_clip)
                st.success("✅ Background music added")
            except Exception as e:
                st.warning(f"⚠️ Could not add background music: {str(e)}")

        # Export video
        output_filename = f"video_{uuid.uuid4().hex[:8]}.mp4"
        output_path = os.path.join(self.temp_dir, sanitize_filename(output_filename))

        st.info("📤 Exporting synchronized video...")

        final_clip.write_videofile(
            output_path,
            codec='libx264',
            audio_codec='aac',
            verbose=False,
            logger=None,
            fps=15,
            bitrate="1500k",
            threads=4
        )

        # Cleanup
        self._cleanup_clips(clips + [final_clip], temp_files)

        st.success(f"✅ Synchronized video created: {os.path.basename(output_path)}")
        return output_path

    def _loop_audio(self, audio_clip, target_duration):
        """Loop audio to match target duration"""
        loops_needed = int(target_duration / audio_clip.duration) + 1
        clips = [audio_clip] * loops_needed
        looped_audio = concatenate_audioclips(clips)
        return looped_audio.subclip(0, target_duration)

    def _add_punctuation_aware_karaoke(self, video_clip, text, font_size, text_color, text_position, audio_duration, text_effect='none'):
        """Add punctuation-aware karaoke with text effects"""
        try:
            st.info(f"🎤 Creating punctuation-aware karaoke with {text_effect} effect...")

            # Get effect config with fallback for invalid effect
            effect_config = get_text_effect_config(text_effect)
            if not effect_config:
                st.warning(f"⚠️ Invalid text effect '{text_effect}', using default settings")
                effect_config = get_text_effect_config('none')

            # Calculate position based on video dimensions
            if text_position == 'middle':
                position = ('center', video_clip.h * 0.3)
            else:
                position = ('center', video_clip.h * 0.8)

            text_clips = []
            # Get punctuation-aware timings
            timings = text_processor.create_punctuation_aware_karaoke(text, audio_duration)
            st.info(f"📊 Processing {len(timings)} karaoke segments with {effect_config['name']} effect")

            for i, timing in enumerate(timings):
                chunk_text = timing['text']
                start_time = timing['start_time']
                end_time = min(timing['end_time'], audio_duration)  # Ensure end_time doesn't exceed audio_duration
                has_punctuation = timing['has_punctuation']
                punctuation = timing.get('punctuation', '')

                if start_time >= audio_duration:
                    st.warning(f"⚠️ Skipping segment {i}: start_time {start_time}s exceeds audio duration {audio_duration}s")
                    continue

                try:
                    # Apply effect settings with defaults
                    stroke_color = effect_config.get('stroke_color', 'black')
                    stroke_width = effect_config.get('stroke_width', 2)
                    font_color = effect_config.get('font_color', text_color)

                    # Apply special styling for punctuation with effects
                    if has_punctuation and punctuation in ['.', '!', '?']:
                        if text_effect == 'glow':
                            font_color = effect_config.get('glow_color', '#FFD700')
                        elif text_effect == 'neon':
                            font_color = effect_config.get('neon_color', '#00FFFF')
                        elif text_effect == 'fade':
                            font_color = effect_config.get('fade_color', text_color)

                    # Create text clip with effect settings
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
                    st.warning(f"⚠️ Failed to create text clip for '{chunk_text}' at segment {i}: {str(e)}")
                    continue

            if not text_clips:
                st.warning("⚠️ No text clips created, falling back to normal subtitle")
                return self._add_normal_subtitle(video_clip, text, font_size, text_color, text_position, text_effect)

            # Composite video with text clips
            st.info(f"🔄 Compositing {len(text_clips)} segments with {effect_config['name']} effect")
            result = CompositeVideoClip([video_clip] + text_clips)

            # Clean up text clips to prevent memory leaks
            for txt_clip in text_clips:
                try:
                    txt_clip.close()
                except:
                    pass

            return result

        except Exception as e:
            st.error(f"❌ Failed to create punctuation-aware karaoke: {str(e)}")
            return self._add_normal_subtitle(video_clip, text, font_size, text_color, text_position, text_effect)

    def _add_normal_subtitle(self, video_clip, text, font_size, text_color, text_position, text_effect='none'):
        """Add static subtitle with text effects"""
        try:
            st.info(f"📝 Adding static subtitle with {text_effect} effect...")

            # Get effect config with fallback
            effect_config = get_text_effect_config(text_effect)
            if not effect_config:
                st.warning(f"⚠️ Invalid text effect '{text_effect}', using default settings")
                effect_config = get_text_effect_config('none')

            # Calculate position
            if text_position == 'middle':
                position = ('center', video_clip.h * 0.3)
            else:
                position = ('center', video_clip.h * 0.85)

            # Split text into manageable lines
            optimized_lines = text_processor.optimize_for_display(text, max_line_length=25)
            display_text = '\n'.join(optimized_lines[:3])  # Limit to 3 lines

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
            ).set_position(position).set_duration(video_clip.duration)

            # Composite video with subtitle
            result = CompositeVideoClip([video_clip, txt_clip])

            # Clean up text clip
            try:
                txt_clip.close()
            except:
                pass

            st.success(f"✅ Static subtitle with {effect_config['name']} effect added")
            return result

        except Exception as e:
            st.warning(f"⚠️ Failed to add static subtitle: {str(e)}")
            return video_clip

    def _loop_clip(self, clip, target_duration):
        """Loop a clip to reach target duration"""
        loops_needed = int(target_duration / clip.duration) + 1
        clips = [clip] * loops_needed
        looped_clip = concatenate_videoclips(clips, method="compose")
        return looped_clip.subclip(0, target_duration)

    def _create_fallback_video(self, media_files, audio_path, duration, video_format):
        """Create a fallback video when main processing fails"""
        st.warning("🔄 Using enhanced fallback video creation...")

        try:
            # Try to create a simple slideshow from images
            image_files = [f for f in media_files if f and f.type.startswith('image')]
            if image_files:
                return self._create_simple_slideshow(image_files, duration, video_format)
            else:
                return self._create_dummy_video(media_files, audio_path, duration)

        except Exception as e:
            st.error(f"❌ Fallback video failed: {str(e)}")
            return self._create_dummy_video(media_files, audio_path, duration)

    def _create_simple_slideshow(self, image_files, duration, video_format):
        """Create a simple slideshow from images"""
        try:
            if not MOVIEPY_AVAILABLE:
                return self._create_dummy_video(image_files, None, duration)

            # Use first few images
            images_to_use = image_files[:3]
            clips = []
            image_duration = duration / len(images_to_use)
            temp_files = []

            for i, image_file in enumerate(images_to_use):
                try:
                    temp_path = os.path.join(self.temp_dir, f"temp_img_{uuid.uuid4().hex[:8]}_{image_file.name}")
                    with open(temp_path, 'wb') as f:
                        f.write(image_file.getvalue())

                    # Create image clip
                    clip = ImageClip(temp_path).set_duration(image_duration)

                    # Resize
                    if video_format == 'short':
                        clip = clip.resize(height=1920)
                    else:
                        clip = clip.resize(height=1080)

                    clips.append(clip)
                    temp_files.append(temp_path)

                except Exception as e:
                    st.warning(f"⚠️ Failed to process image {image_file.name}: {str(e)}")
                    continue

            if not clips:
                return self._create_dummy_video(image_files, None, duration)

            # Concatenate clips
            final_clip = concatenate_videoclips(clips, method="compose")

            # Export
            output_path = os.path.join(self.temp_dir, f"video_slideshow_{uuid.uuid4().hex[:8]}.mp4")
            final_clip.write_videofile(output_path, verbose=False, logger=None, fps=1)

            # Cleanup
            self._cleanup_clips([final_clip] + clips, temp_files)

            st.success("✅ Simple slideshow video created")
            return output_path

        except Exception as e:
            st.warning(f"⚠️ Simple slideshow failed: {str(e)}")
            return self._create_dummy_video(image_files, None, duration)

    def _create_dummy_video(self, media_files, audio_path, duration):
        """Create a dummy video file as last resort"""
        st.info("🎬 Creating placeholder video...")

        output_filename = f"video_placeholder_{uuid.uuid4().hex[:8]}.mp4"
        output_path = os.path.join(self.temp_dir, sanitize_filename(output_filename))

        # Create informative placeholder
        with open(output_path, 'w') as f:
            f.write("VIDEO_PLACEHOLDER\n")
            f.write("================\n")
            f.write(f"Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Duration: {duration}s\n")
            f.write(f"Media files: {len(media_files)}\n")
            f.write(f"Audio: {'Yes' if audio_path else 'No'}\n")
            f.write("\n")
            f.write("This is a placeholder video file.\n")
            f.write("Real video processing requires MoviePy and proper dependencies.\n")

        st.success("✅ Placeholder video created")
        return output_path

# Create singleton instance
video_editor = VideoEditor()
