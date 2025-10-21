import streamlit as st
import os
import uuid
from datetime import datetime
from utils.ffmpeg_checker import check_ffmpeg, setup_ffmpeg_warning
from utils.story_generator import StoryGenerator
from utils.tts_handler import generate_tts_sync, TTS_AVAILABLE, get_supported_languages
from utils.video_editor import VideoEditor, MOVIEPY_AVAILABLE
from utils.speech_to_text import speech_to_text
from utils.content_optimizer import content_optimizer
from utils.text_effects import get_text_effect_config, preview_text_effect

# Initialize session state
if 'story_generated' not in st.session_state:
    st.session_state.story_generated = False
if 'story_options' not in st.session_state:
    st.session_state.story_options = []
if 'selected_story_index' not in st.session_state:
    st.session_state.selected_story_index = 0
if 'story_text' not in st.session_state:
    st.session_state.story_text = ""
if 'uploaded_files' not in st.session_state:
    st.session_state.uploaded_files = []
if 'audio_path' not in st.session_state:
    st.session_state.audio_path = None
if 'video_path' not in st.session_state:
    st.session_state.video_path = None
if 'background_music_path' not in st.session_state:
    st.session_state.background_music_path = None
if 'optimized_content' not in st.session_state:
    st.session_state.optimized_content = None
if 'video_mode' not in st.session_state:
    st.session_state.video_mode = 'video'
if 'selected_text_effect' not in st.session_state:
    st.session_state.selected_text_effect = 'none'

# Initialize story generator
story_generator = StoryGenerator()

