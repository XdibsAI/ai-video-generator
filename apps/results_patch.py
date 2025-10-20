    def render_results(self):
        """Render results section dengan mode info"""
        if not st.session_state.get('video_path'):
            return
        
        st.header("🎉 Hasil Video")
        
        # Show mode info
        video_mode = st.session_state.get('video_mode', 'video')
        mode_name = "Video dengan Media" if video_mode == 'video' else "Teks Karaoke Only"
        
        st.success(f"✅ {mode_name} berhasil dibuat!")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("📺 Preview Video")
            
            if os.path.exists(st.session_state.video_path):
                try:
                    with open(st.session_state.video_path, 'rb') as video_file:
                        video_bytes = video_file.read()
                    st.video(video_bytes)
                    
                    if video_mode == 'text_only':
                        st.info("🎤 **Teks Karaoke Only:** Fokus pada teks dengan background hitam")
                    else:
                        st.info("🎤 **Fitur Karaoke:** Teks muncul kata demi kata sync dengan audio")
                    
                    # Download button for video
                    st.download_button(
                        label="📥 Download Video MP4",
                        data=video_bytes,
                        file_name=f"{'text_karaoke' if video_mode == 'text_only' else 'video'}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4",
                        mime="video/mp4",
                        use_container_width=True,
                        key="download_video_btn"
                    )
                except Exception as e:
                    st.error(f"❌ Error loading video preview: {e}")
            else:
                st.error("❌ Video file not found")
        
        with col2:
            st.subheader("📄 Download Assets")
            
            # Content assets download
            if st.session_state.story_text:
                combined_content = f"""VIDEO CONTENT ASSETS

MODE: {mode_name}

CERITA NARASI:
{st.session_state.story_text}

"""
                if st.session_state.optimized_content:
                    combined_content += f"""OPTIMASI KONTEN:
Judul: {st.session_state.optimized_content.get('title', 'Generated Video')}

Deskripsi:
{st.session_state.optimized_content.get('description', 'No description')}

Video Hooks:
{chr(10).join([f"{i+1}. {hook}" for i, hook in enumerate(st.session_state.optimized_content.get('hooks', []))])}

Hashtags:
{' '.join([f'#{tag}' for tag in st.session_state.optimized_content.get('hashtags', [])])}

Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
                
                st.download_button(
                    label="📋 Download Cerita + Optimasi",
                    data=combined_content,
                    file_name=f"content_assets_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    mime="text/plain",
                    use_container_width=True,
                    key="download_content_btn"
                )
            
            if st.session_state.audio_path and os.path.exists(st.session_state.audio_path):
                try:
                    with open(st.session_state.audio_path, "rb") as f:
                        audio_bytes = f.read()
                    
                    st.download_button(
                        label="🔊 Download Audio Narasi",
                        data=audio_bytes,
                        file_name=f"audio_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp3",
                        mime="audio/mpeg",
                        use_container_width=True,
                        key="download_audio_btn"
                    )
                except Exception as e:
                    st.warning(f"Audio tidak tersedia: {e}")
