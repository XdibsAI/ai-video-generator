    def render_video_generator(self, settings):
        """Render video generation section dengan mode selection"""
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
        
        # ✅ MODE SELECTION
        st.subheader("🎯 Pilih Mode Video")
        
        col1, col2 = st.columns(2)
        
        with col1:
            video_mode = st.radio(
                "Pilih jenis video:",
                options=['video', 'text_only'],
                format_func=lambda x: "🎬 Video dengan Media" if x == 'video' else "📝 Teks Karaoke Only",
                index=0,
                key="video_mode_radio"
            )
        
        with col2:
            if video_mode == 'video':
                st.info("""
                **🎬 Video dengan Media:**
                - Gunakan gambar/video yang diupload
                - Teks karaoke muncul di atas media
                - Cocok untuk content yang visual
                """)
            else:
                st.info("""
                **📝 Teks Karaoke Only:**
                - Background hitam polos
                - Fokus pada teks karaoke
                - Cocok untuk lyric video atau quotes
                - Lebih cepat render
                """)
        
        # Show appropriate requirements based on mode
        if video_mode == 'video' and not st.session_state.uploaded_files:
            st.warning("⚠️ Untuk mode Video, silakan upload file media terlebih dahulu")
            return
        
        if not st.session_state.story_generated:
            st.warning("⚠️ Silakan generate cerita terlebih dahulu")
            return
        
        # ✅ INFO KARAOKE
        st.markdown("""
        <div class="karaoke-info">
        <h4>🎤 Fitur Karaoke Aktif</h4>
        <p>Teks akan muncul <strong>kata demi kata</strong> sesuai timing audio narration!</p>
        <ul>
            <li>✅ Sync sempurna dengan suara</li>
            <li>✅ Efek typewriter real-time</li>
            <li>✅ Posisi teks dapat disesuaikan</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)
        
        generate_video_clicked = st.button("🚀 Generate Video dengan Karaoke", 
                                         use_container_width=True, 
                                         type="primary",
                                         key="generate_video_btn")
        
        if generate_video_clicked:
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            try:
                status_text.text("🔊 Step 1: Generating audio narration...")
                audio_path = generate_tts_sync(st.session_state.story_text, settings['language'])
                progress_bar.progress(33)
                
                if not audio_path:
                    st.error("❌ Gagal generate audio")
                    return
                
                st.session_state.audio_path = audio_path
                
                status_text.text("🎬 Step 2: Creating video with REAL karaoke...")
                
                # ✅ USE THE SELECTED MODE
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
                    mode=video_mode  # ✅ NEW: Pass the selected mode
                )
                progress_bar.progress(66)
                
                if not video_path:
                    st.error("❌ Gagal generate video")
                    return
                
                st.session_state.video_path = video_path
                st.session_state.video_mode = video_mode  # Store the mode for results display
                
                status_text.text("📊 Step 3: Optimizing content...")
                try:
                    st.session_state.optimized_content = content_optimizer.optimize_content(
                        st.session_state.story_text,
                        settings['niche'],
                        settings['language']
                    )
                except:
                    st.session_state.optimized_content = {
                        'title': 'Generated Video',
                        'description': st.session_state.story_text[:100] + '...',
                        'hooks': ['Watch this amazing video!'],
                        'hashtags': ['video', 'content'],
                        'optimal_posting_times': []
                    }
                
                progress_bar.progress(100)
                
                mode_name = "Video dengan Media" if video_mode == 'video' else "Teks Karaoke Only"
                status_text.text(f"✅ {mode_name} berhasil di-generate!")
                
                st.balloons()
                
            except Exception as e:
                st.error(f"❌ Error generating video: {str(e)}")
                import traceback
                st.error(f"Detailed error: {traceback.format_exc()}")
                progress_bar.progress(0)
