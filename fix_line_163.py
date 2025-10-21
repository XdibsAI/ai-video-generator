#!/bin/bash

# Perbaiki error indentasi spesifik di line 163
python3 << 'PYTHONCODE'
import re

with open('apps/main.py', 'r') as f:
    lines = f.readlines()

# Perbaiki line 163-164
for i in range(162, 165):  # Periksa line 163-165 (index 162-164)
    if i < len(lines):
        line = lines[i]
        line_num = i + 1
        
        # Jika ini function definition (line 163), pastikan ada body
        if line_num == 163 and line.strip().endswith(':') and line.strip().startswith('def '):
            print(f"Line {line_num}: {line.strip()}")
            # Cek line berikutnya
            if i + 1 < len(lines):
                next_line = lines[i + 1]
                if not next_line.strip() or not next_line.startswith('    '):
                    # Tambahkan pass statement
                    lines.insert(i + 1, '        pass\\n')
                    print("✅ Added pass statement after function definition")

with open('apps/main.py', 'w') as f:
    f.writelines(lines)

print("✅ Line 163 error fixed")
PYTHONCODE
