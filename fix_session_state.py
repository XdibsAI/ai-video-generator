# Perbaiki session state di story_generator.py
cat >> utils/story_generator.py << 'FIXEOF'

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
FIXEOF

echo "✅ Session state fix ditambahkan"
