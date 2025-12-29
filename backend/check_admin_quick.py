#!/usr/bin/env python3
from app.database import SessionLocal
from app.models import User

db = SessionLocal()
admin = db.query(User).filter(User.role == 'admin').first()
if admin:
    print(f"Admin email: {admin.email}")
    print(f"Admin ID: {admin.id}")
    print(f"Admin role: {admin.role}")
else:
    print("No admin user found")
db.close()
