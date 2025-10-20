import streamlit as st
import os
import sys
import json
from datetime import datetime
import uuid
import subprocess

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

# ✅ DEFINE CHECK_FFMPEG SEBELUM IMPORT LAINNYA
def check_ffmpeg():
    """Check if FFmpeg is available"""
    try:
        result = subprocess.run(['ffmpeg', '-version'], 
                              capture_output=True, text=True, timeout=5)
        return result.returncode == 0
    except:
        return False

def setup_ffmpeg_warning():
    """Display FFmpeg warning"""
    st.warning("⚠️ FFmpeg not available - video processing limited")

# ✅ IMPORT DENGAN FALLBACK HANDLING
MOVIEPY_AVAILABLE = False
TTS_AVAILABLE = False

try:
    # Try to import main dependencies
    from gtts import gTTS
    TTS_AVAILABLE = True
except ImportError:
    st.error("❌ gTTS not available - audio features disabled")

try:
    from moviepy.editor import VideoFileClip, ImageClip
    MOVIEPY_AVAILABLE = True
except ImportError:
    st.warning("⚠️ MoviePy not available - video features limited")

try:
    from config.settings import *
    from utils.story_generator import story_generator
    from utils.tts_handler import generate_tts_sync, estimate_audio_duration
    from utils.video_editor import video_editor
    from utils.content_optimizer import content_optimizer
    from utils.cleanup import cleanup_manager
    from utils.compatibility import estimate_word_count
    from utils.session_manager import setup_persistent_session, show_session_info
    from utils.text_processor import text_processor
    
    # ✅ AUTO LOAD API KEY
    if OPENROUTER_API_KEY:
        story_generator.api_key = OPENROUTER_API_KEY
        st.sidebar.success("✅ API Key Loaded")
    else:
        st.sidebar.warning("⚠️ API Key not configured")
        
except ImportError as e:
    st.error(f"❌ Import Error: {e}")

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
    .warning-box {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

class VideoGeneratorApp:
    def __init__(self):
        self.setup_session_state()
    
    def setup_session_state(self):
        """Initialize session state dengan persistent management"""
        # Initialize default values
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
        
        # Try to setup persistent session
        try:
            from utils.session_manager import setup_persistent_session
            setup_persistent_session()
        except:
            pass

    def render_sidebar(self):
        """Render sidebar dengan system info"""
        with st.sidebar:
            st.title("⚙️ Pengaturan Video")
            
            # ✅ SYSTEM STATUS
            st.subheader("🔧 System Status")
            
            # FFmpeg Status
            if check_ffmpeg():
                st.success("✅ FFmpeg Ready")
            else:
                st.error("❌ FFmpeg Missing")
                st.info("Run: sudo apt install ffmpeg")
            
            # MoviePy Status
            if MOVIEPY_AVAILABLE:
                st.success("✅ MoviePy Ready")
            else:
                st.error("❌ MoviePy Missing")
                st.info("Run: pip install moviepy")
            
            # TTS Status
            if TTS_AVAILABLE:
                st.success("✅ TTS Ready")
            else:
                st.error("❌ TTS Missing") 
                st.info("Run: pip install gtts")
            
            # API Status
            try:
                if hasattr(story_generator, 'api_key') and story_generator.api_key:
                    st.success("✅ API Key Ready")
                else:
                    st.error("❌ API Key Missing")
            except:
                st.error("❌ API System Error")
            
            # Session Info
            try:
                from utils.session_manager import show_session_info
                show_session_info()
            except:
                pass
            
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
                # Save to temporary file
                import tempfile
                bg_music_path = os.path.join(tempfile.gettempdir(), f"bg_music_{uuid.uuid4().hex[:8]}_{background_music.name}")
                with open(bg_music_path, 'wb') as f:
                    f.write(background_music.getvalue())
                st.session_state.background_music_path = bg_music_path
                st.success(f"✅ {background_music.name} uploaded")
            else:
                st.session_state.background_music_path = None
            
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
                                st.rerun()
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
            try:
                estimated_duration = estimate_audio_duration(st.session_state.story_text, settings['language'])
                st.caption(f"📊 **{word_count} kata** (Estimasi audio: {estimated_duration:.1f}s)")
            except:
                st.caption(f"📊 **{word_count} kata**")

    def render_video_generator(self, settings):
        """Render video generation section"""
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
                    background_music=st.session_state.background_music_path,
                    music_volume=settings['music_volume']
                )
                progress_bar.progress(66)
                
                if not video_path:
                    st.error("❌ Gagal generate video")
                    return
                
                st.session_state.video_path = video_path
                
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
                status_text.text("✅ Video dengan karaoke berhasil di-generate!")
                
                st.balloons()
                
            except Exception as e:
                st.error(f"❌ Error generating video: {str(e)}")
                import traceback
                st.error(f"Detailed error: {traceback.format_exc()}")
                progress_bar.progress(0)

    def render_results(self):
        """Render results section"""
        if not st.session_state.get('video_path'):
            return
        
        st.header("🎉 Hasil Video")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("📺 Preview Video")
            
            if os.path.exists(st.session_state.video_path):
                try:
                    with open(st.session_state.video_path, 'rb') as video_file:
                        video_bytes = video_file.read()
                    st.video(video_bytes)
                    st.success("🎬 Video dengan karaoke berhasil dibuat!")
                    st.info("🎤 **Fitur Karaoke:** Teks muncul kata demi kata sync dengan audio")
                    
                    # Download button for video
                    st.download_button(
                        label="📥 Download Video MP4",
                        data=video_bytes,
                        file_name=f"video_karaoke_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4",
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
