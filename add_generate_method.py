#!/bin/bash

# Tambahkan method _generate_video_process
python3 << 'PYTHONCODE'
import re

with open('apps/main.py', 'r') as f:
    content = f.read()

# Tambahkan method _generate_video_process
generate_method = '''
    
    def _generate_video_process(self, settings, selected_effect):
        """Handle video generation process"""
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            # Determine audio source
            use_original_audio = self.safe_session_get('auto_subtitle_used', False)
            
            if use_original_audio and self.safe_session_get('uploaded_files'):
                # Use audio from uploaded video (Auto-Subtitle mode)
                status_text.text("🔊 Menggunakan audio original dari video...")
                video_file = next((f for f in self.safe_session_get('uploaded_files') if hasattr(f, 'type') and f.type.startswith('video')), None)
                
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
                audio_path = generate_tts_sync(self.safe_session_get('story_text'), settings['language'])
            
            progress_bar.progress(33)
            
            if not audio_path:
                st.error("❌ Gagal mendapatkan audio")
                return
            
            self.safe_session_set('audio_path', audio_path)
            
            status_text.text("🎬 Step 2: Creating video dengan REAL karaoke...")
            
            # Video creation
            video_path = video_editor.create_video(
                media_files=self.safe_session_get('uploaded_files'),
                audio_path=audio_path,
                duration=settings['duration'],
                video_format=settings['video_format'],
                subtitle_text=self.safe_session_get('story_text'),
                font_size=settings['font_size'],
                text_color=settings['text_color'],
                text_position=settings['text_position'],
                background_music=self.safe_session_get('background_music_path'),
                music_volume=settings['music_volume'],
                mode=self.safe_session_get('video_mode'),
                auto_subtitle=self.safe_session_get('auto_subtitle_used'),
                subtitle_language=settings['language'],
                text_effect=selected_effect,
                use_original_video=(self.safe_session_get('video_mode') == 'add_text_to_video')
            )
            progress_bar.progress(66)
            
            if not video_path:
                st.error("❌ Gagal generate video")
                return
            
            self.safe_session_set('video_path', video_path)
            
            status_text.text("📊 Step 3: Optimizing content...")
            try:
                optimized_content = content_optimizer.optimize_content(
                    self.safe_session_get('story_text'),
                    settings['niche'],
                    settings['language']
                )
                self.safe_session_set('optimized_content', optimized_content)
            except:
                self.safe_session_set('optimized_content', {
                    'title': 'Generated Video',
                    'description': self.safe_session_get('story_text')[:100] + '...',
                    'hooks': ['Watch this amazing video!'],
                    'hashtags': ['video', 'content'],
                    'optimal_posting_times': []
                })
            
            progress_bar.progress(100)
            
            mode_name = "Video dengan Media" if self.safe_session_get('video_mode') == 'video' else "Teks Karaoke Only"
            if self.safe_session_get('video_mode') == 'add_text_to_video':
                mode_name = "Tambah Teks ke Video Existing"
            
            subtitle_source = "auto dari video" if self.safe_session_get('auto_subtitle_used') else "teks AI"
            status_text.text(f"✅ {mode_name} dengan {subtitle_source} berhasil di-generate!")
            
            st.balloons()
            st.success("🎉 **Video berhasil dibuat!** Lihat hasil di tab '📊 Hasil'")
            
        except Exception as e:
            st.error(f"❌ Error generating video: {str(e)}")
            import traceback
            st.error(f"Detailed error: {traceback.format_exc()}")
            progress_bar.progress(0)'''

# Tambahkan method setelah _render_video_generation_section
if 'def _render_video_generation_section' in content:
    method_end = content.find('def ', content.find('def _render_video_generation_section') + 1)
    if method_end == -1:
        method_end = len(content)
    
    content = content[:method_end] + generate_method + '\\n\\n' + content[method_end:]

with open('apps/main.py', 'w') as f:
    f.write(content)

print("✅ Method generate video ditambahkan")
PYTHONCODE
