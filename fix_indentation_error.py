"""
Quick fix untuk indentasi error di line 314
"""

def fix_indentation():
    # Baca file
    with open('apps/main.py', 'r') as f:
        lines = f.readlines()
    
    # Perbaiki line 314 (index 313 karena zero-based)
    if len(lines) > 313:
        print(f"Line 314 sebelum: {repr(lines[313])}")
        
        # Cari blok yang bermasalah - kemungkinan di sekitar method render_story_generator
        for i in range(300, 330):
            if i < len(lines):
                print(f"Line {i+1}: {repr(lines[i])}")
    
    # Cari pattern yang umum bermasalah
    problematic_lines = []
    for i, line in enumerate(lines):
        if line.strip().startswith('with st.spinner') and 'Generate 3 Cerita Options' in line:
            print(f"Found spinner at line {i+1}")
            # Periksa indentasi setelah ini
    
    print("\n🔧 Applying automatic indentation fix...")
    
    # Rebuild file dengan indentasi yang konsisten
    fixed_lines = []
    indent_level = 0
    in_multiline_string = False
    
    for line in lines:
        stripped = line.strip()
        
        # Skip empty lines
        if not stripped:
            fixed_lines.append(line)
            continue
            
        # Handle multiline strings
        if '"""' in line or "'''" in line:
            if not in_multiline_string:
                in_multiline_string = True
            else:
                in_multiline_string = False
        
        # Jika dalam multiline string, jangan ubah indentasi
        if in_multiline_string:
            fixed_lines.append(line)
            continue
            
        # Adjust indent level based on syntax
        if stripped.startswith(('def ', 'class ', 'if ', 'for ', 'while ', 'with ', 'try:')):
            # Line baru dengan indentasi proper
            fixed_line = '    ' * indent_level + stripped
            fixed_lines.append(fixed_line + '\n')
            if stripped.endswith(':'):
                indent_level += 1
        elif stripped.startswith(('return', 'break', 'continue', 'pass')):
            fixed_line = '    ' * (indent_level - 1) + stripped
            fixed_lines.append(fixed_line + '\n')
        elif stripped.startswith('elif ') or stripped.startswith('else:'):
            fixed_line = '    ' * (indent_level - 1) + stripped
            fixed_lines.append(fixed_line + '\n')
        elif stripped.startswith('except') or stripped.startswith('finally:'):
            fixed_line = '    ' * (indent_level - 1) + stripped
            fixed_lines.append(fixed_line + '\n')
        else:
            fixed_line = '    ' * indent_level + stripped
            fixed_lines.append(fixed_line + '\n')
            
        # Kurangi indent level jika line berakhir dengan kata kunci yang mengurangi indent
        if stripped in ['return', 'break', 'continue', 'pass']:
            indent_level = max(0, indent_level - 1)
    
    # Backup original file
    import shutil
    shutil.copy2('apps/main.py', 'apps/main.py.backup_indent_fix')
    
    # Write fixed file
    with open('apps/main.py', 'w') as f:
        f.writelines(fixed_lines)
    
    print("✅ Indentation fixed! Backup saved as apps/main.py.backup_indent_fix")

if __name__ == "__main__":
    fix_indentation()
