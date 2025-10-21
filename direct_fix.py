# Solusi langsung - tambahkan fungsi di apps/main.py
with open('apps/main.py', 'r') as f:
    content = f.read()

# Tambahkan fungsi estimate_word_count langsung di main.py sebelum class definition
if 'def estimate_word_count(' not in content:
    # Cari tempat yang tepat untuk menambahkan fungsi
    # Tambahkan setelah import statements dan sebelum class definition
    
    # Pattern untuk menemukan setelah imports dan sebelum class
    lines = content.split('\n')
    new_lines = []
    function_added = False
    
    for i, line in enumerate(lines):
        new_lines.append(line)
        
        # Setelah semua imports, tambahkan fungsi
        if not function_added and line.strip() and not line.startswith(('import', 'from', '#')) and 'class ' in line:
            # Tambahkan fungsi sebelum class
            estimate_function = '''
def estimate_word_count(duration_seconds):
    """
    Estimate word count based on duration in seconds
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
            new_lines.insert(i, estimate_function)
            function_added = True
            break
    
    content = '\n'.join(new_lines)

# Juga perbaiki pemanggilan fungsi
content = content.replace(
    "word_range = story_generator._estimate_word_count(settings['duration'])",
    "word_range = estimate_word_count(settings['duration'])"
)

with open('apps/main.py', 'w') as f:
    f.write(content)

print("✅ Fungsi estimate_word_count telah ditambahkan langsung di main.py!")
