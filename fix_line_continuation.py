#!/bin/bash

# Perbaiki error line continuation character
python3 << 'PYTHONCODE'
import re

with open('apps/main.py', 'r') as f:
    content = f.read()

# Perbaiki semua \\n yang tidak properly escaped
content = content.replace('\\n\\n', '\n\n')
content = content.replace('\\n', '\n')

# Hapus karakter backslash yang tidak perlu
content = re.sub(r'[\\]+n', '\n', content)

with open('apps/main.py', 'w') as f:
    f.write(content)

print("✅ Line continuation errors fixed")
PYTHONCODE
