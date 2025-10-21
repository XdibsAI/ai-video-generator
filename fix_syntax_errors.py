"""
Fix syntax errors di main.py
"""

def fix_syntax_errors():
    with open('apps/main.py', 'r') as f:
        content = f.read()
    
    lines = content.split('\n')
    
    print("🔍 Analyzing syntax errors...")
    
    # Perbaiki common syntax errors
    fixed_lines = []
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # Periksa try tanpa except
        if 'try:' in line and i + 1 < len(lines):
            # Cari except yang sesuai
            found_except = False
            for j in range(i + 1, min(i + 10, len(lines))):
                if 'except' in lines[j] or 'finally:' in lines[j]:
                    found_except = True
                    break
            
            if not found_except:
                print(f"⚠️  Try without except at line {i+1}")
                # Tambahkan except pass
                fixed_lines.append(line)
                # Cari indent level
                indent = len(line) - len(line.lstrip())
                next_line = lines[i + 1] if i + 1 < len(lines) else ""
                next_indent = len(next_line) - len(next_line.lstrip()) if next_line.strip() else indent + 4
                
                fixed_lines.append(' ' * next_indent + "except Exception as e:")
                fixed_lines.append(' ' * (next_indent + 4) + "pass")
                i += 1  # Skip next line karena sudah kita handle
                continue
        
        # Periksa except tanpa try
        if line.strip().startswith('except') and i > 0:
            prev_line = lines[i-1].strip()
            if 'try:' not in prev_line and not any(l.strip().startswith('try:') for l in lines[max(0,i-5):i]):
                print(f"⚠️  Except without try at line {i+1}")
                # Hapus line ini atau comment out
                fixed_lines.append("# " + line + "  # COMMENTED: except without try")
            else:
                fixed_lines.append(line)
        
        else:
            fixed_lines.append(line)
        
        i += 1
    
    # Tulis file yang sudah diperbaiki
    with open('apps/main_fixed.py', 'w') as f:
        f.write('\n'.join(fixed_lines))
    
    print("✅ Fixed version created as apps/main_fixed.py")

if __name__ == "__main__":
    fix_syntax_errors()
