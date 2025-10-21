"""
Hapus sementara section imports yang problematic
"""

def remove_problematic_section():
    with open('apps/main_before_line73_fix.py', 'r') as f:
        lines = f.readlines()
    
    # Temukan area problematic (sekitar line 70-80)
    start_line = 68
    end_line = 78
    
    print("🔧 Removing problematic import section...")
    
    fixed_lines = []
    for i, line in enumerate(lines):
        if i >= start_line and i <= end_line:
            if 'except ImportError as e:' in line:
                fixed_lines.append("# " + line.rstrip() + "  # REMOVED: problematic except\n")
            elif 'st.error(f"❌ Import Error:' in line:
                fixed_lines.append("# " + line.rstrip() + "  # REMOVED: problematic error\n")
            else:
                fixed_lines.append(line)
        else:
            fixed_lines.append(line)
    
    # Juga comment out problematic API key assignment
    for i, line in enumerate(fixed_lines):
        if 'story_generator.api_key = OPENROUTER_API_KEY' in line:
            fixed_lines[i] = "# " + line.rstrip() + "  # TEMPORARILY COMMENTED\n"
        elif 'st.sidebar.success("✅ API Key Loaded")' in line:
            fixed_lines[i] = "# " + line.rstrip() + "  # TEMPORARILY COMMENTED\n"
    
    with open('apps/main_clean_imports.py', 'w') as f:
        f.writelines(fixed_lines)
    
    print("✅ Problematic imports removed")

remove_problematic_section()
