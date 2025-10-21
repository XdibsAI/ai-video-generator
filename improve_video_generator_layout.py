#!/bin/bash

# Perbaiki layout video generator
python3 << 'PYTHONCODE'
import re

with open('apps/main.py', 'r') as f:
    content = f.read()

# Perbaiki bagian awal render_video_generator untuk layout yang lebih baik
new_video_generator_start = '''    def render_video_generator(self, settings):
        """Render video generation section dengan layout yang terorganisir"""
        self.ensure_session_state()
        
        st.header("🎬 Generate Video")
        
        # System capability check dalam container yang rapi
        with st.container():
            st.subheader("🔧 System Check")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if TTS_AVAILABLE:
                    st.success("✅ **TTS Ready**")
                else:
                    st.error("❌ **TTS Missing**")
                    st.caption("pip install gtts")
            
            with col2:
                if MOVIEPY_AVAILABLE:
                    st.success("✅ **MoviePy Ready**")
                else:
                    st.error("❌ **MoviePy Missing**") 
                    st.caption("pip install moviepy")
            
            with col3:
                if check_ffmpeg():
                    st.success("✅ **FFmpeg Ready**")
                else:
                    st.error("❌ **FFmpeg Missing**")
                    st.caption("sudo apt install ffmpeg")
        
        # Check content availability
        has_content = self.safe_session_get('story_generated') or self.safe_session_get('auto_subtitle_used')
        
        if not has_content:
            st.error("""
            ⚠️ **Belum ada konten untuk video!**
            
            Silakan pilih salah satu:
            - 📁 **Tab Upload Media**: Upload video dengan audio untuk auto-subtitle
            - 📖 **Tab Generate Cerita**: Buat cerita baru dengan AI
            """)
            return
        
        # Main content dalam tabs
        tab1, tab2, tab3 = st.tabs(["🎨 Efek Teks", "🎯 Mode Video", "🚀 Generate"])
        
        with tab1:
            selected_effect = self.render_text_effects_section()
        
        with tab2:
            self._render_video_mode_selection(settings)
        
        with tab3:
            self._render_video_generation_section(settings, selected_effect)'''

# Cari dan ganti bagian awal render_video_generator
old_start_pattern = r'def render_video_generator\(self, settings\):.*?return'
content = re.sub(old_start_pattern, new_video_generator_start, content, flags=re.DOTALL)

# Tambahkan method baru untuk mode selection
mode_selection_method = '''
    
    def _render_video_mode_selection(self, settings):
        """Render video mode selection section"""
        st.subheader("🎯 Pilih Mode Video")
        
        # Determine available modes based on uploaded content
        has_video_with_audio = self.safe_session_get('auto_subtitle_used')
        has_other_media = self.safe_session_get('uploaded_files') or self.safe_session_get('other_media_files')
        
        mode_options = []
        mode_descriptions = {}
        
        if has_video_with_audio:
            mode_options.append('add_text_to_video')
            mode_descriptions['add_text_to_video'] = "🎬 Tambah Teks ke Video Existing"
        
        if has_other_media or not has_video_with_audio:
            mode_options.append('video')
            mode_descriptions['video'] = "🎬 Video Baru dengan Media"
        
        mode_options.append('text_only')
        mode_descriptions['text_only'] = "📝 Teks Karaoke Only"
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            video_mode = st.radio(
                "Pilih jenis video:",
                options=mode_options,
                format_func=lambda x: mode_descriptions[x],
                index=0,
                key="video_mode_radio"
            )
            self.safe_session_set('video_mode', video_mode)
        
        with col2:
            if video_mode == 'add_text_to_video':
                st.success("**🎬 Mode: Tambah Teks ke Video Existing**")
                st.info("""
                - ✅ Gunakan video yang sudah diupload
                - ✅ Teks karaoke sync dengan audio original  
                - ✅ Hasil: Video sama + teks subtitle
                - ✅ Perfect untuk video narasi yang butuh teks
                """)
            elif video_mode == 'video':
                st.success("**🎬 Mode: Video Baru dengan Media**")
                st.info("""
                - ✅ Buat video baru dengan media yang diupload
                - ✅ Teks karaoke dengan audio TTS
                - ✅ Cocok untuk content baru
                - ✅ Support gambar dan video background
                """)
            else:
                st.success("**📝 Mode: Teks Karaoke Only**")
                st.info("""
                - ✅ Background hitam polos
                - ✅ Fokus pada teks karaoke
                - ✅ Cocok untuk lyric video atau quotes
                - ✅ Lebih cepat render
                """)
        
        # Karaoke info box
        st.markdown("""
        <div style="background: linear-gradient(45deg, #667eea, #764ba2); color: white; padding: 1.5rem; border-radius: 10px; margin: 1rem 0;">
        <h4 style="margin: 0 0 1rem 0;">🎤 Fitur Karaoke Aktif</h4>
        <p style="margin: 0.5rem 0;"><strong>✨ Teks akan muncul kata demi kata sesuai timing audio!</strong></p>
        <ul style="margin: 0.5rem 0; padding-left: 1.5rem;">
            <li>✅ Sync sempurna dengan suara narasi</li>
            <li>✅ Efek typewriter real-time</li>
            <li>✅ Posisi teks dapat disesuaikan</li>
            <li>✅ Multiple text effects available</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)
    
    def _render_video_generation_section(self, settings, selected_effect):
        """Render video generation controls"""
        st.subheader("🚀 Generate Video")
        
        # Content summary
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**📊 Konten Summary:**")
            if self.safe_session_get('auto_subtitle_used'):
                st.success("✅ **Sumber:** Auto-subtitle dari video")
                word_count = len(self.safe_session_get('story_text', '').split())
                st.info(f"**{word_count}** kata diekstrak dari audio")
            else:
                st.success("✅ **Sumber:** Cerita AI-generated")
                word_count = len(self.safe_session_get('story_text', '').split())
                st.info(f"**{word_count}** kata dalam cerita")
        
        with col2:
            st.write("**⚙️ Settings:**")
            st.caption(f"🎯 **Mode:** {self.safe_session_get('video_mode', 'video')}")
            st.caption(f"🎨 **Efek:** {selected_effect}")
            st.caption(f"⏱️ **Durasi:** {settings['duration']} detik")
            st.caption(f"📐 **Format:** {settings['video_format']}")
        
        # Generate button
        st.markdown("---")
        
        # Dynamic button text based on mode
        button_texts = {
            'add_text_to_video': "🚀 GENERATE - Tambah Teks ke Video",
            'video': "🚀 GENERATE - Video Baru dengan Karaoke", 
            'text_only': "🚀 GENERATE - Teks Karaoke Only"
        }
        
        generate_clicked = st.button(
            button_texts.get(self.safe_session_get('video_mode'), "🚀 GENERATE VIDEO"),
            use_container_width=True,
            type="primary",
            key="generate_video_btn_main"
        )
        
        if generate_clicked:
            self._generate_video_process(settings, selected_effect)'''

# Tambahkan method baru setelah render_text_effects_section
if 'def render_text_effects_section' in content:
    # Cari akhir method render_text_effects_section
    effects_end = content.find('def render_', content.find('def render_text_effects_section') + 1)
    if effects_end != -1:
        content = content[:effects_end] + mode_selection_method + '\\n\\n' + content[effects_end:]

with open('apps/main.py', 'w') as f:
    f.write(content)

print("✅ Layout video generator diperbaiki")
PYTHONCODE
