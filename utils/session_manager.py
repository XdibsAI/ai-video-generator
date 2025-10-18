import streamlit as st
import os
import json
import pickle
import tempfile
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class SessionManager:
    def __init__(self):
        self.session_dir = tempfile.gettempdir()
        self.session_file = os.path.join(self.session_dir, "video_generator_session.pkl")
        self.backup_file = os.path.join(self.session_dir, "video_generator_backup.json")
        self.max_session_age = timedelta(hours=24)  # Session expired setelah 24 jam
        
    def save_session(self):
        """Save session state to persistent storage"""
        try:
            session_data = {
                'timestamp': datetime.now().isoformat(),
                'story_generated': st.session_state.get('story_generated', False),
                'story_options': st.session_state.get('story_options', []),
                'selected_story_index': st.session_state.get('selected_story_index', 0),
                'story_text': st.session_state.get('story_text', ""),
                'audio_path': st.session_state.get('audio_path'),
                'video_path': st.session_state.get('video_path'),
                'uploaded_files_info': self._serialize_uploaded_files(),
                'optimized_content': st.session_state.get('optimized_content'),
                'background_music_path': st.session_state.get('background_music_path'),
                'last_activity': datetime.now().isoformat()
            }
            
            # Save as pickle (main)
            with open(self.session_file, 'wb') as f:
                pickle.dump(session_data, f)
                
            # Save as JSON backup
            with open(self.backup_file, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, ensure_ascii=False, indent=2)
                
            logger.info("Session saved successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error saving session: {e}")
            return False
    
    def load_session(self):
        """Load session state from persistent storage"""
        try:
            # Check if session file exists and is not too old
            if not os.path.exists(self.session_file):
                return False
                
            file_time = datetime.fromtimestamp(os.path.getctime(self.session_file))
            if datetime.now() - file_time > self.max_session_age:
                logger.info("Session expired, starting fresh")
                self.clear_session()
                return False
            
            # Load from pickle
            with open(self.session_file, 'rb') as f:
                session_data = pickle.load(f)
            
            # Restore to session state
            st.session_state.story_generated = session_data.get('story_generated', False)
            st.session_state.story_options = session_data.get('story_options', [])
            st.session_state.selected_story_index = session_data.get('selected_story_index', 0)
            st.session_state.story_text = session_data.get('story_text', "")
            st.session_state.audio_path = session_data.get('audio_path')
            st.session_state.video_path = session_data.get('video_path')
            st.session_state.optimized_content = session_data.get('optimized_content')
            st.session_state.background_music_path = session_data.get('background_music_path')
            
            logger.info("Session loaded successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error loading session: {e}")
            # Try JSON backup
            return self._load_from_backup()
    
    def _load_from_backup(self):
        """Try loading from JSON backup"""
        try:
            if not os.path.exists(self.backup_file):
                return False
                
            with open(self.backup_file, 'r', encoding='utf-8') as f:
                session_data = json.load(f)
            
            # Restore basic data
            st.session_state.story_generated = session_data.get('story_generated', False)
            st.session_state.story_text = session_data.get('story_text', "")
            st.session_state.audio_path = session_data.get('audio_path')
            st.session_state.video_path = session_data.get('video_path')
            st.session_state.optimized_content = session_data.get('optimized_content')
            
            logger.info("Session loaded from backup")
            return True
            
        except Exception as e:
            logger.error(f"Error loading backup: {e}")
            return False
    
    def _serialize_uploaded_files(self):
        """Serialize uploaded files info (files themselves can't be serialized)"""
        uploaded_files = st.session_state.get('uploaded_files', [])
        files_info = []
        
        for file in uploaded_files:
            if hasattr(file, 'name'):
                files_info.append({
                    'name': file.name,
                    'type': file.type,
                    'size': file.size
                })
        
        return files_info
    
    def clear_session(self):
        """Clear session data"""
        try:
            if os.path.exists(self.session_file):
                os.remove(self.session_file)
            if os.path.exists(self.backup_file):
                os.remove(self.backup_file)
            logger.info("Session cleared")
        except Exception as e:
            logger.error(f"Error clearing session: {e}")
    
    def get_session_info(self):
        """Get session information"""
        try:
            if os.path.exists(self.session_file):
                file_time = datetime.fromtimestamp(os.path.getctime(self.session_file))
                age = datetime.now() - file_time
                return {
                    'exists': True,
                    'age_minutes': int(age.total_seconds() / 60),
                    'file_size': os.path.getsize(self.session_file)
                }
            return {'exists': False}
        except:
            return {'exists': False}

# Singleton instance
session_manager = SessionManager()

def setup_persistent_session():
    """Setup persistent session - call this at app startup"""
    
    # Initialize session state jika belum ada
    if 'session_initialized' not in st.session_state:
        st.session_state.session_initialized = True
        st.session_state.story_generated = False
        st.session_state.story_options = []
        st.session_state.selected_story_index = 0
        st.session_state.story_text = ""
        st.session_state.audio_path = None
        st.session_state.video_path = None
        st.session_state.uploaded_files = []
        st.session_state.optimized_content = None
        st.session_state.background_music_path = None
        
        # Try to load previous session
        if session_manager.load_session():
            st.success("🔄 Previous session restored!")
    
    # Auto-save trigger
    if any([
        st.session_state.get('story_generated'),
        st.session_state.get('video_path'),
        st.session_state.get('audio_path')
    ]):
        session_manager.save_session()

def save_current_session():
    """Manual save session"""
    if session_manager.save_session():
        st.success("💾 Progress saved!")
    else:
        st.error("❌ Failed to save progress")

def clear_current_session():
    """Manual clear session"""
    session_manager.clear_session()
    # Reset session state
    for key in list(st.session_state.keys()):
        if key != 'session_initialized':
            del st.session_state[key]
    st.success("🗑️ Session cleared!")
    st.rerun()

def show_session_info():
    """Show session information in sidebar"""
    session_info = session_manager.get_session_info()
    
    if session_info['exists']:
        st.sidebar.info(f"💾 Session: {session_info['age_minutes']}m ago")
        
        if st.sidebar.button("💾 Save Progress"):
            save_current_session()
            
        if st.sidebar.button("🗑️ Clear Session"):
            clear_current_session()
    else:
        st.sidebar.info("💾 No saved session")
