from PIL import Image
import os
import uuid
import tempfile
import streamlit as st
from utils.compatibility import sanitize_filename
from utils.text_processor import text_processor

# Compatibility fix for Pillow >=10
if not hasattr(Image, 'ANTIALIAS'):
    Image.ANTIALIAS = Image.Resampling.LANCZOS

# Try to import MoviePy with multiple fallbacks
MOVIEPY_AVAILABLE = False
try:
    from moviepy.editor import VideoFileClip, ImageClip, concatenate_videoclips, CompositeVideoClip, AudioFileClip, TextClip, ColorClip
    from moviepy.video.io.bindings import mplfig_to_npimage
    import numpy as np
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
                    mode='video'):  # ✅ NEW: Added mode parameter
        """Create video atau teks-only dengan proper audio synchronization"""
        
        try:
            if not MOVIEPY_AVAILABLE:
                return self._create_fallback_video(media_files, audio_path, duration, video_format)
            
            if mode == 'text_only':
                st.info("🎬 Creating TEXT-ONLY karaoke video...")
                return self._create_text_only_video(
                    audio_path, duration, video_format, subtitle_text,
                    font_size, text_color, text_position, background_music, music_volume
                )
            else:
                st.info("🎬 Starting video creation with audio synchronization...")
                return self._create_standard_video(
                    media_files, audio_path, duration, video_format,
                    subtitle_text, font_size, text_color, text_position,
                    background_music, music_volume
                )
            
        except Exception as e:
            st.error(f"❌ Video creation failed: {str(e)}")
            import traceback
            st.error(f"Detailed error: {traceback.format_exc()}")
            return self._create_fallback_video(media_files, audio_path, duration, video_format)
    
    def _create_text_only_video(self, audio_path, duration, video_format, subtitle_text,
                               font_size, text_color, text_position, background_music, music_volume):
        """Create text-only karaoke video dengan background color"""
        try:
            # Video settings
            if video_format == 'short':
                width, height = 1080, 1920  # 9:16
            else:
                width, height = 1920, 1080  # 16:9
            
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
            background = ColorClip(size=(width, height), color=(0, 0, 0))  # Black background
            background = background.set_duration(actual_duration)
            
            final_clip = background
            
            # Add audio if available
            if audio_path and os.path.exists(audio_path):
                try:
                    audio_clip = AudioFileClip(audio_path)
                    
                    # Match audio duration to video duration
                    if audio_clip.duration > actual_duration:
                        # Audio too long - trim it
                        audio_clip = audio_clip.subclip(0, actual_duration)
                        st.info("✂️ Audio trimmed to match video duration")
                    elif audio_clip.duration < actual_duration:
                        # Audio too short - loop it
                        audio_clip = self._loop_audio(audio_clip, actual_duration)
                        st.info("🔁 Audio looped to match video duration")
                    
                    final_clip = final_clip.set_audio(audio_clip)
                    st.success("✅ Audio synchronized with text video")
                    
                except Exception as e:
                    st.warning(f"⚠️ Could not add audio: {str(e)}")
            
            # Add PUNCTUATION-AWARE karaoke subtitles
            if subtitle_text:
                try:
                    final_clip = self._add_punctuation_aware_karaoke(
                        final_clip, subtitle_text, font_size, text_color, 
                        text_position, actual_duration
                    )
                    st.success("✅ Punctuation-aware karaoke added to text-only video!")
                except Exception as e:
                    st.warning(f"⚠️ Could not add karaoke: {str(e)}")
                    # Fallback to normal subtitle
                    final_clip = self._add_normal_subtitle(final_clip, subtitle_text, font_size, text_color, text_position)
            
            # Add background music if provided
            if background_music and os.path.exists(background_music):
                try:
                    bg_music_clip = AudioFileClip(background_music).volumex(music_volume)
                    bg_music_clip = bg_music_clip.subclip(0, actual_duration)
                    
                    if final_clip.audio:
                        # Combine narration with background music
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
            
            # Write video file with optimized settings
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
            
            # Cleanup
            final_clip.close()
            
            st.success(f"✅ Text-only karaoke video created: {os.path.basename(output_path)}")
            return output_path
            
        except Exception as e:
            st.error(f"❌ Text-only video creation failed: {str(e)}")
            raise e
    
    def _create_standard_video(self, media_files, audio_path, duration, video_format,
                              subtitle_text, font_size, text_color, text_position,
                              background_music, music_volume):
        """Create standard video dengan media files (existing functionality)"""
        # Video settings
        if video_format == 'short':
            width, height = 1080, 1920  # 9:16
        else:
            width, height = 1920, 1080  # 16:9
        
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
                else:  # image
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
            # Use the shorter duration between audio and target
            actual_duration = min(audio_duration, duration)
            
            if final_clip.duration > actual_duration:
                final_clip = final_clip.subclip(0, actual_duration)
            elif final_clip.duration < actual_duration:
                final_clip = self._loop_clip(final_clip, actual_duration)
            
            st.info(f"📊 Using synchronized duration: {actual_duration:.1f}s")
        else:
            # No audio, use target duration
            if final_clip.duration > duration:
                final_clip = final_clip.subclip(0, duration)
            elif final_clip.duration < duration:
                final_clip = self._loop_clip(final_clip, duration)
        
        # Add audio if available
        final_audio_duration = final_clip.duration
        if audio_path and os.path.exists(audio_path):
            try:
                audio_clip = AudioFileClip(audio_path)
                
                # Match audio duration to video duration
                if audio_clip.duration > final_audio_duration:
                    # Audio too long - trim it
                    audio_clip = audio_clip.subclip(0, final_audio_duration)
                    st.info("✂️ Audio trimmed to match video duration")
                elif audio_clip.duration < final_audio_duration:
                    # Audio too short - loop it
                    audio_clip = self._loop_audio(audio_clip, final_audio_duration)
                    st.info("🔁 Audio looped to match video duration")
                
                final_clip = final_clip.set_audio(audio_clip)
                st.success("✅ Audio synchronized with video")
                
            except Exception as e:
                st.warning(f"⚠️ Could not add audio: {str(e)}")
                final_audio_duration = final_clip.duration
        else:
            final_audio_duration = final_clip.duration
        
        # Add PUNCTUATION-AWARE karaoke subtitles
        if subtitle_text:
            try:
                # Use actual audio duration for karaoke timing
                final_clip = self._add_punctuation_aware_karaoke(
                    final_clip, subtitle_text, font_size, text_color, 
                    text_position, final_audio_duration
                )
                st.success("✅ Punctuation-aware karaoke added!")
            except Exception as e:
                st.warning(f"⚠️ Could not add karaoke: {str(e)}")
                # Fallback to normal subtitle
                final_clip = self._add_normal_subtitle(final_clip, subtitle_text, font_size, text_color, text_position)
        
        # Add background music if provided
        if background_music and os.path.exists(background_music):
            try:
                bg_music_clip = AudioFileClip(background_music).volumex(music_volume)
                bg_music_clip = bg_music_clip.subclip(0, final_audio_duration)
                
                if final_clip.audio:
                    # Combine narration with background music
                    from moviepy.audio.AudioClip import CompositeAudioClip
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
        
        # Write video file with optimized settings
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
        from moviepy.audio.AudioClip import concatenate_audioclips
        
        loops_needed = int(target_duration / audio_clip.duration) + 1
        clips = [audio_clip] * loops_needed
        looped_audio = concatenate_audioclips(clips)
        return looped_audio.subclip(0, target_duration)

    def _add_punctuation_aware_karaoke(self, video_clip, text, font_size, text_color, text_position, audio_duration):
        """Add karaoke yang sync dengan punctuation di audio"""
        try:
            st.info("🎤 Creating punctuation-aware karaoke...")
            
            # Calculate position - use UPPER position to avoid covering video content
            if text_position == 'middle':
                position = ('center', video_clip.h * 0.3)  # 30% from top
            else:  # bottom
                position = ('center', video_clip.h * 0.8)
            
            text_clips = []
            
            # Get punctuation-aware timings
            timings = text_processor.create_punctuation_aware_karaoke(text, audio_duration)
            
            # Display timing info untuk debugging
            st.info(f"📊 Karaoke segments: {len(timings)} | Audio duration: {audio_duration:.1f}s")
            
            for i, timing in enumerate(timings):
                chunk_text = timing['text']
                start_time = timing['start_time']
                end_time = timing['end_time']
                has_punctuation = timing['has_punctuation']
                punctuation = timing['punctuation']
                
                # Ensure timing doesn't exceed audio duration
                if start_time >= audio_duration:
                    break
                    
                end_time = min(end_time, audio_duration)
                
                # Create text clip untuk chunk ini
                try:
                    # Different styling untuk punctuation
                    stroke_width = 4 if has_punctuation else 2
                    font_color = text_color
                    
                    # Highlight punctuation dengan warna berbeda
                    if has_punctuation and punctuation in ['.', '!', '?']:
                        font_color = '#FFD700'  # Gold untuk sentence endings
                    
                    txt_clip = TextClip(
                        chunk_text,
                        fontsize=font_size,
                        color=font_color,
                        font='Arial-Bold',
                        stroke_color='black',
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
                return self._add_normal_subtitle(video_clip, text, font_size, text_color, text_position)
            
            # Composite all text clips with video
            st.info(f"🔄 Compositing {len(text_clips)} synchronized segments...")
            result = CompositeVideoClip([video_clip] + text_clips)
            
            return result
            
        except Exception as e:
            st.error(f"❌ Punctuation-aware karaoke error: {str(e)}")
            raise e

    def _add_normal_subtitle(self, video_clip, text, font_size, text_color, text_position):
        """Add normal static subtitle as fallback"""
        try:
            # Calculate position - use upper position
            if text_position == 'middle':
                position = ('center', video_clip.h * 0.3)  # 30% from top
            else:  # bottom
                position = ('center', video_clip.h * 0.85)
            
            # Split text into manageable lines
            optimized_lines = text_processor.optimize_for_display(text, max_line_length=25)
            display_text = '\n'.join(optimized_lines[:3])  # Max 3 lines
            
            # Create text clip
            txt_clip = TextClip(
                display_text,
                fontsize=font_size,
                color=text_color,
                font='Arial-Bold',
                stroke_color='black',
                stroke_width=2,
                size=(video_clip.w * 0.9, None),
                method='caption'
            )
            
            txt_clip = txt_clip.set_position(position).set_duration(video_clip.duration)
            
            # Composite with video
            result = CompositeVideoClip([video_clip, txt_clip])
            return result
            
        except Exception as e:
            st.warning(f"⚠️ Normal subtitle error: {str(e)}")
            return video_clip

    def _cleanup_clips(self, clips, temp_files):
        """Clean up clips and temporary files"""
        for clip in clips:
            try:
                clip.close()
            except:
                pass
        
        for temp_file in temp_files:
            try:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
            except:
                pass
    
    def _loop_clip(self, clip, target_duration):
        """Loop a clip to reach target duration"""
        from moviepy.editor import concatenate_videoclips
        
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
            images_to_use = image_files[:3]  # Max 3 images
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

# Import datetime for the dummy video
from datetime import datetime

# Singleton instance
video_editor = VideoEditor()
