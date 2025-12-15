"""Create admin user directly in database without API call."""
import sys
import os

# Add backend directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.database import SessionLocal
from app.crud import create_user, get_user_by_email

def main():
    print("\n" + "="*50)
    print(" Creating Admin User (Direct DB)")
    print("="*50 + "\n")
    
    db = SessionLocal()
    try:
        # Check if admin already exists
        existing = get_user_by_email(db, "admin@admin.com")
        if existing:
            print("✓ Admin user already exists!")
            print(f"  Email: {existing.email}")
            print(f"  Name: {existing.full_name}")
            print(f"  Role: {existing.role.value}")
            return
        
        # Create admin user
        print("Creating admin user...")
        admin = create_user(
            db=db,
            email="admin@admin.com",
            password="Admin@123",
            full_name="System Administrator",
            role="admin",
            license_number="ADMIN-001"
        )
        
        print("\n✓ Admin user created successfully!")
        print(f"  Email: {admin.email}")
        print(f"  Password: Admin@123")
        print(f"  Name: {admin.full_name}")
        print(f"  Role: {admin.role.value}")
        print("\nYou can now login at: http://127.0.0.1:5173")
        
    except Exception as e:
        print(f"\n✗ Error creating admin user: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    main()
