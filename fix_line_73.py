"""
Fix spesifik untuk error di line 73
"""

def fix_line_73_error():
    with open('apps/main.py', 'r') as f:
        lines = f.readlines()
    
    print("🔍 Analyzing line 73 error...")
    
    # Periksa line 72-74
    for i in range(70, 76):
        if i < len(lines):
            print(f"Line {i+1}: {lines[i].rstrip()}")
    
    # Cari try sebelum except di line 73
    found_try = False
    try_line = -1
    
    for i in range(65, 73):  # Cari dari line 66-72
        if i < len(lines) and 'try:' in lines[i]:
            found_try = True
            try_line = i
            break
    
    if not found_try:
        print("❌ No try block found before except at line 73")
        print("🔧 Adding try block...")
        
        # Buat file fixed
        fixed_lines = []
        for i, line in enumerate(lines):
            if i == 72:  # Sebelum line 73
                # Tambahkan try block dengan indent yang sama
                indent = len(line) - len(line.lstrip())
                fixed_lines.append(' ' * indent + "try:\n")
                fixed_lines.append(' ' * (indent + 4) + "# Temporary try for imports\n")
            
            fixed_lines.append(line)
        
        with open('apps/main_fixed_line73.py', 'w') as f:
            f.writelines(fixed_lines)
        
        print("✅ Fixed version created: apps/main_fixed_line73.py")
    else:
        print(f"✅ Try block found at line {try_line + 1}")
        print("❓ Error might be different")

fix_line_73_error()
