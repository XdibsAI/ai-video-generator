#!/bin/bash

# Backup file
cp apps/main.py apps/main.py.backup_methods

# Tambahkan method yang missing
cat >> apps/main.py << 'PYTHONEOF'

    def render_header(self):
        """Render application header"""
        st.markdown('<h1 class="main-header">🎬 AI Video Generator</h1>', unsafe_allow_html=True)
        st.markdown("""
        <div style='text-align: center; margin-bottom: 2rem;'>
            <p style='font-size: 1.2rem; color: #666;'>
                Buat video menarik dengan AI dalam hitungan menit!
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # System status overview
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            ffmpeg_status = "✅" if check_ffmpeg() else "❌"
            st.info(f"🎥 FFmpeg: {ffmpeg_status}")
        with col2:
            moviepy_status = "✅" if MOVIEPY_AVAILABLE else "❌"
            st.info(f"🎬 MoviePy: {moviepy_status}")
        with col3:
            tts_status = "✅" if TTS_AVAILABLE else "❌"
            st.info(f"🔊 TTS: {tts_status}")
        with col4:
            try:
                api_status = "✅" if hasattr(story_generator, 'api_key') and story_generator.api_key else "❌"
                st.info(f"🤖 API: {api_status}")
            except:
                st.info(f"🤖 API: ❌")

    def render_file_upload(self):
        """Render file upload section"""
        st.header("📁 Upload Media")
        st.info("⚠️ Fitur upload sedang dalam pengembangan...")

    def render_story_generator(self, settings):
        """Render story generation section"""
        st.header("📖 Generate Cerita (3 Pilihan)")
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            generate_clicked = st.button("🎭 Generate 3 Cerita Options", 
                                       use_container_width=True, 
                                       type="primary",
                                       key="generate_stories_btn")
        
        with col2:
            # ✅ FIX: Gunakan estimate_word_count yang sudah ada
            word_range = estimate_word_count(settings['duration'])
            st.info(f"**Target:** {word_range[0]}-{word_range[1]} kata")
        
        if generate_clicked:
            if not hasattr(story_generator, 'api_key') or not story_generator.api_key:
                st.error("❌ API Key belum dikonfigurasi. Silakan setup di config/settings.py")
                return
            
            with st.spinner("🤖 AI sedang membuat 3 pilihan cerita..."):
                try:
                    story_options = story_generator.generate_stories(
                        niche=settings['niche'],
                        duration_seconds=settings['duration'],
                        style="Serius",
                        language=settings['language'],
                        user_description=settings['user_description']
                    )
                    
                    if story_options and len(story_options) >= 1:
                        st.session_state.story_options = story_options
                        st.session_state.selected_story_index = 0
                        st.session_state.story_text = story_options[0]
                        st.session_state.story_generated = True
                        st.success("✅ 3 pilihan cerita berhasil di-generate!")
                    else:
                        st.error("❌ Gagal generate cerita")
                        
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
        
        if st.session_state.story_generated and st.session_state.story_options:
            st.subheader("🎯 Pilih Salah Satu Cerita")
            
            selected_index = st.radio(
                "Pilih opsi cerita:",
                options=range(len(st.session_state.story_options)),
                format_func=lambda i: f"Opsi {i+1}: {st.session_state.story_options[i][:50]}...",
                key="story_selection"
            )
            
            st.session_state.selected_story_index = selected_index
            st.session_state.story_text = st.session_state.story_options[selected_index]
            
            st.subheader("✏️ Edit Cerita yang Dipilih")
            edited_story = st.text_area(
                "Edit cerita sesuai keinginanmu:",
                value=st.session_state.story_text,
                height=200,
                key="story_editor"
            )
            
            if st.button("💾 Simpan Perubahan"):
                st.session_state.story_text = edited_story
                st.session_state.story_options[selected_index] = edited_story
                st.success("✅ Perubahan disimpan!")
            
            word_count = len(st.session_state.story_text.split())
            st.caption(f"📊 **{word_count} kata**")

    def render_video_generator(self, settings):
        """Render video generation section"""
        st.header("🎬 Generate Video")
        
        if not st.session_state.story_generated:
            st.warning("⚠️ Silakan generate cerita terlebih dahulu di tab 'Generate Cerita'")
            return
        
        st.info("🎨 Pilih efek teks untuk video karaoke")
        
        # Simple effect selection
        effect_options = ['none', 'typewriter', 'highlight', 'glow']
        selected_effect = st.selectbox(
            "Efek Teks:",
            options=effect_options,
            format_func=lambda x: {
                'none': 'Tidak Ada Efek',
                'typewriter': 'Efek Typewriter',
                'highlight': 'Efek Highlight', 
                'glow': 'Efek Glow'
            }[x],
            key="effect_select"
        )
        
        if st.button("🚀 Generate Video dengan Karaoke", use_container_width=True):
            with st.spinner("🎬 Membuat video..."):
                try:
                    # Generate audio
                    audio_path = generate_tts_sync(st.session_state.story_text, settings['language'])
                    
                    if audio_path:
                        st.session_state.audio_path = audio_path
                        st.success("✅ Audio berhasil dibuat!")
                    
                    # Simulate video generation
                    st.session_state.video_path = f"/tmp/demo_video_{uuid.uuid4().hex[:8]}.mp4"
                    st.success("✅ Video berhasil dibuat! (Demo Mode)")
                    
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")

    def render_results(self):
        """Render results section"""
        if not st.session_state.get('video_path'):
            st.info("📊 Hasil video akan muncul di sini setelah generate")
            return
        
        st.header("🎉 Hasil Video")
        st.success("✅ Video berhasil dibuat!")
        
        st.info("📺 Preview video (Demo Mode)")
        st.video("https://sample-videos.com/zip/10/mp4/SampleVideo_1280x720_1mb.mp4")
        
        st.download_button(
            label="📥 Download Video MP4",
            data=b"Demo video content",
            file_name=f"video_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4",
            mime="video/mp4",
            use_container_width=True
        )

PYTHONEOF

echo "✅ Method yang missing telah ditambahkan!"
