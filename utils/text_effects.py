import streamlit as st
from typing import Dict, List, Tuple
import random

class TextEffects:
    def __init__(self):
        self.effects = {
            'none': {
                'name': 'Tidak Ada Efek',
                'description': 'Teks polos tanpa efek',
                'stroke_color': 'black',
                'stroke_width': 2,
                'font_color': '#FFFFFF',
                'shadow': False,
                'gradient': False
            },
            'glow': {
                'name': 'Glow Effect',
                'description': 'Teks dengan efek cahaya',
                'stroke_color': '#FFD700',
                'stroke_width': 4,
                'font_color': '#FFFFFF',
                'shadow': True,
                'glow_color': '#FFD700',
                'glow_intensity': 3
            },
            'neon': {
                'name': 'Neon Effect', 
                'description': 'Efek neon menyala',
                'stroke_color': '#00FFFF',
                'stroke_width': 3,
                'font_color': '#FFFFFF',
                'shadow': True,
                'neon_color': '#00FFFF',
                'blink': False
            },
            'shadow': {
                'name': 'Shadow Effect',
                'description': 'Teks dengan bayangan',
                'stroke_color': 'black',
                'stroke_width': 2,
                'font_color': '#FFFFFF',
                'shadow': True,
                'shadow_color': '#000000',
                'shadow_offset': (2, 2)
            },
            'gradient': {
                'name': 'Gradient Effect',
                'description': 'Teks dengan gradien warna',
                'stroke_color': 'black',
                'stroke_width': 2,
                'font_color': 'linear',
                'gradient_colors': ['#FF6B6B', '#4ECDC4'],
                'gradient_direction': 'horizontal'
            },
            'outline': {
                'name': 'Outline Bold',
                'description': 'Teks dengan outline tebal',
                'stroke_color': '#FF4444',
                'stroke_width': 5,
                'font_color': '#FFFFFF',
                'shadow': False
            },
            'retro': {
                'name': 'Retro Style',
                'description': 'Gaya retro tahun 80an',
                'stroke_color': '#FF00FF',
                'stroke_width': 3,
                'font_color': '#00FF00',
                'shadow': True,
                'shadow_color': '#FF00FF'
            },
            'elegant': {
                'name': 'Elegant Gold',
                'description': 'Teks emas elegan',
                'stroke_color': '#D4AF37',
                'stroke_width': 3,
                'font_color': '#FFD700',
                'shadow': True,
                'shadow_color': '#B8860B'
            },
            'fire': {
                'name': 'Fire Effect',
                'description': 'Efek api menyala',
                'stroke_color': '#FF4500',
                'stroke_width': 4,
                'font_color': '#FF8C00',
                'shadow': True,
                'shadow_color': '#FF0000'
            },
            'ice': {
                'name': 'Ice Effect',
                'description': 'Efek es/dingin',
                'stroke_color': '#00BFFF',
                'stroke_width': 4,
                'font_color': '#E0FFFF',
                'shadow': True,
                'shadow_color': '#1E90FF'
            }
        }
    
    def get_effect(self, effect_name: str) -> Dict:
        """Get effect configuration by name"""
        return self.effects.get(effect_name, self.effects['none'])
    
    def get_all_effects(self) -> List[str]:
        """Get list of all available effects"""
        return list(self.effects.keys())
    
    def get_effect_display_info(self, effect_name: str) -> Tuple[str, str]:
        """Get effect name and description for display"""
        effect = self.get_effect(effect_name)
        return effect['name'], effect['description']
    
    def generate_preview_css(self, effect_name: str, font_size: int = 60) -> str:
        """Generate CSS for effect preview"""
        effect = self.get_effect(effect_name)
        
        base_css = f"""
            font-size: {font_size}px;
            font-weight: bold;
            font-family: 'Arial Black', sans-serif;
            text-align: center;
            padding: 20px;
            margin: 10px;
            border-radius: 10px;
        """
        
        if effect_name == 'none':
            return base_css + f"""
                color: {effect['font_color']};
                text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
            """
        
        elif effect_name == 'glow':
            return base_css + f"""
                color: {effect['font_color']};
                text-shadow: 
                    0 0 5px {effect['glow_color']},
                    0 0 10px {effect['glow_color']},
                    0 0 15px {effect['glow_color']},
                    0 0 20px {effect['glow_color']};
            """
        
        elif effect_name == 'neon':
            return base_css + f"""
                color: {effect['font_color']};
                text-shadow:
                    0 0 5px #fff,
                    0 0 10px #fff,
                    0 0 15px {effect['neon_color']},
                    0 0 20px {effect['neon_color']},
                    0 0 25px {effect['neon_color']};
            """
        
        elif effect_name == 'shadow':
            return base_css + f"""
                color: {effect['font_color']};
                text-shadow: 
                    {effect['shadow_offset'][0]}px {effect['shadow_offset'][1]}px 4px {effect['shadow_color']};
            """
        
        elif effect_name == 'gradient':
            colors = effect['gradient_colors']
            if effect['gradient_direction'] == 'horizontal':
                gradient = f"linear-gradient(to right, {colors[0]}, {colors[1]})"
            else:
                gradient = f"linear-gradient(to bottom, {colors[0]}, {colors[1]})"
            
            return base_css + f"""
                background: {gradient};
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
            """
        
        elif effect_name == 'outline':
            return base_css + f"""
                color: {effect['font_color']};
                text-shadow:
                    -1px -1px 0 {effect['stroke_color']},
                    1px -1px 0 {effect['stroke_color']},
                    -1px 1px 0 {effect['stroke_color']},
                    1px 1px 0 {effect['stroke_color']},
                    0 0 10px {effect['stroke_color']};
            """
        
        elif effect_name == 'retro':
            return base_css + f"""
                color: {effect['font_color']};
                text-shadow:
                    2px 2px 0 {effect['stroke_color']},
                    4px 4px 0 {effect['shadow_color']};
            """
        
        elif effect_name == 'elegant':
            return base_css + f"""
                color: {effect['font_color']};
                text-shadow:
                    0 0 5px {effect['stroke_color']},
                    0 0 10px {effect['stroke_color']},
                    2px 2px 4px {effect['shadow_color']};
            """
        
        elif effect_name == 'fire':
            return base_css + f"""
                color: {effect['font_color']};
                text-shadow:
                    0 0 5px #FF8C00,
                    0 0 10px #FF4500,
                    0 0 15px #FF0000,
                    0 0 20px #FF0000;
            """
        
        elif effect_name == 'ice':
            return base_css + f"""
                color: {effect['font_color']};
                text-shadow:
                    0 0 5px #E0FFFF,
                    0 0 10px #00BFFF,
                    0 0 15px #1E90FF,
                    0 0 20px #0000FF;
            """
        
        return base_css

    def render_effect_preview(self, effect_name: str, sample_text: str = "Sample Text", font_size: int = 60):
        """Render effect preview in Streamlit"""
        effect_css = self.generate_preview_css(effect_name, font_size)
        
        st.markdown(f"""
            <div style="{effect_css}">
                {sample_text}
            </div>
        """, unsafe_allow_html=True)
    
    def render_effects_gallery(self, selected_effect: str = 'none', sample_text: str = "Karaoke Text", font_size: int = 60):
        """Render gallery of all effects dengan preview"""
        st.subheader("🎨 Gallery Efek Teks")
        
        # Grid layout untuk effects
        cols = st.columns(3)
        
        for idx, effect_name in enumerate(self.get_all_effects()):
            with cols[idx % 3]:
                effect_display_name, effect_description = self.get_effect_display_info(effect_name)
                
                # Preview box
                st.markdown(f"""
                    <div style='
                        border: 2px solid {'#4ECDC4' if effect_name == selected_effect else '#e0e0e0'};
                        border-radius: 10px;
                        padding: 10px;
                        margin: 5px;
                        background: {'#f0fff0' if effect_name == selected_effect else '#f9f9f9'};
                        cursor: pointer;
                        transition: all 0.3s ease;
                    '>
                """, unsafe_allow_html=True)
                
                # Effect preview
                self.render_effect_preview(effect_name, sample_text, font_size - 20)
                
                # Effect info
                st.markdown(f"**{effect_display_name}**")
                st.caption(effect_description)
                
                # Select button
                if st.button("Pilih", key=f"select_{effect_name}", use_container_width=True):
                    st.session_state.selected_text_effect = effect_name
                    st.rerun()
                
                st.markdown("</div>", unsafe_allow_html=True)

# Singleton instance
text_effects = TextEffects()

def get_text_effect_config(effect_name: str):
    """Get effect configuration for video rendering"""
    return text_effects.get_effect(effect_name)

def preview_text_effect(effect_name: str, sample_text: str, font_size: int = 60):
    """Preview text effect in Streamlit"""
    text_effects.render_effect_preview(effect_name, sample_text, font_size)
