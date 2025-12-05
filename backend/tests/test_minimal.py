"""Minimal test - find exactly where it hangs"""
import sys
import os
os.environ['PYTHONIOENCODING'] = 'utf-8'

print("Step 1: Import app package...")
sys.stdout.flush()
import app
print("Step 1: DONE")
sys.stdout.flush()

print("Step 2: Import database...")
sys.stdout.flush()
from app.database import engine
print("Step 2: DONE")
sys.stdout.flush()

print("Step 3: Import models...")
sys.stdout.flush()
from app.models import Base
print("Step 3: DONE")
sys.stdout.flush()

print("Step 4: Import app.main (THIS MAY HANG)...")
sys.stdout.flush()
from app import main
print("Step 4: DONE")
sys.stdout.flush()

print("ALL IMPORTS SUCCESSFUL")
