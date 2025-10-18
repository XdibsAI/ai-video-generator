import asyncio
import os
import time
from gtts import gTTS
import tempfile
import streamlit as st
from utils.compatibility import sanitize_filename
import logging
import threading

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
        
        logger.info("TTS Handler initialized - Using gTTS only")

    async def generate_tts(self, text, language='id', voice=None, rate='+0%'):
        """Generate TTS menggunakan gTTS saja - lebih reliable"""
        return await self.generate_tts_gtts(text, language)

    async def generate_tts_gtts(self, text, language='id'):
        """Generate TTS menggunakan gTTS - primary engine"""
        
        # Validasi input
        if not text or not text.strip():
            raise ValueError("Text cannot be empty")
            
        # Map language code
        gtts_lang = self.lang_map.get(language, 'id')
        
        # Create cache filename
        content_hash = f"{hash(text)}_{gtts_lang}"
        filename = f"tts_{content_hash}.mp3"
        filepath = os.path.join(self.temp_dir, sanitize_filename(filename))
        
        # Check cache first
        if self.cache_enabled and os.path.exists(filepath) and os.path.getsize(filepath) > 2000:
            logger.info(f"Using cached TTS: {filename}")
            return filepath
        
        try:
            # Optimize text length untuk gTTS
            optimized_text = self._optimize_text_for_tts(text)
            
            # Show progress
            with st.spinner(f"🔊 Generating audio ({len(optimized_text.split())} words)..."):
                # Generate dengan gTTS - TANPA timeout parameter
                tts = gTTS(
                    text=optimized_text, 
                    lang=gtts_lang, 
                    slow=False
                    # timeout parameter removed - tidak supported oleh gTTS
                )
                tts.save(filepath)
            
            # Verify the file
            if os.path.exists(filepath) and os.path.getsize(filepath) > 2000:
                st.success("✅ Audio generated successfully")
                logger.info(f"TTS generated: {os.path.getsize(filepath)} bytes")
                return filepath
            else:
                raise Exception("Generated file is too small or empty")
                
        except Exception as e:
            logger.error(f"gTTS generation failed: {e}")
            st.error(f"❌ Audio generation failed: {e}")
            
            # Clean up failed file
            if os.path.exists(filepath):
                try:
                    os.remove(filepath)
                except:
                    pass
                    
            # Try fallback
            return await self._generate_fallback_audio(text, language)

    def _optimize_text_for_tts(self, text):
        """Optimize text untuk TTS generation"""
        # Clean text
        text = text.strip()
        
        # Limit length untuk stability
        if len(text) > 1000:  # Reduced from 1500 untuk lebih aman
            words = text.split()
            if len(words) > 80:  # Reduced dari 120
                text = ' '.join(words[:80]) + "..."
                st.info(f"📝 Text optimized: {len(words)} → 80 words")
            else:
                text = text[:990] + "..."
                
        elif len(text) < 10:
            text = text + "..."  # Add ellipsis for very short texts
            
        return text

    async def _generate_fallback_audio(self, text, language):
        """Generate fallback audio ketika gTTS gagal"""
        try:
            st.warning("🔄 Using fallback audio system...")
            
            # Create fallback filename
            content_hash = f"fallback_{hash(text)}_{language}"
            filename = f"tts_{content_hash}.mp3"
            filepath = os.path.join(self.temp_dir, sanitize_filename(filename))
            
            # Try pydub method first
            try:
                from pydub import AudioSegment
                from pydub.generators import Sine
                
                duration = min(len(text.split()) * 0.3, 6)  # 0.3s per word, max 6s
                audio = Sine(523.25).to_audio_segment(duration=duration * 1000)  # C5 note
                audio = audio.fade_in(200).fade_out(500)
                audio.export(filepath, format="mp3", bitrate="128k")
                
                st.info("✅ Fallback audio created (tone)")
                return filepath
                
            except ImportError:
                # pydub not available, create minimal file
                return self._create_minimal_audio(filepath, text)
                
        except Exception as e:
            logger.error(f"Fallback audio failed: {e}")
            st.error("❌ All audio generation methods failed")
            return None

    def _create_minimal_audio(self, filepath, text):
        """Create minimal audio file sebagai last resort"""
        try:
            # Create a very basic silent MP3
            silent_mp3 = b'\xFF\xFB\x90\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00' * 50
            with open(filepath, 'wb') as f:
                f.write(silent_mp3)
            
            logger.info("Minimal audio placeholder created")
            return filepath
        except Exception as e:
            logger.error(f"Minimal audio creation failed: {e}")
            return None

    def get_status(self):
        """Get current TTS status"""
        return {
            'primary_engine': 'gTTS',
            'cache_enabled': self.cache_enabled,
            'supported_languages': list(self.lang_map.keys())
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
                    
                    if file_age > max_age_hours * 3600:
                        try:
                            os.remove(filepath)
                            cleaned_count += 1
                        except:
                            pass
            
            if cleaned_count > 0:
                logger.info(f"Cleaned up {cleaned_count} old TTS files")
                
        except Exception as e:
            logger.warning(f"Cleanup error: {e}")

# Singleton instance
tts_handler = TTSHandler()

def generate_tts_sync(text, language='id', voice=None, rate='+0%', engine='auto'):
    """
    Synchronous TTS generation
    Note: 'edge' engine is disabled due to reliability issues
    """
    
    # Validate input
    if not text or not text.strip():
        st.error("❌ Please enter some text")
        return None
    
    # Show text info
    word_count = len(text.split())
    st.info(f"📝 Generating audio for {word_count} words...")
    
    try:
        # Always use gTTS - Edge TTS disabled due to 403 errors
        result = asyncio.run(tts_handler.generate_tts_gtts(text, language))
        
        if result and os.path.exists(result):
            file_size = os.path.getsize(result) / 1024  # KB
            st.success(f"✅ Audio ready ({file_size:.1f} KB)")
            return result
        else:
            st.error("❌ Audio generation failed")
            return None
            
    except Exception as e:
        st.error(f"❌ TTS Error: {str(e)}")
        return None

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
            time.sleep(3600)  # Run every hour
    
    thread = threading.Thread(target=cleanup_worker, daemon=True)
    thread.start()

# Start cleanup thread
start_cleanup_thread()
