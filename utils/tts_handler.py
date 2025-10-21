import asyncio
import os
import time
from gtts import gTTS
import tempfile
import streamlit as st
from utils.compatibility import sanitize_filename
from utils.ffmpeg_checker import check_ffmpeg
import logging
import threading
from pydub import AudioSegment
from pydub.generators import Sine

# Check if gTTS is available
try:
    from gtts import gTTS
    TTS_AVAILABLE = True
except ImportError:
    TTS_AVAILABLE = False

logger = logging.getLogger(__name__)

class TTSHandler:
    def __init__(self):
        self.temp_dir = tempfile.gettempdir()
        self.cache_enabled = True

        # Language mapping untuk gTTS
        self.lang_map = {
            'id': 'id', 'en': 'en', 'es': 'es', 'fr': 'fr',
            'de': 'de', 'ja': 'ja', 'ko': 'ko', 'zh': 'zh',
            'ar': 'ar', 'hi': 'hi', 'pt': 'pt', 'ru': 'ru',
            'it': 'it', 'tr': 'tr', 'pl': 'pl', 'nl': 'nl'
        }

        # Average reading speed (words per minute)
        self.reading_speed = {
            'id': 160,  # Indonesian
            'en': 150,  # English
            'es': 160,  # Spanish
            'fr': 155,  # French
            'de': 150,  # German
            'ja': 140,  # Japanese
            'ko': 145,  # Korean
            'zh': 140   # Chinese
        }

        logger.info("TTS Handler initialized - Using gTTS only")

    def estimate_audio_duration(self, text, language='id'):
        """Estimate audio duration based on text length and language"""
        try:
            if not text or not isinstance(text, str):
                logger.warning("Empty or invalid text for duration estimation")
                return 1.0

            words = len(text.split())
            wpm = self.reading_speed.get(language, 150)
            duration_minutes = words / wpm
            duration = max(1.0, duration_minutes * 60)  # Minimum 1 second
            logger.info(f"Estimated duration for {words} words in {language}: {duration:.1f}s")
            return duration
        except Exception as e:
            logger.error(f"Error estimating duration: {str(e)}")
            return 1.0

    async def generate_tts(self, text, language='id', voice=None, rate='+0%'):
        """Generate TTS menggunakan gTTS saja - lebih reliable"""
        return await self.generate_tts_gtts(text, language)

    async def generate_tts_gtts(self, text, language='id'):
        """Generate TTS menggunakan gTTS - primary engine"""
        if not TTS_AVAILABLE:
            st.error("❌ gTTS tidak tersedia. Install: pip install gtts")
            logger.error("gTTS library not available")
            return None

        # Validasi input
        if not text or not text.strip():
            st.error("❌ Teks untuk TTS tidak boleh kosong")
            logger.error("Empty text provided for TTS")
            return None

        # Check FFmpeg availability
        if not check_ffmpeg():
            st.error("❌ FFmpeg tidak tersedia. Diperlukan untuk pemrosesan audio.")
            logger.error("FFmpeg not available for TTS processing")
            return None

        # Map language code
        gtts_lang = self.lang_map.get(language, 'id')

        # Create cache filename
        content_hash = f"{hash(text)}_{gtts_lang}"
        filename = f"tts_{content_hash}.mp3"
        filepath = os.path.join(self.temp_dir, sanitize_filename(filename))

        # Check cache first
        if self.cache_enabled and os.path.exists(filepath) and os.path.getsize(filepath) > 2000:
            logger.info(f"Using cached TTS: {filename}")
            st.info(f"✅ Menggunakan audio dari cache: {filename}")
            return filepath

        try:
            # Optimize text length untuk gTTS
            optimized_text = self._optimize_text_for_tts(text)

            # Estimate duration sebelum generate
            estimated_duration = self.estimate_audio_duration(optimized_text, language)
            st.info(f"⏱️ Estimasi durasi audio: {estimated_duration:.1f}s")

            # Show progress
            with st.spinner(f"🔊 Menghasilkan audio ({len(optimized_text.split())} kata)..."):
                # Generate dengan gTTS
                tts = gTTS(
                    text=optimized_text,
                    lang=gtts_lang,
                    slow=False
                )
                tts.save(filepath)

            # Verify the file
            if os.path.exists(filepath) and os.path.getsize(filepath) > 2000:
                # Get actual duration using FFmpeg
                try:
                    import subprocess
                    result = subprocess.run([
                        'ffprobe', '-v', 'error', '-show_entries',
                        'format=duration', '-of',
                        'default=noprint_wrappers=1:nokey=1', filepath
                    ], capture_output=True, text=True, timeout=10)

                    actual_duration = float(result.stdout.strip()) if result.stdout else estimated_duration
                    st.success(f"✅ Audio dihasilkan ({actual_duration:.1f}s)")
                    logger.info(f"TTS generated: {filepath}, size: {os.path.getsize(filepath)} bytes, duration: {actual_duration:.1f}s")
                    return filepath
                except Exception as e:
                    st.success("✅ Audio dihasilkan dengan sukses")
                    logger.info(f"TTS generated: {filepath}, size: {os.path.getsize(filepath)} bytes")
                    return filepath
            else:
                st.error("❌ File audio yang dihasilkan kosong atau terlalu kecil")
                logger.error(f"Generated file is invalid: {filepath}, size: {os.path.getsize(filepath) if os.path.exists(filepath) else 0} bytes")
                raise Exception("Generated audio file is too small or empty")

        except Exception as e:
            logger.error(f"gTTS generation failed: {str(e)}")
            st.error(f"❌ Gagal menghasilkan audio: {str(e)}")

            # Clean up failed file
            if os.path.exists(filepath):
                try:
                    os.remove(filepath)
                    logger.info(f"Cleaned up failed file: {filepath}")
                except:
                    pass

            # Try fallback
            return await self._generate_fallback_audio(text, language)

    def _optimize_text_for_tts(self, text):
        """Optimize text untuk TTS generation"""
        try:
            # Clean text
            text = text.strip()

            # Limit length untuk stability
            if len(text) > 1000:
                words = text.split()
                if len(words) > 80:
                    text = ' '.join(words[:80]) + "..."
                    st.info(f"📝 Teks dioptimalkan: {len(words)} → 80 kata")
                else:
                    text = text[:990] + "..."
            elif len(text) < 10:
                text = text + "..."  # Add ellipsis for very short texts

            return text
        except Exception as e:
            logger.error(f"Text optimization failed: {str(e)}")
            return text

    async def _generate_fallback_audio(self, text, language):
        """Generate fallback audio ketika gTTS gagal"""
        try:
            st.warning("🔄 Menggunakan sistem audio cadangan...")

            # Create fallback filename
            content_hash = f"fallback_{hash(text)}_{language}"
            filename = f"tts_{content_hash}.mp3"
            filepath = os.path.join(self.temp_dir, sanitize_filename(filename))

            # Try pydub method first
            try:
                duration = min(len(text.split()) * 0.3, 6)
                audio = Sine(523.25).to_audio_segment(duration=duration * 1000)
                audio = audio.fade_in(200).fade_out(500)
                audio.export(filepath, format="mp3", bitrate="128k")

                st.info("✅ Audio cadangan (nada sederhana) dibuat")
                logger.info(f"Fallback audio created: {filepath}")
                return filepath

            except ImportError:
                # pydub not available, create minimal file
                return self._create_minimal_audio(filepath, text)

        except Exception as e:
            logger.error(f"Fallback audio failed: {str(e)}")
            st.error("❌ Semua metode pembuatan audio gagal")
            return None

    def _create_minimal_audio(self, filepath, text):
        """Create minimal audio file sebagai last resort"""
        try:
            # Create a very basic silent MP3
            silent_mp3 = b'\xFF\xFB\x90\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00' * 50
            with open(filepath, 'wb') as f:
                f.write(silent_mp3)

            logger.info(f"Minimal audio placeholder created: {filepath}")
            st.info("✅ Audio minimal (diam) dibuat sebagai cadangan")
            return filepath
        except Exception as e:
            logger.error(f"Minimal audio creation failed: {str(e)}")
            st.error("❌ Gagal membuat audio cadangan")
            return None

    def get_status(self):
        """Get current TTS status"""
        return {
            'primary_engine': 'gTTS',
            'cache_enabled': self.cache_enabled,
            'supported_languages': list(self.lang_map.keys()),
            'tts_available': TTS_AVAILABLE
        }

    def cleanup_old_files(self, max_age_hours=24):
        """Clean up old TTS files"""
        try:
            current_time = time.time()
            cleaned_count = 0

            for filename in os.listdir(self.temp_dir):
                if filename.startswith('tts_'):
                    filepath = os.path.join(self.temp_dir, filename)
                    file_age = current_time - os.path.getctime(filepath)
                    file_size = os.path.getsize(filepath) if os.path.exists(filepath) else 0

                    if file_age > max_age_hours * 3600 or file_size < 2000:
                        try:
                            os.remove(filepath)
                            cleaned_count += 1
                            logger.info(f"Removed old or invalid file: {filepath}")
                        except:
                            pass

            if cleaned_count > 0:
                logger.info(f"Cleaned up {cleaned_count} old or invalid TTS files")

        except Exception as e:
            logger.warning(f"Cleanup error: {str(e)}")

