"""
Perbaiki error spesifik tanpa menghilangkan fitur
"""

def fix_specific_errors():
    with open('apps/main_backup_with_errors.py', 'r') as f:
        content = f.read()
    
    # Perbaikan 1: Area imports (sekitar line 73)
    # Cari pattern try-except yang bermasalah
    lines = content.split('\n')
    fixed_lines = []
    
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # Perbaikan untuk area imports (sekitar line 53-73)
        if i >= 50 and i <= 80 and 'except ImportError as e:' in line:
            # Cek apakah ada try sebelumnya
            has_try = False
            for j in range(max(0, i-5), i):
                if 'try:' in lines[j]:
                    has_try = True
                    break
            
            if not has_try:
                print(f"🔧 Adding try block before line {i+1}")
                indent = len(line) - len(line.lstrip())
                fixed_lines.append(' ' * indent + "try:\n")
                fixed_lines.append(' ' * (indent + 4) + "# Import attempt\n")
        
        fixed_lines.append(line)
        i += 1
    
    # Tulis file fixed
    fixed_content = '\n'.join(fixed_lines)
    
    # Perbaikan lainnya: pastikan semua try punya except
    import re
    
    # Pattern untuk cari try tanpa except
    try_pattern = r'try:'
    except_pattern = r'except'
    
    # Hitung try dan except
    try_count = len(re.findall(try_pattern, fixed_content))
    except_count = len(re.findall(except_pattern, fixed_content))
    
    print(f"Try blocks: {try_count}, Except blocks: {except_count}")
    
    if try_count > except_count:
        print("⚠️  Adding missing except blocks...")
        # Tambahkan except untuk try yang missing
        lines = fixed_content.split('\n')
        fixed_lines = []
        i = 0
        
        while i < len(lines):
            line = lines[i]
            fixed_lines.append(line)
            
            if 'try:' in line and i + 1 < len(lines):
                # Cek 10 line berikutnya ada except atau tidak
                has_except = False
                for j in range(i + 1, min(i + 15, len(lines))):
                    if 'except' in lines[j] or 'finally:' in lines[j]:
                        has_except = True
                        break
                
                if not has_except:
                    print(f"🔧 Adding except for try at line {i+1}")
                    indent = len(line) - len(line.lstrip())
                    next_line = lines[i + 1] if i + 1 < len(lines) else ""
                    next_indent = len(next_line) - len(next_line.lstrip()) if next_line.strip() else indent + 4
                    
                    fixed_lines.append(' ' * next_indent + "except Exception as e:")
                    fixed_lines.append(' ' * (next_indent + 4) + f"st.warning(f\"Import warning: {{e}}\")")
            
            i += 1
        
        fixed_content = '\n'.join(fixed_lines)
    
    # Save fixed file
    with open('apps/main_fixed_complete.py', 'w') as f:
        f.write(fixed_content)
    
    print("✅ Complete fixed version created")

fix_specific_errors()
