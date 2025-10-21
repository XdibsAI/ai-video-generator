#!/bin/bash

# Perbaiki error indentasi di main.py
python3 << 'PYTHONCODE'
import re

# Baca file main.py
with open('apps/main.py', 'r') as f:
    lines = f.readlines()

# Perbaiki indentasi
fixed_lines = []
in_class = False
class_indent = 0

for i, line in enumerate(lines):
    # Deteksi awal class
    if line.strip().startswith('class VideoGeneratorApp:'):
        in_class = True
        class_indent = len(line) - len(line.lstrip())
        fixed_lines.append(line)
        continue
    
    # Jika dalam class, perbaiki indentasi method
    if in_class and line.strip():
        current_indent = len(line) - len(line.lstrip())
        
        # Jika ini adalah method definition (def ...)
        if line.strip().startswith('def ') and current_indent <= class_indent:
            # Method harus di-indent 4 spasi dari class
            fixed_line = ' ' * (class_indent + 4) + line.lstrip()
            fixed_lines.append(fixed_line)
        elif line.strip() and current_indent < class_indent + 4:
            # Line lainnya harus di-indent minimal 8 spasi dari class
            fixed_line = ' ' * (class_indent + 8) + line.lstrip()
            fixed_lines.append(fixed_line)
        else:
            fixed_lines.append(line)
    else:
        fixed_lines.append(line)

# Tulis file yang sudah diperbaiki
with open('apps/main.py', 'w') as f:
    f.writelines(fixed_lines)

print("✅ Indentasi diperbaiki")
PYTHONCODE