# Singleton instance
tts_handler = TTSHandler()

def generate_tts_sync(text, language='id', voice=None, rate='+0%', engine='auto'):
    """
    Synchronous TTS generation
    Note: 'edge' engine is disabled due to reliability issues
    """
    # Validate input
    if not text or not text.strip():
        st.error("❌ Silakan masukkan teks untuk TTS")
        logger.error("Empty text provided for TTS generation")
        return None

    # Show text info
    word_count = len(text.split())
    estimated_duration = tts_handler.estimate_audio_duration(text, language)
    st.info(f"📝 Menghasilkan audio untuk {word_count} kata (~{estimated_duration:.1f}s)")

    try:
        # Always use gTTS
        result = asyncio.run(tts_handler.generate_tts_gtts(text, language))

        if result and os.path.exists(result) and os.path.getsize(result) > 2000:
            file_size = os.path.getsize(result) / 1024  # KB
            st.success(f"✅ Audio siap ({file_size:.1f} KB)")
            logger.info(f"TTS generation successful: {result}, size: {file_size:.1f} KB")
            return result
        else:
            st.error("❌ Gagal menghasilkan audio yang valid")
            logger.error("TTS generation failed: Invalid or empty audio file")
            return None

    except Exception as e:
        st.error(f"❌ Error TTS: {str(e)}")
        logger.error(f"TTS generation failed: {str(e)}")
        return None

def estimate_audio_duration(text, language='id'):
    """Estimate audio duration for the given text"""
    return tts_handler.estimate_audio_duration(text, language)

def get_tts_info():
    """Get TTS system information"""
    return tts_handler.get_status()

def get_supported_languages():
    """Get supported languages"""
    return {
        'Indonesian': 'id',
        'English': 'en',
        'Spanish': 'es',
        'French': 'fr',
        'German': 'de',
        'Japanese': 'ja',
        'Korean': 'ko',
        'Chinese': 'zh'
    }

# Background cleanup
def start_cleanup_thread():
    def cleanup_worker():
        while True:
            try:
                tts_handler.cleanup_old_files()
            except Exception as e:
                logger.error(f"Cleanup thread error: {e}")
            time.sleep(3600)

    thread = threading.Thread(target=cleanup_worker, daemon=True)
    thread.start()

# Start cleanup thread
start_cleanup_thread()
