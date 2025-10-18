import os
import time
import threading
import tempfile

class CleanupManager:
    def __init__(self):
        self.temp_dir = tempfile.gettempdir()
        self.cleanup_interval = 300  # 5 minutes
        self.max_file_age = 3600  # 1 hour
        self.running = False
        self.cleanup_thread = None
    
    def start_cleanup_service(self):
        """Start background cleanup service"""
        self.running = True
        self.cleanup_thread = threading.Thread(target=self._cleanup_worker, daemon=True)
        self.cleanup_thread.start()
        print("🔄 Cleanup service started")
    
    def stop_cleanup_service(self):
        """Stop background cleanup service"""
        self.running = False
        if self.cleanup_thread:
            self.cleanup_thread.join(timeout=5)
        print("🛑 Cleanup service stopped")
    
    def _cleanup_worker(self):
        """Background worker for file cleanup"""
        while self.running:
            try:
                self.cleanup_old_files()
                time.sleep(self.cleanup_interval)
            except Exception as e:
                print(f"Cleanup error: {e}")
                time.sleep(60)
    
    def cleanup_old_files(self):
        """Clean up files older than max_file_age"""
        current_time = time.time()
        files_cleaned = 0
        
        for filename in os.listdir(self.temp_dir):
            if filename.startswith(('tts_', 'video_')):
                filepath = os.path.join(self.temp_dir, filename)
                
                try:
                    if os.path.isfile(filepath):
                        file_age = current_time - os.path.getmtime(filepath)
                        
                        if file_age > self.max_file_age:
                            os.remove(filepath)
                            files_cleaned += 1
                            print(f"🧹 Cleaned up: {filename}")
                            
                except Exception as e:
                    print(f"Error cleaning {filename}: {e}")
        
        if files_cleaned > 0:
            print(f"✅ Cleaned up {files_cleaned} old files")
    
    def get_storage_info(self):
        """Get storage usage information"""
        return {
            "total_files": "N/A",
            "total_size_mb": "N/A", 
            "max_age_minutes": self.max_file_age // 60
        }

# Singleton instance
cleanup_manager = CleanupManager()

# Auto-start cleanup service when module is imported
cleanup_manager.start_cleanup_service()
