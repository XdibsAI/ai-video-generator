#!/bin/bash

# Buat workflow langsung dari upload video ke generate video
python3 << 'PYTHONCODE'
import re

with open('apps/main.py', 'r') as f:
    content = f.read()

# Hapus bagian auto-subtitle yang lama dan ganti dengan yang langsung
old_upload_section = '''    def render_file_upload(self):
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
        )'''

new_upload_section = '''    def render_file_upload(self):
        """Render file upload section dengan direct auto-subtitle to video"""
        st.header("📁 Upload Video dengan Audio (Auto Subtitle)")
        
        st.info("""
        **Workflow Cepat:**
        1. Upload video yang sudah ada audio
        2. Sistem otomatis extract teks dari audio  
        3. Langsung ke tab Generate Video dengan efek teks
        *Tidak perlu melalui Generate Cerita*
        """)
        
        # ✅ DIRECT AUTO-SUBTITLE TO VIDEO WORKFLOW
        st.subheader("🎬 Upload Video untuk Auto Subtitle")
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            video_with_audio = st.file_uploader(
                "📹 Upload video yang sudah ada audio",
                type=['mp4', 'mov', 'avi', 'mkv', 'webm'],
                help="Pilih video yang audionya ingin dijadikan teks otomatis",
                key="video_with_audio_uploader"
            )
        
        with col2:
            audio_language = st.selectbox(
                "🗣️ Bahasa Audio",
                options=['id', 'en'],
                format_func=lambda x: "Indonesia" if x == 'id' else "English",
                key="audio_lang_select"
            )
        
        if video_with_audio:
            st.success(f"✅ Video '{video_with_audio.name}' siap diproses")
            
            # Show video preview
            st.video(video_with_audio)
            
            # Auto process button
            if st.button("🚀 Auto Process Video + Generate Subtitle", type="primary", use_container_width=True):
                with st.spinner("🔊 Mengekstrak teks dari audio video..."):
                    try:
                        transcribed_text = speech_to_text.transcribe_video(video_with_audio, audio_language)
                        
                        if transcribed_text and len(transcribed_text.strip()) > 10:
                            # Simpan semua data untuk video generator
                            st.session_state.uploaded_files = [video_with_audio]
                            st.session_state.story_text = transcribed_text
                            st.session_state.story_generated = True
                            st.session_state.auto_subtitle_used = True
                            st.session_state.video_with_audio = video_with_audio
                            st.session_state.audio_language = audio_language
                            
                            word_count = len(transcribed_text.split())
                            st.success(f"✅ Berhasil ekstrak {word_count} kata dari audio!")
                            
                            # Show extracted text
                            st.subheader("📝 Teks yang Diekstrak:")
                            st.text_area(
                                "Teks dari audio video:",
                                value=transcribed_text,
                                height=150,
                                key="auto_extracted_text",
                                disabled=True
                            )
                            
                            st.info("🎯 **Langsung ke tab 'Buat Video' untuk generate video dengan efek teks!**")
                            
                        else:
                            st.error("❌ Tidak bisa mengekstrak teks dari audio. Pastikan video memiliki audio yang jelas.")
                            
                    except Exception as e:
                        st.error(f"❌ Error saat memproses video: {str(e)}")
        
        st.markdown("---")
        st.subheader("📁 Upload Media Lainnya (Opsional)")
        
        st.info("Upload gambar atau video tambahan untuk background (jika tidak menggunakan video audio)")
        
        other_media_files = st.file_uploader(
            "Pilih gambar atau video untuk background",
            type=['jpg', 'jpeg', 'png', 'mp4', 'mov', 'avi'],
            accept_multiple_files=True,
            help="Upload media tambahan untuk variasi video",
            key="other_media_uploader"
        )
        
        if other_media_files:
            st.session_state.other_media_files = other_media_files
            st.success(f"✅ {len(other_media_files)} file media tambahan diupload")'''

# Replace the section
content = content.replace(old_upload_section, new_upload_section)

with open('apps/main.py', 'w') as f:
    f.write(content)

print("✅ Workflow auto-subtitle langsung ke video telah dibuat")
PYTHONCODE
