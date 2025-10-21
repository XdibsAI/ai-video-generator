    def render_video_generator(self, settings):
        """Render video generation section dengan auto-subtitle"""
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
        
        # ✅ AUTO SUBTITLE OPTION
        has_video_upload = any(f.type.startswith('video') for f in st.session_state.uploaded_files) if st.session_state.uploaded_files else False
        
        if has_video_upload:
            st.subheader("🎤 Opsi Subtitle Otomatis")
            auto_subtitle = st.checkbox(
                "Gunakan teks dari audio video yang diupload",
                help="Extract teks otomatis dari audio video dan gunakan sebagai subtitle",
                key="auto_subtitle_checkbox"
            )
            
            if auto_subtitle:
                st.info("ℹ️ Teks akan diekstrak dari audio video dan digunakan sebagai narasi")
        else:
            auto_subtitle = False
        
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
        
        if not st.session_state.story_generated and not auto_subtitle:
            st.warning("⚠️ Silakan generate cerita atau aktifkan auto-subtitle terlebih dahulu")
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
                # Determine audio source
                if auto_subtitle and has_video_upload:
                    # Use audio from uploaded video
                    status_text.text("🔊 Using audio from uploaded video...")
                    video_file = next(f for f in st.session_state.uploaded_files if f.type.startswith('video'))
                    
                    # Extract audio from video
                    import tempfile
                    temp_video_path = os.path.join(tempfile.gettempdir(), f"temp_video_{uuid.uuid4().hex[:8]}_{video_file.name}")
                    with open(temp_video_path, 'wb') as f:
                        f.write(video_file.getvalue())
                    
                    from moviepy.editor import VideoFileClip
                    video_clip = VideoFileClip(temp_video_path)
                    audio_path = os.path.join(tempfile.gettempdir(), f"extracted_audio_{uuid.uuid4().hex[:8]}.mp3")
                    video_clip.audio.write_audiofile(audio_path, verbose=False, logger=None)
                    video_clip.close()
                    
                    # Extract text from video audio
                    status_text.text("🎤 Extracting text from video audio...")
                    transcribed_text = speech_to_text.transcribe_video(video_file, settings['language'])
                    if transcribed_text:
                        st.session_state.story_text = transcribed_text
                        st.success(f"✅ Extracted {len(transcribed_text)} characters from video")
                    
                else:
                    # Generate TTS seperti biasa
                    status_text.text("🔊 Generating audio narration...")
                    audio_path = generate_tts_sync(st.session_state.story_text, settings['language'])
                
                progress_bar.progress(33)
                
                if not audio_path:
                    st.error("❌ Gagal mendapatkan audio")
                    return
                
                st.session_state.audio_path = audio_path
                
                status_text.text("🎬 Step 2: Creating video with REAL karaoke...")
                
                # ✅ USE THE SELECTED MODE dengan auto-subtitle
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
                    subtitle_language=settings['language']
                )
                progress_bar.progress(66)
                
                if not video_path:
                    st.error("❌ Gagal generate video")
                    return
                
                st.session_state.video_path = video_path
                st.session_state.video_mode = video_mode
                
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
                subtitle_source = "auto dari video" if auto_subtitle else "teks provided"
                status_text.text(f"✅ {mode_name} dengan subtitle {subtitle_source} berhasil di-generate!")
                
                st.balloons()
                
            except Exception as e:
                st.error(f"❌ Error generating video: {str(e)}")
                import traceback
                st.error(f"Detailed error: {traceback.format_exc()}")
                progress_bar.progress(0)
