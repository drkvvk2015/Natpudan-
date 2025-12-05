"""Test backend startup step by step"""
import sys
import time
import os

# Fix encoding for Windows
os.environ['PYTHONIOENCODING'] = 'utf-8'

print("=" * 50)
print("BACKEND STARTUP DIAGNOSTIC")
print("=" * 50)

try:
    print("\n1. Testing basic imports...")
    import app
    print("[OK] app package")
    
    print("\n2. Testing database...")
    from app.database import engine, SessionLocal
    print("[OK] database module")
    
    print("\n3. Testing models...")
    from app.models import Base
    print("[OK] models module")
    
    print("\n4. Testing main module import...")
    start = time.time()
    from app import main
    elapsed = time.time() - start
    print(f"[OK] main module imported in {elapsed:.2f}s")
    
    print("\n5. Testing FastAPI app...")
    app_instance = main.app
    print(f"[OK] FastAPI app: {app_instance.title}")
    
    print("\n6. Testing init_db...")
    start = time.time()
    from app.database import init_db
    init_db()
    elapsed = time.time() - start
    print(f"[OK] Database initialized in {elapsed:.2f}s")
    
    print("\n" + "=" * 50)
    print("[SUCCESS] ALL TESTS PASSED - Backend should start normally")
    print("=" * 50)
    
except Exception as e:
    print(f"\n[ERROR] {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
