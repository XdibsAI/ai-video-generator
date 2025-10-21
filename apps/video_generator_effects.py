    def render_video_generator(self, settings):
        """Render video generation section dengan text effects"""
        st.header("🎬 Generate Video")
        
        # System capability check
        if not TTS_AVAILABLE:
            st.error("❌ TTS tidak tersedia. Install: pip install gtts")
            return
            
        if not MOVIEPY_AVAILABLE:
            st.error("❌ Video processing tidak tersedia. Install: pip install moviepy")
            return
            
        if not check_ffmpeg():
            st.error("❌ FFmpeg tidak tersedia. Install: sudo apt install ffmpeg")
            return
        
        # ✅ TEXT EFFECTS SECTION
        st.subheader("🎨 Pilih Efek Teks")
        selected_effect = self.render_text_effects_section()
        
        # ... (rest of existing video generator code tetap sama)
        
        # Dalam bagian generate_video_clicked, pastikan pass text_effect:
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
            text_effect=selected_effect  # ✅ PASS SELECTED EFFECT
        )
