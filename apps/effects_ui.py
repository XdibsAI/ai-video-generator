    def render_text_effects_section(self):
        """Render text effects selection dengan preview"""
        st.subheader("🎨 Efek Teks Karaoke")
        
        # Initialize selected effect
        if 'selected_text_effect' not in st.session_state:
            st.session_state.selected_text_effect = 'none'
        
        # Sample text untuk preview
        sample_text = st.text_input(
            "Teks Preview:",
            value="Karaoke Effect Preview",
            key="effect_preview_text"
        )
        
        # Font size untuk preview
        preview_font_size = st.slider(
            "Ukuran Font Preview:",
            min_value=30,
            max_value=100,
            value=60,
            key="preview_font_size"
        )
        
        # Render effects gallery
        from utils.text_effects import text_effects
        text_effects.render_effects_gallery(
            st.session_state.selected_text_effect,
            sample_text,
            preview_font_size
        )
        
        # Selected effect info
        selected_effect = st.session_state.selected_text_effect
        effect_name, effect_description = text_effects.get_effect_display_info(selected_effect)
        
        st.success(f"✅ Efek terpilih: **{effect_name}**")
        st.info(f"ℹ️ {effect_description}")
        
        return selected_effect
