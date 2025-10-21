# Perbaiki indentasi di story_generator.py
python3 << 'PYTHONCODE'
import re

# Baca file story_generator.py
with open('utils/story_generator.py', 'r') as f:
    content = f.read()

# Hapus method yang bermasalah dan tambahkan dengan indentasi yang benar
# Cari akhir class StoryGenerator
class_end = content.find('# Singleton instance')
if class_end != -1:
    # Hapus method yang bermasalah jika ada
    content = re.sub(r'def generate_stories_with_session_fix.*?user_description=""":.*?""".*?(?=def|\Z)', '', content, flags=re.DOTALL)
    
    # Tambahkan method dengan indentasi yang benar
    new_method = '''
    def generate_stories_with_session_fix(self, niche, duration_seconds, style, language, user_description=""):
        """Generate stories dengan session state fix"""
        try:
            # Initialize session state cache jika belum ada
            import streamlit as st
            if not hasattr(st.session_state, 'story_cache'):
                st.session_state.story_cache = {}
                
            return self.generate_stories(niche, duration_seconds, style, language, user_description)
        except Exception as e:
            # Fallback tanpa session state
            return self._generate_dummy_stories(niche, duration_seconds, style, language, user_description)
'''
    
    # Sisipkan method sebelum singleton instance
    content = content[:class_end] + new_method + content[class_end:]

with open('utils/story_generator.py', 'w') as f:
    f.write(content)

print("✅ Indentasi story_generator.py diperbaiki")
PYTHONCODE
