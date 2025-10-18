import streamlit as st
import os
import asyncio
import time
from datetime import datetime
from config.settings import *
from app.utils.story_generator import story_generator
from app.utils.tts_handler import generate_tts_sync
from app.utils.video_editor import video_editor
from app.utils.content_optimizer import content_optimizer
from app.utils.cleanup import cleanup_manager
from app.utils.compatibility import check_ffmpeg, estimate_word_count

# Page configuration
st.set_page_config(
    page_title="AI Video Generator",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

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
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 1rem 0;
    }
    .info-box {
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 1rem 0;
    }
    .upload-box {
        border: 2px dashed #4ECDC4;
        border-radius: 0.5rem;
        padding: 2rem;
        text-align: center;
        margin: 1rem 0;
    }
    .generated-content {
        background-color: #f8f9fa;
        border-left: 4px solid #4ECDC4;
        padding: 1rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

class VideoGeneratorApp:
    def __init__(self):
        self.setup_session_state()
    
    def setup_session_state(self):
        """Initialize session state variables"""
        if 'story_generated' not in st.session_state:
            st.session_state.story_generated = False
        if 'story_text' not in st.session_state:
            st.session_state.story_text = ""
        if 'audio_path' not in st.session_state:
            st.session_state.audio_path = None
        if 'video_path' not in st.session_state:
            st.session_state.video_path = None
        if 'uploaded_files' not in st.session_state:
            st.session_state.uploaded_files = []
        if 'optimized_content' not in st.session_state:
            st.session_state.optimized_content = None
    
    def render_sidebar(self):
        """Render sidebar with settings"""
        with st.sidebar:
            st.title("⚙️ Pengaturan")
            
            # Niche selection
            niche = st.selectbox(
                "🎯 Pilih Niche",
                options=NICHE_OPTIONS,
                index=0
            )
            
            # Language selection
            language = st.selectbox(
                "🌍 Bahasa",
                options=[lang["code"] for lang in LANGUAGE_OPTIONS],
                format_func=lambda x: next(lang["name"] for lang in LANGUAGE_OPTIONS if lang["code"] == x),
                index=0
            )
            
            # Duration selection
            duration_option = st.selectbox(
                "⏱️ Durasi Video",
                options=DURATION_OPTIONS,
                format_func=lambda x: x["label"],
                index=0
            )
            duration = duration_option["seconds"]
            
            # Style selection
            style = st.selectbox(
                "🎨 Gaya Narasi",
                options=STYLE_OPTIONS,
                index=0
            )
            
            # Video format
            video_format = st.radio(
                "📐 Format Video",
                options=["short", "long"],
                format_func=lambda x: "Short (9:16)" if x == "short" else "Long (16:9)",
                index=0
            )
            
            # Text settings
            st.subheader("✍️ Pengaturan Teks")
            text_position = st.radio(
                "📍 Posisi Teks",
                options=[pos["value"] for pos in TEXT_POSITIONS],
                format_func=lambda x: next(pos["label"] for pos in TEXT_POSITIONS if pos["value"] == x),
                index=0
            )
            
            font_size = st.slider(
                "📏 Ukuran Font",
                min_value=40,
                max_value=100,
                value=60,
                step=5
            )
            
            text_color = st.selectbox(
                "🎨 Warna Teks",
                options=COLOR_OPTIONS,
                index=0
            )
            
            font_name = st.selectbox(
                "🔤 Font",
                options=[font["name"] for font in FONT_OPTIONS],
                index=0
            )
            
            # User description
            user_description = st.text_area(
                "📝 Deskripsi Tambahan (Opsional)",
                placeholder="Ceritakan lebih detail tentang konten yang kamu inginkan...",
                height=100
            )
            
            return {
                'niche': niche,
                'language': language,
                'duration': duration,
                'style': style,
                'video_format': video_format,
                'text_position': text_position,
                'font_size': font_size,
                'text_color': text_color,
                'font_name': font_name,
                'user_description': user_description
            }
    
    def render_file_upload(self):
        """Render file upload section"""
        st.subheader("📁 Upload Media")
        
        uploaded_files = st.file_uploader(
            "Pilih gambar atau video",
            type=['jpg', 'jpeg', 'png', 'mp4', 'mov', 'avi'],
            accept_multiple_files=True,
            help="Upload beberapa file untuk video yang lebih menarik"
        )
        
        # Background music upload
        bg_music = st.file_uploader(
            "🎵 Musik Latar (Opsional)",
            type=['mp3', 'wav'],
            accept_multiple_files=False,
            help="Upload file audio untuk background music"
        )
        
        music_volume = st.slider(
            "🔊 Volume Musik",
            min_value=0.0,
            max_value=1.0,
            value=0.3,
            step=0.1,
            help="Atur volume background music"
        )
        
        return uploaded_files, bg_music, music_volume
    
    def render_story_generator(self, settings):
        """Render story generation section"""
        st.subheader("📖 Generate Cerita")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            if st.button("🎭 Generate Cerita Otomatis", use_container_width=True):
                with st.spinner("🤖 Sedang membuat cerita menarik..."):
                    try:
                        story = story_generator.generate_story(
                            settings['niche'],
                            settings['duration'],
                            settings['style'],
                            settings['language'],
                            settings['user_description']
                        )
                        
                        st.session_state.story_text = story
                        st.session_state.story_generated = True
                        st.success("✅ Cerita berhasil di-generate!")
                        
                    except Exception as e:
                        st.error(f"❌ Error generating story: {e}")
        
        with col2:
            # Word count information
            word_range = estimate_word_count(settings['duration'])
            st.info(f"📊 Target: {word_range[0]}-{word_range[1]} kata")
        
        # Story editor
        if st.session_state.story_generated:
            st.subheader("✏️ Edit Cerita")
            edited_story = st.text_area(
                "Edit cerita sesuai keinginanmu:",
                value=st.session_state.story_text,
                height=200,
                key="story_editor"
            )
            
            if edited_story != st.session_state.story_text:
                st.session_state.story_text = edited_story
                st.rerun()
            
            # Word count real-time
            word_count = len(st.session_state.story_text.split())
            st.caption(f"📝 Jumlah kata: {word_count} (Estimasi durasi audio: {word_count/2.5:.1f} detik)")
    
    def render_video_generator(self, settings, bg_music_path=None, music_volume=0.3):
        """Render video generation section"""
        if not st.session_state.story_generated:
            st.warning("⚠️ Silakan generate cerita terlebih dahulu")
            return
        
        st.subheader("🎬 Generate Video")
        
        if st.button("🚀 Generate Video", use_container_width=True, type="primary"):
            if not st.session_state.uploaded_files:
                st.error("❌ Silakan upload minimal satu file media")
                return
            
            # Progress tracking
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            try:
                # Step 1: Generate TTS
                status_text.text("🔊 Generating audio narration...")
                audio_path = generate_tts_sync(
                    st.session_state.story_text,
                    settings['language']
                )
                progress_bar.progress(25)
                
                if not audio_path:
                    st.error("❌ Gagal generate audio")
                    return
                
                st.session_state.audio_path = audio_path
                
                # Step 2: Create video
                status_text.text("🎬 Creating video with effects...")
                video_path = video_editor.create_video(
                    media_files=st.session_state.uploaded_files,
                    audio_path=audio_path,
                    duration=settings['duration'],
                    video_format=settings['video_format'],
                    subtitle_text=st.session_state.story_text,
                    font_size=settings['font_size'],
                    text_color=settings['text_color'],
                    text_position=settings['text_position'],
                    font_name=settings['font_name'],
                    background_music=bg_music_path,
                    music_volume=music_volume
                )
                progress_bar.progress(75)
                
                if not video_path:
                    st.error("❌ Gagal generate video")
                    return
                
                st.session_state.video_path = video_path
                
                # Step 3: Optimize content
                status_text.text("📊 Optimizing content...")
                st.session_state.optimized_content = content_optimizer.optimize_content(
                    st.session_state.story_text,
                    settings['niche'],
                    settings['language']
                )
                progress_bar.progress(100)
                status_text.text("✅ Video berhasil di-generate!")
                
                st.balloons()
                
            except Exception as e:
                st.error(f"❌ Error generating video: {e}")
                progress_bar.progress(0)
                status_text.text("❌ Gagal generate video")
    
    def render_results(self):
        """Render results section"""
        if not st.session_state.video_path:
            return
        
        st.subheader("🎉 Hasil Video")
        
        # Video preview and download
        col1, col2 = st.columns(2)
        
        with col1:
            st.video(st.session_state.video_path)
            
            # Download video
            with open(st.session_state.video_path, "rb") as f:
                video_bytes = f.read()
            
            st.download_button(
                label="📥 Download Video",
                data=video_bytes,
                file_name=f"video_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4",
                mime="video/mp4",
                use_container_width=True
            )
        
        with col2:
            # Download story
            st.download_button(
                label="📄 Download Cerita",
                data=st.session_state.story_text,
                file_name=f"cerita_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain",
                use_container_width=True
            )
            
            # Download audio if exists
            if st.session_state.audio_path and os.path.exists(st.session_state.audio_path):
                with open(st.session_state.audio_path, "rb") as f:
                    audio_bytes = f.read()
                
                st.download_button(
                    label="🔊 Download Audio",
                    data=audio_bytes,
                    file_name=f"audio_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp3",
                    mime="audio/mp3",
                    use_container_width=True
                )
        
        # Optimized content
        if st.session_state.optimized_content:
            self.render_optimized_content()
    
    def render_optimized_content(self):
        """Render optimized content suggestions"""
        st.subheader("📈 Optimasi Konten")
        
        content = st.session_state.optimized_content
        
        with st.expander("🎯 Judul Video", expanded=True):
            st.write(content["title"])
        
        with st.expander("📝 Deskripsi Video"):
            st.text_area("Deskripsi", value=content["description"], height=150)
        
        with st.expander("🎣 Video Hooks"):
            for i, hook in enumerate(content["hooks"], 1):
                st.write(f"{i}. {hook}")
        
        with st.expander("🏷️ Hashtags"):
            hashtags = " ".join([f"#{tag}" for tag in content["hashtags"]])
            st.code(hashtags)
        
        with st.expander("🕐 Waktu Upload Optimal"):
            for time_slot in content["optimal_posting_times"]:
                st.write(f"**{time_slot['day']}** ({time_slot['date']}): {time_slot['time_slot']} - Rekomendasi: {time_slot['recommendation']}")
    
    def render_header(self):
        """Render application header"""
        st.markdown('<h1 class="main-header">🎬 AI Video Generator</h1>', unsafe_allow_html=True)
        st.markdown("""
        <div style='text-align: center; margin-bottom: 2rem;'>
            <p style='font-size: 1.2rem; color: #666;'>
                Buat video menarik dengan AI dalam hitungan menit! Upload media, generate cerita, 
                dan dapatkan video siap upload ke platform favoritmu.
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    def run(self):
        """Main application runner"""
        
        # Check dependencies
        if not check_ffmpeg():
            st.error("""
            ❌ FFmpeg tidak terinstall. Silakan install FFmpeg terlebih dahulu:
            
            **Ubuntu/Debian:**
            ```bash
            sudo apt update && sudo apt install ffmpeg
            ```
            
            **Windows:**
            Download dari https://ffmpeg.org/download.html
            
            **Mac:**
            ```bash
            brew install ffmpeg
            ```
            """)
            return
        
        # Render header
        self.render_header()
        
        # Main layout
        col1, col2 = st.columns([1, 2])
        
        with col1:
            settings = self.render_sidebar()
        
        with col2:
            # File upload
            uploaded_files, bg_music, music_volume = self.render_file_upload()
            if uploaded_files:
                st.session_state.uploaded_files = uploaded_files
                st.success(f"✅ {len(uploaded_files)} file berhasil diupload")
            
            # Save background music if uploaded
            bg_music_path = None
            if bg_music:
                bg_music_path = os.path.join(TEMP_DIR, bg_music.name)
                with open(bg_music_path, "wb") as f:
                    f.write(bg_music.getvalue())
                st.success("✅ Musik latar berhasil diupload")
            
            # Story generator
            self.render_story_generator(settings)
            
            # Video generator
            self.render_video_generator(settings, bg_music_path, music_volume)
            
            # Results
            self.render_results()
        
        # Storage info in sidebar
        with st.sidebar:
            st.divider()
            storage_info = cleanup_manager.get_storage_info()
            st.caption(f"💾 Storage: {storage_info['total_files']} files ({storage_info['total_size_mb']} MB)")
            st.caption(f"🕐 Auto-cleanup: {storage_info['max_age_minutes']} menit")

# Run the application
if __name__ == "__main__":
    app = VideoGeneratorApp()
    app.run()
