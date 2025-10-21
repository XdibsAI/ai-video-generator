"""
Comment out problematic imports sementara untuk bisa jalan dulu
"""

def comment_problematic():
    with open('apps/main_backup_with_errors.py', 'r') as f:
        content = f.read()
    
    # Comment out problematic import blocks
    lines = content.split('\n')
    fixed_lines = []
    
    in_problematic_block = False
    for i, line in enumerate(lines):
        # Area imports yang problematic (sekitar line 50-80)
        if i >= 50 and i <= 80:
            if 'try:' in line or 'except' in line:
                if 'OPENROUTER_API_KEY' in line or 'story_generator' in line:
                    fixed_lines.append("# " + line + "  # TEMPORARILY COMMENTED")
                    in_problematic_block = True
                else:
                    fixed_lines.append(line)
            elif in_problematic_block and line.strip() == '':
                fixed_lines.append(line)
                in_problematic_block = False
            else:
                fixed_lines.append(line)
        else:
            fixed_lines.append(line)
    
    # Juga comment out problematic method calls
    final_lines = []
    for line in fixed_lines:
        if 'story_generator.api_key' in line and 'OPENROUTER_API_KEY' in line:
            final_lines.append("# " + line + "  # TEMPORARILY COMMENTED")
        else:
            final_lines.append(line)
    
    with open('apps/main_comment_fix.py', 'w') as f:
        f.write('\n'.join(final_lines))
    
    print("✅ Problematic imports commented out")

comment_problematic()
