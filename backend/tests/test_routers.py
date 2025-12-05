"""Test which router is blocking"""
import sys
print("="*60)
print("TESTING ROUTER IMPORTS")
print("="*60)

print("\n1. Testing auth_new...")
try:
    from app.api.auth_new import router as auth_router
    print("   [OK] auth_new OK")
except Exception as e:
    print(f"   [ERROR] auth_new FAILED: {e}")
    sys.exit(1)

print("\n2. Testing chat_new...")
try:
    from app.api.chat_new import router as chat_router
    print("   [OK] chat_new OK")
except Exception as e:
    print(f"   [ERROR] chat_new FAILED: {e}")
    sys.exit(1)

print("\n3. Testing discharge...")
try:
    from app.api.discharge import router as discharge_router
    print("   [OK] discharge OK")
except Exception as e:
    print(f"   [ERROR] discharge FAILED: {e}")
    sys.exit(1)

print("\n" + "="*60)
print("[OK] ALL ROUTERS IMPORT SUCCESSFULLY!")
print("="*60)
