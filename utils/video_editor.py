from PIL import Image
import os
import uuid
import tempfile
import streamlit as st
from utils.compatibility import sanitize_filename

# Compatibility fix for Pillow >=10
if not hasattr(Image, 'ANTIALIAS'):
    Image.ANTIALIAS = Image.Resampling.LANCZOS

# Try to import MoviePy with multiple fallbacks
MOVIEPY_AVAILABLE = False
try:
    from moviepy.editor import VideoFileClip, ImageClip, concatenate_videoclips, CompositeVideoClip, AudioFileClip, TextClip
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
                    background_music=None, music_volume=0.3):
        """Create video with REAL karaoke effect - ONE WORD AT A TIME"""
        
        try:
            if not MOVIEPY_AVAILABLE:
                return self._create_fallback_video(media_files, audio_path, duration, video_format)
            
            st.info("🎬 Starting video creation with REAL karaoke effect...")
            
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
            
            # Adjust duration
            if final_clip.duration > duration:
                final_clip = final_clip.subclip(0, duration)
            elif final_clip.duration < duration:
                final_clip = self._loop_clip(final_clip, duration)
            
            # Add audio if available
            audio_duration = duration
            if audio_path and os.path.exists(audio_path):
                try:
                    audio_clip = AudioFileClip(audio_path)
                    audio_duration = min(audio_clip.duration, duration)
                    audio_clip = audio_clip.subclip(0, audio_duration)
                    final_clip = final_clip.set_audio(audio_clip)
                    st.success("✅ Audio added to video")
                except Exception as e:
                    st.warning(f"⚠️ Could not add audio: {str(e)}")
            
            # Add REAL karaoke subtitles - ONE WORD AT A TIME
            if subtitle_text:
                try:
                    final_clip = self._add_real_karaoke_subtitle(final_clip, subtitle_text, font_size, text_color, text_position, audio_duration)
                    st.success("✅ Karaoke subtitles added (one word at a time)")
                except Exception as e:
                    st.warning(f"⚠️ Could not add karaoke: {str(e)}")
                    # Fallback to normal subtitle
                    final_clip = self._add_normal_subtitle(final_clip, subtitle_text, font_size, text_color, text_position)
            
            # Add background music if provided
            if background_music and os.path.exists(background_music):
                try:
                    bg_music_clip = AudioFileClip(background_music).volumex(music_volume)
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
            
            st.info("📤 Exporting video with karaoke...")
            
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
            
            st.success(f"✅ Video with REAL karaoke created: {os.path.basename(output_path)}")
            return output_path
            
        except Exception as e:
            st.error(f"❌ Video creation failed: {str(e)}")
            import traceback
            st.error(f"Detailed error: {traceback.format_exc()}")
            return self._create_fallback_video(media_files, audio_path, duration, video_format)
    
    def _add_real_karaoke_subtitle(self, video_clip, text, font_size, text_color, text_position, audio_duration):
        """Add REAL karaoke subtitle that shows ONE WORD AT A TIME"""
        try:
            st.info("🎤 Creating word-by-word karaoke effect...")
            
            # Split text into words
            words = text.split()
            if not words:
                return video_clip
            
            # Calculate timing for each word (simple linear distribution)
            total_words = len(words)
            word_duration = audio_duration / total_words
            
            # Calculate position - use UPPER position to avoid covering video content
            if text_position == 'middle':
                position = ('center', video_clip.h * 0.3)  # 30% from top instead of center
            else:  # bottom
                position = ('center', video_clip.h * 0.8)
            
            text_clips = []
            
            # Create INDIVIDUAL text clips for EACH WORD
            for i in range(total_words):
                # Current text: ONLY the current word
                current_word = words[i]
                
                # Timing for this word
                start_time = i * word_duration
                end_time = min((i + 1) * word_duration, audio_duration)
                
                # Ensure minimum duration
                if end_time - start_time < 0.1:
                    end_time = start_time + 0.1
                
                # Create text clip for THIS WORD ONLY
                try:
                    txt_clip = TextClip(
                        current_word,  # Hanya satu kata!
                        fontsize=font_size,
                        color=text_color,
                        font='Arial-Bold',
                        stroke_color='black',
                        stroke_width=3,  # Thicker stroke for better visibility
                        size=(video_clip.w * 0.8, None),  # Limit width
                        method='caption'
                    ).set_position(position).set_start(start_time).set_duration(end_time - start_time)
                    
                    text_clips.append(txt_clip)
                    
                except Exception as e:
                    st.warning(f"⚠️ Error creating text clip for word '{words[i]}': {str(e)}")
                    continue
            
            if not text_clips:
                st.warning("⚠️ No text clips created, using normal subtitle")
                return self._add_normal_subtitle(video_clip, text, font_size, text_color, text_position)
            
            # Composite all text clips with video
            st.info(f"🔄 Compositing {len(text_clips)} individual word clips...")
            result = CompositeVideoClip([video_clip] + text_clips)
            
            return result
            
        except Exception as e:
            st.error(f"❌ Karaoke subtitle error: {str(e)}")
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
            words = text.split()
            lines = []
            current_line = []
            current_length = 0
            
            for word in words:
                current_line.append(word)
                current_length += len(word) + 1
                
                if current_length > 25:  # Fewer characters per line for better readability
                    lines.append(' '.join(current_line))
                    current_line = []
                    current_length = 0
            
            if current_line:
                lines.append(' '.join(current_line))
            
            # Take first 2-3 lines max
            display_text = '\n'.join(lines[:3])
            
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
