"""
Quick patch untuk testing karaoke fix
"""

import streamlit as st
import os
import sys

def apply_quick_fix():
    """Apply quick fixes untuk testing"""
    
    st.warning("🔧 Applying quick karaoke fixes...")
    
    # Fix 1: Simple karaoke dengan timing dasar
    simple_fix = """
    # SIMPLE KARAOKE FIX - tambahkan di video_editor.py
    def _add_simple_karaoke(self, video_clip, text, font_size, text_color, position, duration):
        \"\"\"Simple karaoke fallback\"\"\"
        try:
            words = text.split()
            word_duration = duration / len(words)
            text_clips = []
            
            for i, word in enumerate(words):
                start_time = i * word_duration
                end_time = (i + 1) * word_duration
                
                txt_clip = TextClip(
                    word,
                    fontsize=font_size,
                    color=text_color,
                    font='Arial-Bold',
                    stroke_color='black',
                    stroke_width=2,
                    size=(video_clip.w * 0.8, None),
                    method='label'
                ).set_position(position).set_start(start_time).set_duration(word_duration)
                
                text_clips.append(txt_clip)
            
            return CompositeVideoClip([video_clip] + text_clips)
        except Exception as e:
            st.error(f"Simple karaoke failed: {e}")
            return video_clip
    """
    
    # Fix 2: Pastikan text clips benar-benar ditambahkan
    composite_fix = """
    # PASTIKAN TEXT CLIPS TERATTACH - di video_editor.py
    if text_clips:
        st.info(f"🎯 Adding {len(text_clips)} text segments to video...")
        
        # Debug info
        for i, clip in enumerate(text_clips[:3]):  # Show first 3
            st.write(f"Segment {i+1}: '{clip.text}' at {clip.start}s for {clip.duration}s")
        
        final_clip = CompositeVideoClip([video_clip] + text_clips)
        final_clip = final_clip.set_duration(video_clip.duration)
        
        st.success("✅ Text clips composited successfully!")
        return final_clip
    else:
        st.warning("❌ No text clips to add")
        return video_clip
    """
    
    return simple_fix, composite_fix

if __name__ == "__main__":
    apply_quick_fix()
    print("✅ Quick fixes ready for testing")
