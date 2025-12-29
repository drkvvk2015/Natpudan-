#!/usr/bin/env python3
from app.database import SessionLocal
from app.models import User
from app.utils.security import hash_password

db = SessionLocal()
admin = db.query(User).filter(User.email == 'admin@admin.com').first()

if admin:
    # Reset password to admin123
    admin.hashed_password = hash_password('admin123')
    db.commit()
    print(f"Password reset for {admin.email}")
    print(f"New password hash: {admin.hashed_password[:50]}...")
else:
    print("Admin user not found")

db.close()
