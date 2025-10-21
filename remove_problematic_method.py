# Hapus method yang bermasalah
python3 << 'PYTHONCODE'
import re

with open('utils/story_generator.py', 'r') as f:
    content = f.read()

# Hapus method generate_stories_with_session_fix
content = re.sub(r'def generate_stories_with_session_fix.*?user_description=""":.*?return self\._generate_dummy_stories.*?\)\n', '', content, flags=re.DOTALL)

with open('utils/story_generator.py', 'w') as f:
    f.write(content)

print("✅ Method bermasalah dihapus")
PYTHONCODE
