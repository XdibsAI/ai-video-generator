    def render_file_upload(self):
        """Render file upload section dengan auto-subtitle feature"""
        st.header("📁 Upload Media")
        
        # ✅ AUTO SUBTITLE SECTION
        st.subheader("🎤 Auto Subtitle dari Video")
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            video_for_subtitle = st.file_uploader(
                "Upload video untuk extract teks otomatis",
                type=['mp4', 'mov', 'avi'],
                help="Upload video yang ada suara, kami akan extract teksnya otomatis",
                key="subtitle_video_uploader"
            )
        
        with col2:
            subtitle_language = st.selectbox(
                "Bahasa Video",
                options=['id', 'en'],
                format_func=lambda x: "Indonesia" if x == 'id' else "English",
                key="subtitle_lang_select"
            )
        
        if video_for_subtitle and st.button("🎤 Extract Teks dari Video", key="extract_subtitle_btn"):
            with st.spinner("🔊 Menganalisis audio video..."):
                transcribed_text = speech_to_text.transcribe_video(video_for_subtitle, subtitle_language)
                
                if transcribed_text:
                    st.success("✅ Teks berhasil diekstrak dari video!")
                    st.text_area("Teks yang diekstrak:", value=transcribed_text, height=150, key="extracted_text")
                    
                    # Auto-fill ke story text jika user mau
                    if st.button("💾 Gunakan Teks Ini untuk Video", key="use_extracted_text"):
                        st.session_state.story_text = transcribed_text
                        st.session_state.story_generated = True
                        st.success("✅ Teks sudah disimpan! Lanjut ke Generate Video.")
                        st.rerun()
                else:
                    st.error("❌ Gagal mengekstrak teks dari video")
        
        st.markdown("---")
        st.subheader("📁 Upload Media untuk Video")
        
        uploaded_files = st.file_uploader(
            "Pilih gambar atau video untuk background",
            type=['jpg', 'jpeg', 'png', 'mp4', 'mov', 'avi'],
            accept_multiple_files=True,
            help="Upload beberapa file untuk video yang lebih menarik",
            key="file_uploader_main"
        )
        
        if uploaded_files:
            st.success(f"✅ {len(uploaded_files)} file berhasil diupload")
            st.session_state.uploaded_files = uploaded_files
            
            # Show preview
            cols = st.columns(3)
            for i, file in enumerate(uploaded_files):
                col = cols[i % 3]
                with col:
                    if file.type.startswith('image'):
                        st.image(file, use_column_width=True, caption=file.name)
                    else:
                        st.video(file)
                    st.caption(f"{file.name} ({file.type})")
