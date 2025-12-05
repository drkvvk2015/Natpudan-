"""Test script to identify import errors"""
import sys
import traceback

print("=" * 60)
print("Testing Backend Import")
print("=" * 60)

try:
    print("\n1. Testing database import...")
    from app.database import init_db, get_db
    print("   [OK] Database module imported successfully")
    
    print("\n2. Testing models import...")
    from app.models import User, Conversation, Message
    print("   [OK] Models imported successfully")
    
    print("\n3. Testing crud import...")
    from app.crud import get_user_by_email, create_user
    print("   [OK] CRUD imported successfully")
    
    print("\n4. Testing auth_new import...")
    from app.api.auth_new import router as auth_router
    print("   [OK] Auth router imported successfully")
    
    print("\n5. Testing chat_new import...")
    from app.api.chat_new import router as chat_router
    print("   [OK] Chat router imported successfully")
    
    print("\n6. Testing main app import...")
    from app.main import app
    print("   [OK] Main app imported successfully")
    
    print("\n" + "=" * 60)
    print("[OK] ALL IMPORTS SUCCESSFUL - Backend should work!")
    print("=" * 60)
    
except Exception as e:
    print("\n" + "=" * 60)
    print("[ERROR] ERROR FOUND:")
    print("=" * 60)
    print(f"\nError: {str(e)}")
    print("\nFull traceback:")
    traceback.print_exc()
    print("=" * 60)
    sys.exit(1)
