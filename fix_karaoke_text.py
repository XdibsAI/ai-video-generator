"""
Script untuk memperbaiki masalah karaoke text tidak muncul
"""

def fix_karaoke_timing():
    """Perbaikan timing karaoke yang lebih reliable"""
    
    fix_code = '''
    def _add_punctuation_aware_karaoke(self, video_clip, text, font_size, text_color, text_position, audio_duration, text_effect='none'):
        """Add karaoke dengan text effects - FIXED VERSION"""
        try:
            st.info("🎤 Creating punctuation-aware karaoke with effects...")
            
            # Get effect config
            effect_config = get_text_effect_config(text_effect)
            
            # Calculate position - FIXED POSITION
            if text_position == 'middle':
                position = ('center', 'center')  # FIX: Use 'center' instead of pixel calculation
            else:
                position = ('center', video_clip.h * 0.85)
            
            text_clips = []
            
            # Get punctuation-aware timings - ADD ERROR HANDLING
            try:
                timings = text_processor.create_punctuation_aware_karaoke(text, audio_duration)
            except Exception as e:
                st.warning(f"⚠️ Karaoke timing error, using fallback: {str(e)}")
                # Fallback: split by words with equal timing
                words = text.split()
                word_duration = audio_duration / max(len(words), 1)
                timings = []
                for i, word in enumerate(words):
                    timings.append({
                        'text': word,
                        'start_time': i * word_duration,
                        'end_time': (i + 1) * word_duration,
                        'has_punctuation': False,
                        'punctuation': ''
                    })
            
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
                duration = end_time - start_time
                
                # Skip if duration is too short
                if duration < 0.1:
                    continue
                    
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
                    
                    # FIX: Use simpler text clip creation
                    txt_clip = TextClip(
                        chunk_text,
                        fontsize=font_size,
                        color=font_color,
                        font='Arial-Bold',
                        stroke_color=stroke_color,
                        stroke_width=stroke_width,
                        size=(video_clip.w * 0.8, None),  # FIX: Reduce width for better fit
                        method='label'  # FIX: Use label method for better compatibility
                    )
                    
                    # FIX: Set position and timing
                    txt_clip = txt_clip.set_position(position)
                    txt_clip = txt_clip.set_start(start_time)
                    txt_clip = txt_clip.set_duration(duration)
                    
                    text_clips.append(txt_clip)
                    
                except Exception as e:
                    st.warning(f"⚠️ Error creating text for '{chunk_text}': {str(e)}")
                    continue

            if not text_clips:
                st.warning("⚠️ No text clips created, using normal subtitle")
                return self._add_normal_subtitle(video_clip, text, font_size, text_color, text_position, text_effect)
            
            st.info(f"🔄 Compositing {len(text_clips)} segments with {effect_config['name']}...")
            
            # FIX: Ensure video clip has audio and proper duration
            final_video = CompositeVideoClip([video_clip] + text_clips)
            final_video = final_video.set_duration(audio_duration)
            
            return final_video
            
        except Exception as e:
            st.error(f"❌ Punctuation-aware karaoke error: {str(e)}")
            import traceback
            st.error(f"Detailed error: {traceback.format_exc()}")
            return video_clip
    '''
    
    return fix_code

def fix_text_effects_ui():
    """Perbaikan UI untuk text effects preview"""
    
    fix_code = '''
    def render_text_effects_section(self):
        """Render text effects selection dengan preview - FIXED UI"""
        st.subheader("🎨 Efek Teks Karaoke")
        
        # Container untuk preview yang lebih rapi
        with st.container():
            col1, col2 = st.columns([2, 1])
            
            with col1:
                # Sample text untuk preview
                sample_text = st.text_input(
                    "Teks Preview:",
                    value="Contoh Teks Karaoke",
                    key="effect_preview_text",
                    help="Teks untuk melihat preview efek"
                )
            
            with col2:
                # Font size untuk preview
                preview_font_size = st.slider(
                    "Ukuran Font:",
                    min_value=30,
                    max_value=100,
                    value=60,
                    key="preview_font_size"
                )
        
        # Garis pemisah
        st.markdown("---")
        
        # Render effects gallery dengan layout yang lebih baik
        st.subheader("✨ Pilih Efek Teks")
        
        # Gunakan columns untuk layout efek yang lebih rapi
        effects = text_effects.get_available_effects()
        cols = st.columns(3)
        
        selected_effect = st.session_state.selected_text_effect
        
        for idx, effect in enumerate(effects):
            with cols[idx % 3]:
                effect_name, effect_desc = text_effects.get_effect_display_info(effect)
                
                # Tombol radio style
                is_selected = (selected_effect == effect)
                button_label = f"✅ {effect_name}" if is_selected else effect_name
                
                if st.button(
                    button_label,
                    key=f"effect_btn_{effect}",
                    use_container_width=True,
                    type="primary" if is_selected else "secondary"
                ):
                    st.session_state.selected_text_effect = effect
                    st.rerun()
                
                # Preview kecil
                st.caption(effect_desc)
        
        # Preview area yang lebih terorganisir
        st.markdown("---")
        st.subheader("👁️ Preview Efek")
        
        # Container preview dengan border
        preview_html = f"""
        <div style='
            border: 2px solid #e0e0e0;
            border-radius: 10px;
            padding: 30px;
            margin: 10px 0;
            text-align: center;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 150px;
            display: flex;
            align-items: center;
            justify-content: center;
        '>
            <div style='
                font-size: {preview_font_size}px;
                font-weight: bold;
                color: {text_effects.get_effect_config(selected_effect).get('font_color', '#FFFFFF')};
                text-shadow: {text_effects.get_effect_config(selected_effect).get('text_shadow', '2px 2px 4px rgba(0,0,0,0.5)')};
                padding: 20px;
            '>
                {sample_text}
            </div>
        </div>
        """
        
        st.markdown(preview_html, unsafe_allow_html=True)
        
        # Info efek terpilih
        effect_name, effect_description = text_effects.get_effect_display_info(selected_effect)
        
        st.success(f"✅ **Efek Terpilih:** {effect_name}")
        st.info(f"ℹ️ {effect_description}")
        
        return selected_effect
    '''
    
    return fix_code

if __name__ == "__main__":
    print("🔧 Script perbaikan karaoke text dan UI ready!")
    print("📝 Copy kode di atas ke file yang sesuai:")
    print("1. Karaoke timing fix -> utils/video_editor.py")
    print("2. UI effects fix -> apps/main.py")
