import os
import tempfile
import streamlit as st
from utils.compatibility import sanitize_filename
import logging

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
            from moviepy.editor import VideoFileClip
            
            # Create temp audio file
            audio_filename = f"extracted_audio_{os.path.basename(video_path)}.wav"
            audio_path = os.path.join(self.temp_dir, sanitize_filename(audio_filename))
            
            # Extract audio
            video_clip = VideoFileClip(video_path)
            audio_clip = video_clip.audio
            audio_clip.write_audiofile(audio_path, verbose=False, logger=None)
            
            # Cleanup
            audio_clip.close()
            video_clip.close()
            
            logger.info(f"Audio extracted: {audio_path}")
            return audio_path
            
        except Exception as e:
            logger.error(f"Error extracting audio: {e}")
            return None
    
    def transcribe_audio(self, audio_path, language='id'):
        """Transcribe audio ke text menggunakan SpeechRecognition"""
        try:
            import speech_recognition as sr
            from pydub import AudioSegment
            
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
            st.info("🎤 Processing speech recognition...")
            text = recognizer.recognize_google(audio_data, language=lang_code)
            
            logger.info(f"Transcription successful: {len(text)} characters")
            return text
            
        except sr.UnknownValueError:
            st.error("❌ Could not understand the audio")
            return None
        except sr.RequestError as e:
            st.error(f"❌ Speech recognition error: {e}")
            return None
        except Exception as e:
            logger.error(f"Transcription error: {e}")
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
            
            st.info("📹 Extracting audio from video...")
            
            # Extract audio dari video
            audio_path = self.extract_audio_from_video(temp_video_path)
            if not audio_path:
                st.error("❌ Failed to extract audio from video")
                return None
            
            # Transcribe audio ke text
            transcribed_text = self.transcribe_audio(audio_path, language)
            
            # Cleanup temporary files
            try:
                os.remove(temp_video_path)
                if os.path.exists(audio_path):
                    os.remove(audio_path)
            except:
                pass
            
            return transcribed_text
            
        except Exception as e:
            logger.error(f"Video transcription failed: {e}")
            st.error(f"❌ Transcription failed: {e}")
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
