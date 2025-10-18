import streamlit as st
import os
import sys
import json
from datetime import datetime

# ✅ SET PAGE_CONFIG PALING AWAL
st.set_page_config(
    page_title="AI Video Generator",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ✅ IMPORT SETELAH PAGE_CONFIG
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.insert(0, project_root)

try:
    from config.settings import *
    from utils.story_generator import story_generator
    from utils.tts_handler import generate_tts_sync
    from utils.video_editor import video_editor, MOVIEPY_AVAILABLE
    from utils.content_optimizer import content_optimizer
    from utils.cleanup import cleanup_manager
    from utils.compatibility import check_ffmpeg, estimate_word_count
    
    print("✅ All imports successful!")
except ImportError as e:
    st.error(f"❌ Import Error: {e}")
    # Fallback functions jika import gagal
    def check_ffmpeg():
        st.error("❌ FFmpeg check tidak tersedia")
        return False
    
    def estimate_word_count(duration_seconds):
        return (50, 100)

# ✅ CEK .ENV FILE DAN LOAD API KEY
def load_api_key():
    """Load API key dari .env file dengan debugging"""
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        api_key = os.getenv('OPENROUTER_API_KEY')
        print(f"🔑 API Key dari .env: {api_key[:10]}..." if api_key and api_key != "your_actual_openrouter_api_key_here" else "❌ API Key tidak valid")
        
        if api_key and api_key != "your_actual_openrouter_api_key_here":
            story_generator.api_key = api_key
            return True
        else:
            return False
    except Exception as e:
        print(f"❌ Error loading API key: {e}")
        return False

# ✅ LOAD API KEY SAAT APLIKASI DIMULAI
api_key_loaded = load_api_key()

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        background: linear-gradient(45deg, #FF6B6B, #4ECDC4);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 2rem;
    }
    .story-option {
        padding: 1rem;
        border: 2px solid #e0e0e0;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    .story-option:hover {
        border-color: #4ECDC4;
        background-color: #f8ffff;
    }
    .story-option.selected {
        border-color: #FF6B6B;
        background-color: #fff0f0;
    }
    .karaoke-info {
        background: linear-gradient(45deg, #667eea, #764ba2);
        color: white;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .api-status {
        padding: 0.5rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .api-success {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
    }
    .api-error {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
    }
</style>
""", unsafe_allow_html=True)

class VideoGeneratorApp:
    def __init__(self):
        self.setup_session_state()
    
    def setup_session_state(self):
        """Initialize session state variables"""
        if 'initialized' not in st.session_state:
            st.session_state.initialized = True
            st.session_state.story_generated = False
            st.session_state.story_options = []
            st.session_state.selected_story_index = 0
            st.session_state.story_text = ""
            st.session_state.audio_path = None
            st.session_state.video_path = None
            st.session_state.uploaded_files = []
            st.session_state.optimized_content = None
            st.session_state.selected_color = "#FFFFFF"
            st.session_state.background_music = None
    
    def render_sidebar(self):
        """Render sidebar dengan informasi karaoke"""
        with st.sidebar:
            st.title("⚙️ Pengaturan Video")
            
            # ✅ STATUS API KEY - DENGAN DEBUG INFO
            st.subheader("🔑 Status API")
            
            # Cek status API key
            api_key = getattr(story_generator, 'api_key', None)
            has_valid_api = api_key and api_key != "your_actual_openrouter_api_key_here"
            
            if has_valid_api:
                st.markdown('<div class="api-status api-success">✅ API Key Ready</div>', unsafe_allow_html=True)
                st.info(f"Model: {getattr(story_generator, 'model', 'x-ai/grok-4-fast')}")
            else:
                st.markdown('<div class="api-status api-error">❌ API Key Missing</div>', unsafe_allow_html=True)
                st.markdown("""
                **Setup API Key:**
                1. Edit file `.env` di root project
                2. Tambahkan line: `OPENROUTER_API_KEY=your_actual_api_key_here`
                3. Restart aplikasi
                
                **Dapatkan API Key:**
                - Kunjungi [OpenRouter](https://openrouter.ai/keys)
                - Buat account dan generate API key
                - Copy key ke file `.env`
                """)
                
                # Debug info
                with st.expander("🔧 Debug Info"):
                    st.write(f"API Key loaded: {api_key_loaded}")
                    st.write(f"Story Generator API Key: {api_key}")
                    try:
                        from dotenv import load_dotenv
                        load_dotenv()
                        env_key = os.getenv('OPENROUTER_API_KEY')
                        st.write(f".env API Key: {env_key}")
                        st.write(f".env file exists: {os.path.exists('.env')}")
                    except Exception as e:
                        st.write(f"Debug error: {e}")
            
            # ✅ STATUS MOVIEPY & KARAOKE
            st.subheader("🎬 Status Video")
            if MOVIEPY_AVAILABLE:
                st.success("✅ Video Processing Ready")
                st.markdown("""
                **🎤 Fitur Karaoke:**
                - Teks muncul kata demi kata
                - Sync dengan audio narration
                - Efek typewriter real-time
                """)
            else:
                st.error("❌ Video Processing Limited")
            
            st.subheader("📝 Konten Settings")
            
            niche = st.selectbox("🎯 Tema Konten", 
                               ["Fakta Menarik", "Motivasi", "Humor", "Petualangan", "Pendidikan"], 
                               index=0, key="niche_select")
            
            language = st.selectbox("🌍 Bahasa", ["id", "en"], 
                                  format_func=lambda x: "Indonesia" if x == "id" else "English", 
                                  index=0, key="language_select")
            
            duration = st.selectbox("⏱️ Durasi Video", [30, 60, 90], 
                                  format_func=lambda x: f"{x} detik", 
                                  index=0, key="duration_select")
            
            video_format = st.radio("📐 Format Video", ["short", "long"], 
                                  format_func=lambda x: "Short (9:16)" if x == "short" else "Long (16:9)", 
                                  index=0, key="format_radio")
            
            st.subheader("✍️ Pengaturan Teks")
            
            text_position = st.radio("📍 Posisi Teks", ["middle", "bottom"], 
                                   format_func=lambda x: "Tengah" if x == "middle" else "Bawah", 
                                   index=0, key="position_radio")
            
            font_size = st.slider("📏 Ukuran Font", 40, 100, 60, 5, key="font_slider")
            
            # Color picker
            text_color = st.selectbox(
                "🎨 Warna Teks",
                options=["#FFFFFF", "#FFD700", "#00FF00", "#FF4500", "#1E90FF", "#FF69B4"],
                format_func=lambda x: {
                    "#FFFFFF": "Putih ⚪",
                    "#FFD700": "Emas 🟡",
                    "#00FF00": "Hijau 🟢", 
                    "#FF4500": "Merah 🔴",
                    "#1E90FF": "Biru 🔵",
                    "#FF69B4": "Pink 🌸"
                }[x],
                index=0,
                key="color_select"
            )
            
            # ✅ BACKGROUND MUSIC UPLOAD
            st.subheader("🎵 Musik Latar")
            background_music = st.file_uploader(
                "Upload file audio (MP3/WAV)",
                type=['mp3', 'wav'],
                help="File audio untuk background music",
                key="bg_music_uploader"
            )
            
            if background_music:
                st.session_state.background_music = background_music
                st.success(f"✅ {background_music.name} uploaded")
            
            music_volume = st.slider("🔊 Volume Musik", 0.0, 1.0, 0.3, 0.1, key="volume_slider")
            
            user_description = st.text_area(
                "📝 Deskripsi Tambahan (Opsional)",
                placeholder="Jelaskan konten yang kamu inginkan...",
                height=80,
                key="desc_textarea"
            )
            
            return {
                'niche': niche, 'language': language, 'duration': duration, 
                'video_format': video_format, 'text_position': text_position, 
                'font_size': font_size, 'text_color': text_color, 
                'user_description': user_description, 'music_volume': music_volume
            }
    
    def render_file_upload(self):
        """Render file upload section"""
        st.header("📁 Upload Media")
        
        uploaded_files = st.file_uploader(
            "Pilih gambar atau video",
            type=['jpg', 'jpeg', 'png', 'mp4', 'mov', 'avi'],
            accept_multiple_files=True,
            help="Upload beberapa file untuk video yang lebih menarik",
            key="file_uploader_main"
        )
        
        if uploaded_files:
            st.success(f"✅ {len(uploaded_files)} file berhasil diupload")
            st.session_state.uploaded_files = uploaded_files
            
            for i, file in enumerate(uploaded_files):
                col1, col2 = st.columns([1, 4])
                with col1:
                    if file.type.startswith('image'):
                        st.image(file, width=80)
                    else:
                        st.video(file)
                with col2:
                    st.write(f"**{file.name}** ({file.type})")
    
    def render_story_generator(self, settings):
        """Render story generation section dengan 3 options"""
        st.header("📖 Generate Cerita (3 Pilihan)")
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            generate_clicked = st.button("🎭 Generate 3 Cerita Options", 
                                       use_container_width=True, 
                                       type="primary",
                                       key="generate_stories_btn")
        
        with col2:
            word_range = estimate_word_count(settings['duration'])
            st.info(f"**Target:**\n{word_range[0]}-{word_range[1]} kata")
        
        if generate_clicked:
            # Cek API key sebelum generate
            api_key = getattr(story_generator, 'api_key', None)
            has_valid_api = api_key and api_key != "your_actual_openrouter_api_key_here"
            
            if not has_valid_api:
                st.error("""
                ❌ API Key belum dikonfigurasi. 
                
                **Langkah perbaikan:**
                1. Edit file `.env` di folder project
                2. Tambahkan: `OPENROUTER_API_KEY=your_actual_api_key_here`
                3. Restart aplikasi
                4. Pastikan API key valid dari [OpenRouter](https://openrouter.ai/keys)
                """)
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
            
            with st.form(key="story_selection_form"):
                for i, story in enumerate(st.session_state.story_options):
                    is_selected = (i == st.session_state.selected_story_index)
                    
                    col1, col2 = st.columns([1, 20])
                    with col1:
                        radio_val = st.radio(
                            f"Pilih Opsi {i+1}",
                            [f"opsi_{i}"],
                            key=f"story_radio_{i}",
                            label_visibility="collapsed",
                            index=0 if is_selected else None
                        )
                    
                    with col2:
                        css_class = "story-option selected" if is_selected else "story-option"
                        st.markdown(f'<div class="{css_class}">{story[:200]}...</div>', unsafe_allow_html=True)
                
                story_submitted = st.form_submit_button("✅ Pilih Cerita Ini")
                
                if story_submitted:
                    for i in range(len(st.session_state.story_options)):
                        if st.session_state.get(f"story_radio_{i}") == f"opsi_{i}":
                            if st.session_state.selected_story_index != i:
                                st.session_state.selected_story_index = i
                                st.session_state.story_text = st.session_state.story_options[i]
                                break
            
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
            st.caption(f"📊 **{word_count} kata** (Estimasi audio: {word_count/2.5:.1f}s)")
    
    def render_video_generator(self, settings):
        """Render video generation section dengan info karaoke"""
        st.header("🎬 Generate Video")
        
        # ✅ INFO KARAOKE
        if MOVIEPY_AVAILABLE:
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
        else:
            st.warning("🎬 Mode Terbatas: MoviePy tidak tersedia.")
        
        if not st.session_state.story_generated:
            st.warning("⚠️ Silakan generate cerita terlebih dahulu")
            return
        
        if not st.session_state.uploaded_files:
            st.warning("⚠️ Silakan upload file media terlebih dahulu")
            return
        
        generate_video_clicked = st.button("🚀 Generate Video dengan Karaoke", 
                                         use_container_width=True, 
                                         type="primary",
                                         key="generate_video_btn")
        
        if generate_video_clicked:
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            try:
                # Save background music if uploaded
                bg_music_path = None
                if st.session_state.background_music:
                    import tempfile
                    bg_music = st.session_state.background_music
                    bg_music_path = os.path.join(tempfile.gettempdir(), f"bg_music_{uuid.uuid4().hex[:8]}_{bg_music.name}")
                    with open(bg_music_path, 'wb') as f:
                        f.write(bg_music.getvalue())
                
                status_text.text("🔊 Step 1: Generating audio narration...")
                audio_path = generate_tts_sync(st.session_state.story_text, settings['language'])
                progress_bar.progress(33)
                
                if not audio_path:
                    st.error("❌ Gagal generate audio")
                    return
                
                st.session_state.audio_path = audio_path
                
                status_text.text("🎬 Step 2: Creating video with REAL karaoke...")
                video_path = video_editor.create_video(
                    media_files=st.session_state.uploaded_files,
                    audio_path=audio_path,
                    duration=settings['duration'],
                    video_format=settings['video_format'],
                    subtitle_text=st.session_state.story_text,
                    font_size=settings['font_size'],
                    text_color=settings['text_color'],
                    text_position=settings['text_position'],
                    background_music=bg_music_path,
                    music_volume=settings['music_volume']
                )
                progress_bar.progress(66)
                
                if not video_path:
                    st.error("❌ Gagal generate video")
                    return
                
                st.session_state.video_path = video_path
                
                status_text.text("📊 Step 3: Optimizing content...")
                st.session_state.optimized_content = content_optimizer.optimize_content(
                    st.session_state.story_text,
                    settings['niche'],
                    settings['language']
                )
                progress_bar.progress(100)
                status_text.text("✅ Video dengan karaoke berhasil di-generate!")
                
                st.balloons()
                
            except Exception as e:
                st.error(f"❌ Error generating video: {str(e)}")
                progress_bar.progress(0)
    
    def render_results(self):
        """Render results section dengan video preview"""
        if not st.session_state.get('video_path'):
            return
        
        st.header("🎉 Hasil Video")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("📺 Preview Video")
            
            if os.path.exists(st.session_state.video_path):
                try:
                    video_file = open(st.session_state.video_path, 'rb')
                    video_bytes = video_file.read()
                    st.video(video_bytes)
                    st.success("🎬 Video dengan karaoke berhasil dibuat!")
                    st.info("🎤 **Fitur Karaoke:** Teks muncul kata demi kata sync dengan audio")
                except Exception as e:
                    st.error(f"❌ Error loading video preview: {e}")
                    st.info(f"Video file: {os.path.basename(st.session_state.video_path)}")
            
            if os.path.exists(st.session_state.video_path):
                try:
                    with open(st.session_state.video_path, "rb") as f:
                        video_bytes = f.read()
                    
                    st.download_button(
                        label="📥 Download Video MP4",
                        data=video_bytes,
                        file_name=f"video_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4",
                        mime="video/mp4",
                        use_container_width=True,
                        key="download_video_btn"
                    )
                except Exception as e:
                    st.error(f"Error loading video: {e}")
        
        with col2:
            st.subheader("📄 Download Assets")
            
            if st.session_state.story_text and st.session_state.optimized_content:
                combined_content = f"""VIDEO CONTENT ASSETS

CERITA NARASI:
{st.session_state.story_text}

OPTIMASI KONTEN:
Judul: {st.session_state.optimized_content['title']}

Deskripsi:
{st.session_state.optimized_content['description']}

Video Hooks:
{chr(10).join([f"{i+1}. {hook}" for i, hook in enumerate(st.session_state.optimized_content['hooks'])])}

Hashtags:
{' '.join([f'#{tag}' for tag in st.session_state.optimized_content['hashtags']])}

Waktu Upload Optimal:
{chr(10).join([f"- {slot['day']}: {slot['time_slot']} ({slot['recommendation']})" for slot in st.session_state.optimized_content['optimal_posting_times'][:3]])}

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
                        mime="audio/mp3",
                        use_container_width=True,
                        key="download_audio_btn"
                    )
                except Exception as e:
                    st.warning(f"Audio tidak tersedia: {e}")
        
        if st.session_state.optimized_content:
            self.render_optimized_content()
    
    def render_optimized_content(self):
        """Render optimized content suggestions"""
        st.header("📈 Optimasi Konten")
        
        content = st.session_state.optimized_content
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🎯 Judul Video")
            st.write(content["title"])
            
            st.subheader("📝 Deskripsi")
            st.text_area("Deskripsi Video", 
                        value=content["description"], 
                        height=150,
                        key="desc_output_final")
        
        with col2:
            st.subheader("🎣 Video Hooks")
            for i, hook in enumerate(content["hooks"], 1):
                st.write(f"{i}. {hook}")
            
            st.subheader("🏷️ Hashtags")
            hashtags = " ".join([f"#{tag}" for tag in content["hashtags"]])
            st.code(hashtags)
    
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
        
        # Status indicators
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.info(f"📁 Media: {len(st.session_state.uploaded_files)}")
        with col2:
            story_status = "📖 Cerita: ✅" if st.session_state.story_generated else "📖 Cerita: ⏳"
            st.info(story_status)
        with col3:
            video_status = "🎬 Video: ✅" if st.session_state.video_path else "🎬 Video: ⏳"
            st.info(video_status)
        with col4:
            api_key = getattr(story_generator, 'api_key', None)
            has_valid_api = api_key and api_key != "your_actual_openrouter_api_key_here"
            ai_status = "🤖 AI: ✅" if has_valid_api else "🤖 AI: ❌"
            st.info(ai_status)
    
    def run(self):
        """Main application runner"""
        
        if not check_ffmpeg():
            st.error("❌ FFmpeg tidak terinstall. Install dengan: `sudo apt install ffmpeg`")
            return
        
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

import uuid

if __name__ == "__main__":
    app = VideoGeneratorApp()
    app.run()

# Tambahkan import di bagian atas
from utils.session_manager import setup_persistent_session, save_current_session, clear_current_session, show_session_info

class VideoGeneratorApp:
    def __init__(self):
        self.setup_session_state()
    
    def setup_session_state(self):
        """Initialize session state dengan persistent management"""
        setup_persistent_session()  # ✅ Ini yang penting!
        
        # Default values jika belum ada di session state
        defaults = {
            'initialized': True,
            'story_generated': False,
            'story_options': [],
            'selected_story_index': 0,
            'story_text': "",
            'audio_path': None,
            'video_path': None,
            'uploaded_files': [],
            'optimized_content': None,
            'selected_color': "#FFFFFF",
            'background_music': None,
            'background_music_path': None
        }
        
        for key, value in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = value

    def render_sidebar(self):
        """Render sidebar dengan session info"""
        with st.sidebar:
            st.title("⚙️ Pengaturan Video")
            
            # ✅ TAMBAHKAN SESSION INFO DI SIDEBAR
            show_session_info()
            
            # ... rest of your existing sidebar code ...

    def render_story_generator(self, settings):
        """Render story generation section dengan auto-save"""
        # ... existing code ...
        
        if generate_clicked:
            # ... existing story generation code ...
            
            # ✅ AUTO-SAVE SETELAH GENERATE CERITA
            setup_persistent_session()
            
        # ... rest of method ...

    def render_video_generator(self, settings):
        """Render video generation dengan auto-save"""
        # ... existing code ...
        
        if generate_video_clicked:
            # ... existing video generation code ...
            
            # ✅ AUTO-SAVE SETELAH BUAT VIDEO
            setup_persistent_session()
            
        # ... rest of method ...
