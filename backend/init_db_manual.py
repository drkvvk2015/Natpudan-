#!/usr/bin/env python
"""Initialize database with all tables"""
import sys
sys.path.insert(0, 'D:/Users/CNSHO/Documents/GitHub/Natpudan-/backend')

from app.database.base import Base
from app.database.connection import engine
from app.models import chat, user, medical_models, patient_intake_models, treatment_plan

print("Creating all database tables...")
print(f"Models registered: {list(Base.metadata.tables.keys())}")

Base.metadata.create_all(bind=engine)

print("\nVerifying tables...")
import sqlite3
conn = sqlite3.connect('D:/Users/CNSHO/Documents/GitHub/Natpudan-/physician_ai.db')
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print(f"Created tables: {[t[0] for t in tables]}")

print("\nChecking chat_sessions schema...")
cursor.execute('PRAGMA table_info(chat_sessions)')
rows = cursor.fetchall()
for row in rows:
    print(f"  {row[1]:25} {row[2]:15}")

conn.close()
print("\n[OK] Database initialization complete!")
