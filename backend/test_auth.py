import sys
sys.path.insert(0, '.')

from app.utils.security import verify_password
from app.crud import authenticate_user
from app.database import SessionLocal

# Test 1: Direct verify_password test
print("=" * 60)
print("TEST 1: Direct verify_password() Test")
print("=" * 60)

bcrypt_hash = "$2b$12$XKErYKaFgj8xXQ8tKHMsh.LCGLbOWKsEnmKtetijZL3DoJgpKw5eW"
test_password = "Admin@123"

try:
    result = verify_password(test_password, bcrypt_hash)
    print(f"Password: '{test_password}'")
    print(f"Hash: {bcrypt_hash[:40]}...")
    print(f"verify_password() result: {result}")
    if result:
        print("✅ Password verification WORKS!")
    else:
        print("❌ Password verification FAILED")
except Exception as e:
    print(f"❌ Error in verify_password: {e}")

# Test 2: authenticate_user test
print("\n" + "=" * 60)
print("TEST 2: authenticate_user() Test")
print("=" * 60)

db = SessionLocal()
try:
    user = authenticate_user(db, "admin@admin.com", "Admin@123")
    if user:
        print(f"✅ Authentication SUCCESS")
        print(f"   Email: {user.email}")
        print(f"   Role: {user.role}")
        print(f"   Full Name: {user.full_name}")
    else:
        print("❌ Authentication FAILED")
        print("   This means authenticate_user returned None")
except Exception as e:
    print(f"❌ Error in authenticate_user: {e}")
    import traceback
    traceback.print_exc()
finally:
    db.close()

# Test 3: Check what's in the database
print("\n" + "=" * 60)
print("TEST 3: Check Database Admin User")
print("=" * 60)

db = SessionLocal()
try:
    from app.models import User
    admin = db.query(User).filter(User.email == "admin@admin.com").first()
    if admin:
        print(f"Admin exists: YES ✅")
        print(f"  Email: {admin.email}")
        print(f"  Role: {admin.role}")
        print(f"  Hash (first 40 chars): {admin.hashed_password[:40]}...")
        print(f"  Hash length: {len(admin.hashed_password)}")
    else:
        print("Admin exists: NO ❌")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
finally:
    db.close()
