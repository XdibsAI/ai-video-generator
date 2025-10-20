import re
import streamlit as st

class TextProcessor:
    def __init__(self):
        self.punctuation_marks = ['.', ',', '!', '?', ';', ':', '—', '-', '...']
        self.pause_durations = {
            '.': 0.8,   # Long pause for sentences
            '!': 0.8,   # Long pause for exclamation
            '?': 0.8,   # Long pause for questions
            '...': 0.6, # Medium pause for ellipsis
            ';': 0.5,   # Medium pause
            ':': 0.4,   # Short-medium pause
            ',': 0.3,   # Short pause for commas
            '—': 0.4,   # Medium pause for em dash
            '-': 0.2    # Very short pause for hyphen
        }
    
    def split_text_with_punctuation(self, text):
        """Split text into chunks based on punctuation with timing info"""
        
        # Pattern untuk split dengan menjaga punctuation
        pattern = r'([{}])'.format(''.join(re.escape(mark) for mark in self.punctuation_marks))
        
        # Split text sambil menjaga punctuation
        chunks = []
        current_chunk = ""
        
        for char in text:
            current_chunk += char
            if char in self.punctuation_marks:
                chunks.append(current_chunk.strip())
                current_chunk = ""
        
        # Add remaining text jika ada
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def calculate_chunk_timings(self, chunks, total_duration):
        """Calculate timings for each chunk based on punctuation"""
        
        # Hitung base duration tanpa punctuation pauses
        base_duration_per_char = total_duration / len(' '.join(chunks))
        
        chunk_timings = []
        current_time = 0
        
        for chunk in chunks:
            # Calculate base duration untuk chunk ini
            chunk_length = len(chunk)
            base_duration = chunk_length * base_duration_per_char
            
            # Check jika chunk berakhir dengan punctuation
            punctuation = None
            for mark in self.punctuation_marks:
                if chunk.endswith(mark):
                    punctuation = mark
                    break
            
            # Add pause time jika ada punctuation
            pause_duration = self.pause_durations.get(punctuation, 0) if punctuation else 0
            
            # Total duration untuk chunk ini
            chunk_duration = base_duration + pause_duration
            
            chunk_timings.append({
                'text': chunk,
                'start_time': current_time,
                'end_time': current_time + chunk_duration,
                'duration': chunk_duration,
                'has_punctuation': bool(punctuation),
                'punctuation': punctuation,
                'pause_duration': pause_duration
            })
            
            current_time += chunk_duration
        
        return chunk_timings
    
    def create_punctuation_aware_karaoke(self, text, audio_duration):
        """Create karaoke timing yang sync dengan punctuation di audio"""
        
        # Split text into punctuation-aware chunks
        chunks = self.split_text_with_punctuation(text)
        
        # Calculate timings dengan punctuation pauses
        timings = self.calculate_chunk_timings(chunks, audio_duration)
        
        return timings
    
    def optimize_for_display(self, text, max_line_length=30):
        """Optimize text untuk display dengan line breaks yang natural"""
        
        # Split into sentences first
        sentences = re.split(r'([.!?])', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        optimized_lines = []
        current_line = ""
        
        for segment in sentences:
            words = segment.split()
            
            for word in words:
                # Check jika adding word ini melebihi max line length
                if len(current_line) + len(word) + 1 <= max_line_length:
                    if current_line:
                        current_line += " " + word
                    else:
                        current_line = word
                else:
                    # Start new line
                    if current_line:
                        optimized_lines.append(current_line)
                    current_line = word
            
            # Add punctuation to current line
            if current_line and segment in self.punctuation_marks:
                current_line += segment
        
        # Add last line jika ada
        if current_line:
            optimized_lines.append(current_line)
        
        return optimized_lines

# Singleton instance
text_processor = TextProcessor()

def test_punctuation_timing():
    """Test function untuk lihat bagaimana timing bekerja"""
    test_text = "Halo, nama saya AI. Senang bertemu dengan Anda! Apa kabar?"
    processor = TextProcessor()
    
    timings = processor.create_punctuation_aware_karaoke(test_text, 10.0)
    
    for timing in timings:
        print(f"'{timing['text']}' | {timing['start_time']:.2f}s - {timing['end_time']:.2f}s | Pause: {timing['pause_duration']:.2f}s")
    
    return timings

if __name__ == "__main__":
    test_punctuation_timing()
