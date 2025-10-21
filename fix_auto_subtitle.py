#!/bin/bash

# Update bagian auto-subtitle di main.py
python3 << 'PYTHONCODE'
import re

with open('apps/main.py', 'r') as f:
    content = f.read()

# Perbaiki bagian auto-subtitle untuk lebih jelas
old_auto_subtitle_section = '''        # ✅ AUTO SUBTITLE SECTION
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
                    st.error("❌ Gagal mengekstrak teks dari video")'''

new_auto_subtitle_section = '''        # ✅ AUTO SUBTITLE SECTION - BUAT TEKS DARI VIDEO YANG SUDAH ADA AUDIO
        st.subheader("🎤 Auto Subtitle: Buat Teks dari Video yang Ada Audio")
        
        st.info("""
        **Fitur ini untuk:** Video yang sudah ada audio tapi belum ada teks/subtitle
        **Cara kerja:** 
        1. Upload video yang ada audionya
        2. Sistem akan extract audio dan convert ke teks
        3. Hasil teks bisa langsung digunakan untuk video baru dengan karaoke
        """)
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            video_for_subtitle = st.file_uploader(
                "📹 Upload video yang sudah ada audio (tanpa teks)",
                type=['mp4', 'mov', 'avi', 'mkv'],
                help="Pilih video yang audionya ingin dijadikan teks otomatis",
                key="subtitle_video_uploader"
            )
        
        with col2:
            subtitle_language = st.selectbox(
                "🗣️ Bahasa dalam Audio",
                options=['id', 'en'],
                format_func=lambda x: "Indonesia" if x == 'id' else "English",
                key="subtitle_lang_select"
            )
        
        if video_for_subtitle:
            st.success(f"✅ Video '{video_for_subtitle.name}' siap untuk extract teks")
            
            if st.button("🎤 Extract Teks dari Audio Video", key="extract_subtitle_btn", type="primary"):
                with st.spinner("🔊 Menganalisis audio dan mengconvert ke teks..."):
                    try:
                        transcribed_text = speech_to_text.transcribe_video(video_for_subtitle, subtitle_language)
                        
                        if transcribed_text and len(transcribed_text.strip()) > 10:
                            st.success("✅ Teks berhasil diekstrak dari audio video!")
                            
                            # Show word count
                            word_count = len(transcribed_text.split())
                            st.info(f"📊 **{word_count} kata** diekstrak dari audio")
                            
                            # Preview extracted text
                            st.subheader("📝 Teks yang Berhasil Diekstrak:")
                            edited_text = st.text_area(
                                "Edit teks jika diperlukan:",
                                value=transcribed_text,
                                height=200,
                                key="extracted_text_editor"
                            )
                            
                            col1, col2 = st.columns(2)
                            with col1:
                                if st.button("💾 Gunakan Teks Ini", key="use_extracted_text", use_container_width=True):
                                    st.session_state.story_text = edited_text
                                    st.session_state.story_generated = True
                                    st.session_state.auto_subtitle_used = True
                                    st.success("✅ Teks sudah disimpan! Sekarang bisa lanjut ke Generate Video.")
                                    st.rerun()
                            
                            with col2:
                                if st.button("📥 Download Teks", key="download_extracted_text", use_container_width=True):
                                    st.download_button(
                                        label="💾 Download sebagai TXT",
                                        data=edited_text,
                                        file_name=f"extracted_text_{video_for_subtitle.name}.txt",
                                        mime="text/plain"
                                    )
                        else:
                            st.error("❌ Gagal mengekstrak teks dari audio. Pastikan video memiliki audio yang jelas.")
                            
                    except Exception as e:
                        st.error(f"❌ Error saat extract teks: {str(e)}")
                        st.info("💡 Pastikan file video tidak corrupt dan memiliki audio yang jelas")'''

# Replace the section
content = content.replace(old_auto_subtitle_section, new_auto_subtitle_section)

with open('apps/main.py', 'w') as f:
    f.write(content)

print("✅ Fitur auto-subtitle diperbaiki dan ditingkatkan")
PYTHONCODE
