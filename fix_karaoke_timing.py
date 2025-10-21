#!/bin/bash

# Perbaiki karaoke timing untuk kata demi kata
python3 << 'PYTHONCODE'
import re

with open('utils/video_editor.py', 'r') as f:
    content = f.read()

# Ganti method _add_punctuation_aware_karaoke dengan yang lebih baik
old_karaoke_method = '''    def _add_punctuation_aware_karaoke(self, video_clip, text, font_size, text_color, text_position, audio_duration, text_effect='none'):
        """Add karaoke dengan text effects"""
        try:
            st.info("🎤 Creating punctuation-aware karaoke with effects...")
            
            # Get effect config
            effect_config = get_text_effect_config(text_effect)
            
            # Calculate position
            if text_position == 'middle':
                position = ('center', video_clip.h * 0.3)
            else:
                position = ('center', video_clip.h * 0.8)
            
            text_clips = []
            
            # Get punctuation-aware timings
            timings = text_processor.create_punctuation_aware_karaoke(text, audio_duration)
            
            st.info(f"📊 Karaoke segments: {len(timings)} | Effect: {effect_config['name']}")
            
            for i, timing in enumerate(timings):
                chunk_text = timing['text']
                start_time = timing['start_time']
                end_time = timing['end_time']
                has_punctuation = timing['has_punctuation']
                punctuation = timing['punctuation']
                
                if start_time >= audio_duration:
                    break
                    
                end_time = min(end_time, audio_duration)
                
                try:
                    # ✅ APPLY EFFECT SETTINGS
                    stroke_color = effect_config.get('stroke_color', 'black')
                    stroke_width = effect_config.get('stroke_width', 2)
                    font_color = effect_config.get('font_color', text_color)
                    
                    # Special styling untuk punctuation dengan effects
                    if has_punctuation and punctuation in ['.', '!', '?']:
                        if text_effect == 'glow':
                            font_color = effect_config.get('glow_color', '#FFD700')
                        elif text_effect == 'neon':
                            font_color = effect_config.get('neon_color', '#00FFFF')
                    
                    txt_clip = TextClip(
                        chunk_text,
                        fontsize=font_size,
                        color=font_color,
                        font='Arial-Bold',
                        stroke_color=stroke_color,
                        stroke_width=stroke_width,
                        size=(video_clip.w * 0.9, None),
                        method='caption'
                    ).set_position(position).set_start(start_time).set_duration(end_time - start_time)
                    
                    text_clips.append(txt_clip)
                    
                except Exception as e:
                    st.warning(f"⚠️ Error creating text for '{chunk_text}': {str(e)}")
                    continue
            
            if not text_clips:
                st.warning("⚠️ No text clips created, using normal subtitle")
                return self._add_normal_subtitle(video_clip, text, font_size, text_color, text_position, text_effect)
            
            st.info(f"🔄 Compositing {len(text_clips)} segments with {effect_config['name']}...")
            result = CompositeVideoClip([video_clip] + text_clips)
            
            return result
            
        except Exception as e:
            st.error(f"❌ Punctuation-aware karaoke error: {str(e)}")
            raise e'''

new_karaoke_method = '''    def _add_punctuation_aware_karaoke(self, video_clip, text, font_size, text_color, text_position, audio_duration, text_effect='none'):
        """Add karaoke dengan text effects - KATA DEMI KATA"""
        try:
            st.info("🎤 Creating word-by-word karaoke with effects...")
            
            # Get effect config
            effect_config = get_text_effect_config(text_effect)
            
            # Calculate position
            if text_position == 'middle':
                position = ('center', video_clip.h * 0.3)
            else:
                position = ('center', video_clip.h * 0.8)
            
            text_clips = []
            
            # Split text into individual words for true karaoke
            words = text.split()
            total_words = len(words)
            
            if total_words == 0:
                st.warning("⚠️ No words found for karaoke")
                return self._add_normal_subtitle(video_clip, text, font_size, text_color, text_position, text_effect)
            
            # Calculate timing per word
            word_duration = audio_duration / total_words
            
            st.info(f"📊 Karaoke words: {total_words} | Duration per word: {word_duration:.2f}s | Effect: {effect_config['name']}")
            
            # Build text progressively (word by word)
            for i in range(total_words):
                start_time = i * word_duration
                end_time = (i + 1) * word_duration
                
                if start_time >= audio_duration:
                    break
                    
                end_time = min(end_time, audio_duration)
                
                # Current word and all previous words (progressive build)
                current_words = words[:i+1]
                display_text = ' '.join(current_words)
                
                try:
                    # ✅ APPLY EFFECT SETTINGS
                    stroke_color = effect_config.get('stroke_color', 'black')
                    stroke_width = effect_config.get('stroke_width', 2)
                    font_color = effect_config.get('font_color', text_color)
                    
                    # Highlight current word with effect
                    if text_effect == 'glow':
                        # Current word gets glow effect
                        font_color = effect_config.get('glow_color', '#FFD700')
                    elif text_effect == 'neon':
                        font_color = effect_config.get('neon_color', '#00FFFF')
                    elif text_effect == 'typewriter':
                        # Typewriter effect - all text but current word highlighted
                        font_color = text_color
                    
                    txt_clip = TextClip(
                        display_text,
                        fontsize=font_size,
                        color=font_color,
                        font='Arial-Bold',
                        stroke_color=stroke_color,
                        stroke_width=stroke_width,
                        size=(video_clip.w * 0.9, None),
                        method='caption',
                        align='center'
                    ).set_position(position).set_start(start_time).set_duration(end_time - start_time)
                    
                    text_clips.append(txt_clip)
                    
                except Exception as e:
                    st.warning(f"⚠️ Error creating text for word {i+1}: {str(e)}")
                    continue
            
            if not text_clips:
                st.warning("⚠️ No text clips created, using normal subtitle")
                return self._add_normal_subtitle(video_clip, text, font_size, text_color, text_position, text_effect)
            
            st.info(f"🔄 Compositing {len(text_clips)} word segments with {effect_config['name']}...")
            result = CompositeVideoClip([video_clip] + text_clips)
            
            return result
            
        except Exception as e:
            st.error(f"❌ Word-by-word karaoke error: {str(e)}")
            raise e'''

content = content.replace(old_karaoke_method, new_karaoke_method)

with open('utils/video_editor.py', 'w') as f:
    f.write(content)

print("✅ Karaoke timing diperbaiki untuk kata demi kata")
PYTHONCODE
