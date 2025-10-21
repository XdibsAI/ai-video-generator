# Cek syntax Python
try:
    with open('apps/main.py', 'r') as f:
        code = f.read()
    
    # Compile untuk cek syntax
    compile(code, 'apps/main.py', 'exec')
    print("✅ Syntax Python valid!")
    
except SyntaxError as e:
    print(f"❌ Syntax error: {e}")
    print(f"   Line {e.lineno}: {e.text}")
except Exception as e:
    print(f"❌ Error: {e}")
