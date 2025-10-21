#!/bin/bash

# Backup file
cp apps/main.py apps/main.py.backup_indent

# Perbaiki indentasi dengan Python
python3 << 'PYTHONCODE'
import re

# Baca file
with open('apps/main.py', 'r') as f:
    content = f.read()

# Perbaiki indentasi untuk class VideoGeneratorApp
lines = content.split('\n')
fixed_lines = []
in_class = False
class_indent = 0

for i, line in enumerate(lines):
    # Cari awal class VideoGeneratorApp
    if 'class VideoGeneratorApp:' in line and not in_class:
        in_class = True
        class_indent = len(line) - len(line.lstrip())
        fixed_lines.append(line)
        continue
    
    # Jika dalam class, perbaiki indentasi method
    if in_class and line.strip():
        current_indent = len(line) - len(line.lstrip())
        # Jika indentasi kurang dari class_indent + 4, perbaiki
        if current_indent < class_indent + 4 and line.strip():
            fixed_line = ' ' * (class_indent + 4) + line.lstrip()
            fixed_lines.append(fixed_line)
        else:
            fixed_lines.append(line)
    else:
        fixed_lines.append(line)

# Tulis file yang sudah diperbaiki
with open('apps/main.py', 'w') as f:
    f.write('\n'.join(fixed_lines))

print("✅ Indentasi telah diperbaiki")
PYTHONCODE
