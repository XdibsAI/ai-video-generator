"""
Perbaikan untuk text processor karaoke timing
"""

def improved_karaoke_timing():
    """Improved karaoke timing algorithm"""
    
    fix_code = '''
    def create_punctuation_aware_karaoke(self, text, total_duration):
        """Create karaoke timing dengan punctuation awareness - IMPROVED"""
        try:
            # Clean text
            text = self.clean_text(text)
            
            # Split into sentences first
            sentences = self.split_into_sentences(text)
            
            segments = []
            current_time = 0
            
            for sentence in sentences:
                if not sentence.strip():
                    continue
                    
                # Split sentence into words
                words = sentence.split()
                sentence_duration = total_duration * (len(sentence) / len(text))
                
                # Calculate word durations based on complexity
                word_durations = []
                total_chars = sum(len(word) for word in words)
                
                for word in words:
                    # Duration based on word length and punctuation
                    base_duration = (len(word) / total_chars) * sentence_duration
                    
                    # Adjust for punctuation
                    if word.endswith(('.', '!', '?')):
                        base_duration *= 1.5  # Longer pause for punctuation
                    elif word.endswith((',', ';', ':')):
                        base_duration *= 1.2
                    
                    word_durations.append(max(0.3, base_duration))  # Minimum duration
                
                # Normalize to fit sentence duration
                total_planned = sum(word_durations)
                if total_planned > 0:
                    word_durations = [dur * (sentence_duration / total_planned) for dur in word_durations]
                
                # Create segments
                for i, word in enumerate(words):
                    start_time = current_time
                    duration = word_durations[i] if i < len(word_durations) else 0.5
                    end_time = start_time + duration
                    
                    segments.append({
                        'text': word,
                        'start_time': start_time,
                        'end_time': end_time,
                        'has_punctuation': any(punc in word for punc in '.!?,;:'),
                        'punctuation': next((punc for punc in '.!?,;:' if punc in word), '')
                    })
                    
                    current_time = end_time
                
                # Add small pause after sentence
                current_time += 0.2
            
            # Normalize to total duration
            if segments and current_time > 0:
                scale_factor = total_duration / current_time
                for segment in segments:
                    segment['start_time'] *= scale_factor
                    segment['end_time'] *= scale_factor
            
            return segments
            
        except Exception as e:
            # Fallback: equal word timing
            words = text.split()
            word_duration = total_duration / max(len(words), 1)
            
            segments = []
            for i, word in enumerate(words):
                segments.append({
                    'text': word,
                    'start_time': i * word_duration,
                    'end_time': (i + 1) * word_duration,
                    'has_punctuation': any(punc in word for punc in '.!?,;:'),
                    'punctuation': next((punc for punc in '.!?,;:' if punc in word), '')
                })
            
            return segments
    '''
    
    return fix_code

if __name__ == "__main__":
    print("🔧 Improved karaoke timing algorithm ready!")
    print("📝 Copy to utils/text_processor.py")
