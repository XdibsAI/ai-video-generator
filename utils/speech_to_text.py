import os
import tempfile
import streamlit as st
from utils.compatibility import sanitize_filename
from utils.ffmpeg_checker import check_ffmpeg
import logging
import speech_recognition as sr
from pydub import AudioSegment

logger = logging.getLogger(__name__)

class SpeechToText:
    def __init__(self):
        self.temp_dir = tempfile.gettempdir()
        self.supported_languages = {
            'id': 'id-ID',
            'en': 'en-US',
            'es': 'es-ES',
            'fr': 'fr-FR',
            'de': 'de-DE',
            'ja': 'ja-JP',
            'ko': 'ko-KR',
            'zh': 'zh-CN'
        }

    def extract_audio_from_video(self, video_path):
        """Extract audio dari video file"""
        try:
            if not check_ffmpeg():
                st.error("❌ FFmpeg tidak tersedia. Silakan instal FFmpeg.")
                logger.error("FFmpeg not available for audio extraction")
                return None

            from moviepy.editor import VideoFileClip

            # Create temp audio file
            audio_filename = f"extracted_audio_{os.path.basename(video_path)}.wav"
            audio_path = os.path.join(self.temp_dir, sanitize_filename(audio_filename))

            # Extract audio
            video_clip = VideoFileClip(video_path)
            if not video_clip.audio:
                st.error("❌ Video tidak memiliki audio")
                logger.error(f"No audio stream found in {video_path}")
                video_clip.close()
                return None

            audio_clip = video_clip.audio
            audio_clip.write_audiofile(audio_path, codec='pcm_s16le', verbose=False, logger=None)

            # Cleanup
            audio_clip.close()
            video_clip.close()

            if not os.path.exists(audio_path) or os.path.getsize(audio_path) == 0:
                st.error("❌ Gagal mengekstrak audio: File kosong atau tidak valid")
                logger.error(f"Audio extraction failed: {audio_path} is empty or invalid")
                return None

            logger.info(f"Audio extracted successfully: {audio_path}")
            return audio_path

        except Exception as e:
            logger.error(f"Error extracting audio: {str(e)}")
            st.error(f"❌ Gagal mengekstrak audio: {str(e)}")
            return None

    def transcribe_audio(self, audio_path, language='id'):
        """Transcribe audio ke text menggunakan SpeechRecognition"""
        try:
            if not os.path.exists(audio_path):
                st.error("❌ File audio tidak ditemukan")
                logger.error(f"Audio file not found: {audio_path}")
                return None

            # Convert to WAV if needed
            if not audio_path.endswith('.wav'):
                audio = AudioSegment.from_file(audio_path)
                wav_path = audio_path.replace(os.path.splitext(audio_path)[1], '.wav')
                audio.export(wav_path, format='wav')
                audio_path = wav_path

            # Initialize recognizer
            recognizer = sr.Recognizer()

            # Load audio file
            with sr.AudioFile(audio_path) as source:
                # Adjust for ambient noise
                recognizer.adjust_for_ambient_noise(source)
                audio_data = recognizer.record(source)

            # Get language code
            lang_code = self.supported_languages.get(language, 'id-ID')

            # Transcribe
            st.info("🎤 Memproses pengenalan suara...")
            text = recognizer.recognize_google(audio_data, language=lang_code)

            logger.info(f"Transcription successful: {len(text)} characters")
            st.success(f"✅ Berhasil mentranskrip {len(text)} karakter")
            return text

        except sr.UnknownValueError:
            st.error("❌ Tidak dapat memahami audio")
            logger.error("Speech recognition failed: Could not understand audio")
            return None
        except sr.RequestError as e:
            st.error(f"❌ Error pengenalan suara: {str(e)}")
            logger.error(f"Speech recognition error: {str(e)}")
            return None
        except Exception as e:
            st.error(f"❌ Error transkripsi: {str(e)}")
            logger.error(f"Transcription error: {str(e)}")
            return None

    def transcribe_video(self, video_file, language='id'):
        """Main function untuk transcribe video ke text"""
        try:
            # Save uploaded video temporarily
            temp_video_path = os.path.join(
                self.temp_dir,
                f"temp_video_{os.urandom(8).hex()}_{video_file.name}"
            )

            with open(temp_video_path, 'wb') as f:
                f.write(video_file.getvalue())

            st.info("📹 Mengekstrak audio dari video...")

            # Extract audio dari video
            audio_path = self.extract_audio_from_video(temp_video_path)
            if not audio_path:
                st.error("❌ Gagal mengekstrak audio dari video")
                return None

            # Transcribe audio ke text
            transcribed_text = self.transcribe_audio(audio_path, language)

            # Cleanup temporary files
            try:
                if os.path.exists(temp_video_path):
                    os.remove(temp_video_path)
                if os.path.exists(audio_path):
                    os.remove(audio_path)
            except Exception as e:
                logger.warning(f"Failed to clean up temporary files: {str(e)}")

            return transcribed_text

        except Exception as e:
            logger.error(f"Video transcription failed: {str(e)}")
            st.error(f"❌ Transkripsi video gagal: {str(e)}")
            return None

    def get_supported_languages(self):
        """Get list of supported languages"""
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

# Singleton instance
speech_to_text = SpeechToText()

def transcribe_video_sync(video_file, language='id'):
    """Synchronous wrapper untuk video transcription"""
    return speech_to_text.transcribe_video(video_file, language)

def get_supported_stt_languages():
    """Get supported languages untuk UI"""
    return speech_to_text.get_supported_languages()