class VideoGeneratorApp:
    def __init__(self):
        pass

    def render_file_upload(self):
        """Render file upload section"""
        st.header("📁 Upload Media")
        uploaded_files = st.file_uploader(
            "Upload gambar atau video",
            accept_multiple_files=True,
            type=['jpg', 'jpeg', 'png', 'mp4', 'mov'],
            key="media_uploader"
        )

        if uploaded_files:
            st.session_state.uploaded_files = uploaded_files
            st.success(f"✅ {len(uploaded_files)} file diupload!")
            
            for file in uploaded_files:
                if file.type.startswith('image'):
                    st.image(file, caption=file.name, width=200)
                else:
                    st.video(file)

        # Background music upload
        background_music = st.file_uploader(
            "Upload musik latar (opsional)",
            type=['mp3', 'wav'],
            key="background_music_uploader"
        )
        
        if background_music:
            temp_music_path = os.path.join("temp", f"music_{uuid.uuid4().hex[:8]}_{background_music.name}")
            os.makedirs("temp", exist_ok=True)
            with open(temp_music_path, 'wb') as f:
                f.write(background_music.getvalue())
            st.session_state.background_music_path = temp_music_path
            st.success("✅ Musik latar diupload!")

    def render_text_effects_section(self):
        """Render text effects selection section"""
        effect_options = ['none', 'glow', 'neon', 'shadow', 'gradient', 'outline', 'retro', 'elegant', 'fire', 'ice']
        
        st.subheader("🎨 Pilih Efek Teks")
        selected_effect = st.selectbox(
            "Pilih efek teks untuk subtitle karaoke:",
            options=effect_options,
            format_func=lambda x: get_text_effect_config(x)['name'],
            key="text_effect_select"
        )
        
        if selected_effect:
            st.session_state.selected_text_effect = selected_effect
            preview_text_effect(selected_effect, "Contoh Teks Karaoke", font_size=40)
        
        return selected_effect

    def render_story_generator(self, settings):
        """Render story generator section"""
        st.header("📖 Generate Cerita")
        
        if not hasattr(story_generator, 'api_key') or not story_generator.api_key:
            st.error("❌ API key untuk story generation tidak ditemukan. Pastikan file .env diatur dengan benar.")
            return

        with st.form(key="story_form"):
            prompt = st.text_area(
                "Masukkan prompt untuk cerita:",
                placeholder="Contoh: Fakta menarik tentang kereta",
                height=100,
                key="story_prompt"
            )
            
            generate_clicked = st.form_submit_button("✨ Generate Cerita")
            
            if generate_clicked and prompt:
                try:
                    # Generate three story options using StoryGenerator
                    stories = story_generator.generate_stories(
                        niche=settings['niche'],
                        duration_seconds=settings['duration'],
                        style='Fakta Menarik',  # Default style, adjust as needed
                        language=settings['language'],
                        user_description=prompt
                    )
                    
                    if stories and len(stories) >= 1:
                        st.session_state.story_options = stories
                        st.session_state.story_text = stories[0]
                        st.session_state.selected_story_index = 0
                        st.session_state.story_generated = True
                        st.success(f"✅ {len(stories)} cerita berhasil digenerate!")
                    else:
                        st.error("❌ Gagal generate cerita")
                
                except Exception as e:
                    st.error(f"❌ Error generating cerita: {str(e)}")
                    import traceback
                    st.error(f"Detail error: {traceback.format_exc()}")

        if st.session_state.story_generated and st.session_state.story_options:
            st.subheader("📚 Pilih Cerita")
            
            for i, story in enumerate(st.session_state.story_options):
                is_selected = st.session_state.selected_story_index == i
                
                with st.form(key=f"story_form_{i}"):
                    col1, col2 = st.columns([1, 4])
                    
                    with col1:
                        st.radio(
                            "Pilih opsi:",
                            options=[f"opsi_{i}"],
                            key=f"story_radio_{i}",
                            index=0 if is_selected else None
                        )
                    
                    with col2:
                        css_class = "story-option selected" if is_selected else "story-option"
                        st.markdown(f'<div class="{css_class}">{story[:200]}...</div>', unsafe_allow_html=True)
                    
                    story_submitted = st.form_submit_button("✅ Pilih Cerita Ini")
                    
                    if story_submitted:
                        if st.session_state.get(f"story_radio_{i}") == f"opsi_{i}":
                            if st.session_state.selected_story_index != i:
                                st.session_state.selected_story_index = i
                                st.session_state.story_text = st.session_state.story_options[i]
                                st.rerun()
            
            st.subheader("✏️ Edit Cerita yang Dipilih")
            
            with st.form(key="story_edit_form"):
                edited_story = st.text_area(
                    "Edit cerita sesuai keinginanmu:",
                    value=st.session_state.story_text,
                    height=200,
                    key="story_editor_main"
                )
                
                save_clicked = st.form_submit_button("💾 Simpan Perubahan")
                
                if save_clicked:
                    if edited_story != st.session_state.story_text:
                        st.session_state.story_text = edited_story
                        st.session_state.story_options[st.session_state.selected_story_index] = edited_story
                        st.success("✅ Perubahan disimpan!")
            
            word_count = len(st.session_state.story_text.split())
            try:
                from utils.tts_handler import estimate_audio_duration
                estimated_duration = estimate_audio_duration(st.session_state.story_text, settings['language'])
                st.caption(f"📊 **{word_count} kata** (Estimasi audio: {estimated_duration:.1f}s)")
            except:
                st.caption(f"📊 **{word_count} kata**")

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
            st.error("❌ FFmpeg tidak tersedia. Silakan instal FFmpeg.")
            setup_ffmpeg_warning()
            return
        
        # Text effects section
        st.subheader("🎨 Pilih Efek Teks")
        selected_effect = self.render_text_effects_section()
        
        # Auto subtitle option
        has_video_upload = any(f.type.startswith('video') for f in st.session_state.uploaded_files) if st.session_state.uploaded_files else False
        
        if has_video_upload:
            st.subheader("🎤 Opsi Subtitle Otomatis")
            auto_subtitle = st.checkbox(
                "Gunakan teks dari audio video yang diupload",
                help="Ekstrak teks otomatis dari audio video dan gunakan sebagai subtitle",
                key="auto_subtitle_checkbox"
            )
            
            if auto_subtitle:
                st.info("ℹ️ Teks akan diekstrak dari audio video dan digunakan sebagai narasi")
        else:
            auto_subtitle = False
        
        # Mode selection
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
        
        # Validate requirements
        if video_mode == 'video' and not st.session_state.uploaded_files:
            st.warning("⚠️ Untuk mode Video, silakan upload file media terlebih dahulu")
            return
        
        if not st.session_state.story_generated and not auto_subtitle:
            st.warning("⚠️ Silakan generate cerita atau aktifkan auto-subtitle terlebih dahulu")
            return
        
        # Info karaoke
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
                audio_path = None
                transcribed_text = None
                
                if auto_subtitle and has_video_upload:
                    # Use audio from uploaded video
                    status_text.text("🔊 Mengekstrak audio dari video yang diunggah...")
                    video_file = next(f for f in st.session_state.uploaded_files if f.type.startswith('video'))
                    
                    # Extract audio from video
                    import tempfile
                    temp_video_path = os.path.join(tempfile.gettempdir(), f"temp_video_{uuid.uuid4().hex[:8]}_{video_file.name}")
                    with open(temp_video_path, 'wb') as f:
                        f.write(video_file.getvalue())
                    
                    from moviepy.editor import VideoFileClip
                    video_clip = VideoFileClip(temp_video_path)
                    if video_clip.audio:
                        audio_path = os.path.join(tempfile.gettempdir(), f"extracted_audio_{uuid.uuid4().hex[:8]}.mp3")
                        video_clip.audio.write_audiofile(audio_path, codec='mp3', verbose=False, logger=None)
                    else:
                        st.error("❌ Video tidak memiliki audio untuk transkripsi")
                        video_clip.close()
                        return
                    
                    video_clip.close()
                    
                    # Extract text from video audio
                    status_text.text("🎤 Mengekstrak teks dari audio video...")
                    transcribed_text = speech_to_text.transcribe_video(video_file, settings['language'])
                    if transcribed_text:
                        st.session_state.story_text = transcribed_text
                        st.success(f"✅ Berhasil mengekstrak {len(transcribed_text)} karakter dari video")
                    else:
                        st.error("❌ Gagal mengekstrak teks dari audio video")
                        return
                
                else:
                    # Generate TTS seperti biasa
                    status_text.text("🔊 Menghasilkan narasi audio...")
                    audio_path = generate_tts_sync(st.session_state.story_text, settings['language'])
                
                progress_bar.progress(33)
                
                if not audio_path or not os.path.exists(audio_path):
                    st.error("❌ Gagal mendapatkan audio")
                    return
                
                st.session_state.audio_path = audio_path
                
                status_text.text("🎬 Langkah 2: Membuat video dengan karaoke...")
                
                # Use the selected mode dengan auto-subtitle dan effects
                video_path = VideoEditor().create_video(
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
                    text_effect=selected_effect
                )
                progress_bar.progress(66)
                
                if not video_path or not os.path.exists(video_path):
                    st.error("❌ Gagal generate video")
                    return
                
                st.session_state.video_path = video_path
                st.session_state.video_mode = video_mode
                
                status_text.text("📊 Langkah 3: Mengoptimasi konten...")
                try:
                    st.session_state.optimized_content = content_optimizer.optimize_content(
                        st.session_state.story_text,
                        settings['niche'],
                        settings['language']
                    )
                except Exception as e:
                    st.warning(f"⚠️ Gagal mengoptimasi konten: {str(e)}")
                    st.session_state.optimized_content = {
                        'title': 'Generated Video',
                        'description': st.session_state.story_text[:100] + '...',
                        'hooks': ['Watch this amazing video!'],
                        'hashtags': ['video', 'content'],
                        'optimal_posting_times': []
                    }
                
                progress_bar.progress(100)
                
                mode_name = "Video dengan Media" if video_mode == 'video' else "Teks Karaoke Only"
                subtitle_source = "otomatis dari video" if auto_subtitle else "teks yang disediakan"
                status_text.text(f"✅ {mode_name} dengan subtitle {subtitle_source} berhasil di-generate!")
                
                st.balloons()
                
            except Exception as e:
                st.error(f"❌ Error generating video: {str(e)}")
                import traceback
                st.error(f"Detail error: {traceback.format_exc()}")
                progress_bar.progress(0)

    def render_results(self):
        """Render results section"""
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
                    st.error(f"❌ Error memuat preview video: {str(e)}")
            else:
                st.error("❌ File video tidak ditemukan")
        
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
                    st.warning(f"Audio tidak tersedia: {str(e)}")

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

    def render_sidebar(self):
        """Render sidebar for settings"""
        with st.sidebar:
            st.header("⚙️ Pengaturan")
            
            settings = {
                'niche': st.selectbox(
                    "Pilih niche konten:",
                    ['Fakta Menarik', 'Motivasi', 'Edukasi', 'Hiburan'],
                    key="niche_select"
                ),
                'language': st.selectbox(
                    "Pilih bahasa:",
                    ['id', 'en', 'es', 'fr', 'de', 'ja', 'ko', 'zh'],
                    format_func=lambda x: get_supported_languages().get(x, 'Indonesian'),
                    key="language_select"
                ),
                'duration': st.slider(
                    "Durasi video (detik):",
                    min_value=10,
                    max_value=120,
                    value=30,
                    step=10,
                    key="duration_slider"
                ),
                'video_format': st.selectbox(
                    "Rasio aspek video:",
                    ['short', 'standard'],
                    index=0,  # Default to 'short' (9:16)
                    format_func=lambda x: "Vertikal (9:16)" if x == 'short' else "Horizontal (16:9)",
                    key="video_format_select"
                ),
                'font_size': st.slider(
                    "Ukuran font subtitle:",
                    min_value=20,
                    max_value=60,
                    value=40,
                    step=5,
                    key="font_size_slider"
                ),
                'text_color': st.color_picker(
                    "Warna teks subtitle:",
                    value="#FFFFFF",
                    key="text_color_picker"
                ),
                'text_position': st.selectbox(
                    "Posisi teks subtitle:",
                    ['bottom', 'center', 'top'],
                    key="text_position_select"
                ),
                'music_volume': st.slider(
                    "Volume musik latar:",
                    min_value=0.0,
                    max_value=1.0,
                    value=0.2,
                    step=0.1,
                    key="music_volume_slider"
                )
            }
            return settings

    def run(self):
        """Main application runner"""
        
        # Check system dependencies
        if not check_ffmpeg():
            setup_ffmpeg_warning()
        
        self.render_header()
        settings = self.render_sidebar()
        
        tab1, tab2, tab3, tab4 = st.tabs(["📁 Upload Media", "📖 Generate Cerita", "🎬 Buat Video", "📊 Hasil"])
        
        with tab1:
            self.render_file_upload()
        with tab2:
            self.render_story_generator(settings)
        with tab3:
            self.render_video_generator(settings)
        with tab4:
            self.render_results()

if __name__ == "__main__":
    app = VideoGeneratorApp()
    app.run()
