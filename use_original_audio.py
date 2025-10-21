#!/bin/bash

# Update video editor untuk menggunakan audio original jika auto-subtitle
python3 << 'PYTHONCODE'
import re

with open('apps/main.py', 'r') as f:
    content = f.read()

# Cari bagian generate_video_clicked dan perbaiki audio handling
old_audio_section = '''                # Determine audio source
                if auto_subtitle and has_video_upload:
                    # Use audio from uploaded video
                    status_text.text("🔊 Using audio from uploaded video...")
                    video_file = next(f for f in st.session_state.uploaded_files if f.type.startswith('video'))
                    
                    # Extract audio from video
                    import tempfile
                    temp_video_path = os.path.join(tempfile.gettempdir(), f"temp_video_{uuid.uuid4().hex[:8]}_{video_file.name}")
                    with open(temp_video_path, 'wb') as f:
                        f.write(video_file.getvalue())
                    
                    from moviepy.editor import VideoFileClip
                    video_clip = VideoFileClip(temp_video_path)
                    audio_path = os.path.join(tempfile.gettempdir(), f"extracted_audio_{uuid.uuid4().hex[:8]}.mp3")
                    video_clip.audio.write_audiofile(audio_path, verbose=False, logger=None)
                    video_clip.close()
                    
                    # Extract text from video audio
                    status_text.text("🎤 Extracting text from video audio...")
                    transcribed_text = speech_to_text.transcribe_video(video_file, settings['language'])
                    if transcribed_text:
                        st.session_state.story_text = transcribed_text
                        st.success(f"✅ Extracted {len(transcribed_text)} characters from video")
                    
                else:
                    # Generate TTS seperti biasa
                    status_text.text("🔊 Generating audio narration...")
                    audio_path = generate_tts_sync(st.session_state.story_text, settings['language'])'''

new_audio_section = '''                # Determine audio source
                use_original_audio = st.session_state.get('auto_subtitle_used', False) or auto_subtitle
                
                if use_original_audio and st.session_state.uploaded_files:
                    # Use audio from uploaded video (Auto-Subtitle mode)
                    status_text.text("🔊 Menggunakan audio original dari video...")
                    video_file = next((f for f in st.session_state.uploaded_files if f.type.startswith('video')), None)
                    
                    if video_file:
                        # Extract audio from video
                        import tempfile
                        temp_video_path = os.path.join(tempfile.gettempdir(), f"temp_video_{uuid.uuid4().hex[:8]}_{video_file.name}")
                        with open(temp_video_path, 'wb') as f:
                            f.write(video_file.getvalue())
                        
                        from moviepy.editor import VideoFileClip
                        video_clip = VideoFileClip(temp_video_path)
                        audio_path = os.path.join(tempfile.gettempdir(), f"extracted_audio_{uuid.uuid4().hex[:8]}.mp3")
                        video_clip.audio.write_audiofile(audio_path, verbose=False, logger=None)
                        video_clip.close()
                        
                        st.success("✅ Audio original berhasil diekstrak")
                    else:
                        st.error("❌ Video file tidak ditemukan")
                        return
                else:
                    # Generate TTS untuk cerita biasa
                    status_text.text("🔊 Generating audio narration...")
                    audio_path = generate_tts_sync(st.session_state.story_text, settings['language'])'''

content = content.replace(old_audio_section, new_audio_section)

with open('apps/main.py', 'w') as f:
    f.write(content)

print("✅ Audio handling diupdate untuk gunakan audio original")
PYTHONCODE
