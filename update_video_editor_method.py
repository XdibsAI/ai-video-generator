# Tambahkan method untuk handle existing video di video_editor.py
cat >> utils/video_editor.py << 'VIDEOEDITOREOF'

    def add_text_to_existing_video(self, video_path, subtitle_text, output_path, 
                                 font_size=60, text_color="#FFFFFF", text_position="middle",
                                 text_effect='none'):
        """
        Add text/subtitle to existing video without re-rendering entire video
        """
        try:
            from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip
            import tempfile
            
            # Load the original video
            video_clip = VideoFileClip(video_path)
            
            # Create text clips with effects
            text_clips = self._create_text_clips(
                subtitle_text, 
                video_clip.duration, 
                font_size, 
                text_color, 
                text_position,
                text_effect,
                video_clip.size
            )
            
            # Composite text on original video
            final_video = CompositeVideoClip([video_clip] + text_clips)
            
            # Write result
            final_video.write_videofile(
                output_path,
                codec='libx264',
                audio_codec='aac',
                temp_audiofile='temp-audio.m4a',
                remove_temp=True,
                verbose=False,
                logger=None
            )
            
            # Close clips
            video_clip.close()
            final_video.close()
            
            return output_path
            
        except Exception as e:
            print(f"Error adding text to existing video: {e}")
            return None

    def create_video_with_existing(self, original_video_path, subtitle_text, output_path,
                                 font_size=60, text_color="#FFFFFF", text_position="middle",
                                 text_effect='none', duration=None):
        """
        Create video using existing video as base with added text
        """
        try:
            from moviepy.editor import VideoFileClip
            
            # Load original video to get duration if not provided
            if not duration:
                video_clip = VideoFileClip(original_video_path)
                duration = video_clip.duration
                video_clip.close()
            
            # Use the add_text_to_existing_video method
            return self.add_text_to_existing_video(
                original_video_path,
                subtitle_text,
                output_path,
                font_size,
                text_color, 
                text_position,
                text_effect
            )
            
        except Exception as e:
            print(f"Error creating video with existing: {e}")
            return None
VIDEOEDITOREOF

echo "✅ Video editor methods untuk existing video ditambahkan"
