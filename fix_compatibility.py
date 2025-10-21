# Fix untuk estimate_word_count - samakan dengan story_generator
with open('utils/compatibility.py', 'r') as f:
    content = f.read()

# Ganti implementasi estimate_word_count
new_estimate_function = '''
def estimate_word_count(duration_seconds):
    """
    Estimate word count based on duration in seconds
    Consistent with story_generator implementation
    """
    if duration_seconds == 30:
        return (50, 80)
    elif duration_seconds == 60:
        return (100, 150)
    elif duration_seconds == 90:
        return (150, 200)
    else:
        words_per_second = 2.5
        estimated_words = int(duration_seconds * words_per_second)
        return (estimated_words - 20, estimated_words + 20)
'''

# Replace the function
import re
pattern = r'def estimate_word_count\(duration_seconds\):.*?return \(min_words, max_words\)'
content = re.sub(pattern, new_estimate_function, content, flags=re.DOTALL)

with open('utils/compatibility.py', 'w') as f:
    f.write(content)

print("✅ estimate_word_count telah diperbaiki!")
