#!/usr/bin/env python
"""Environment validation script for Natpudan Medical AI."""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
backend_dir = Path(__file__).parent
env_file = backend_dir / ".env"
load_dotenv(env_file)

print("\n" + "=" * 70)
print("NATPUDAN MEDICAL AI - ENVIRONMENT VALIDATION")
print("=" * 70 + "\n")

# Validation rules
validations = {
    "CRITICAL": [],
    "WARNING": [],
    "INFO": []
}

def check_critical(key: str, description: str, pattern: str = None):
    """Check critical environment variable."""
    value = os.getenv(key)
    if not value:
        validations["CRITICAL"].append(f"❌ {key}: {description}")
        return False
    if pattern and not value.startswith(pattern):
        validations["CRITICAL"].append(f"❌ {key}: Invalid format - {description}")
        return False
    validations["INFO"].append(f"✅ {key}: Configured")
    return True

def check_optional(key: str, description: str):
    """Check optional environment variable."""
    value = os.getenv(key)
    if not value:
        validations["WARNING"].append(f"⚠️  {key}: {description} (optional)")
        return False
    validations["INFO"].append(f"✅ {key}: Configured")
    return True

# Critical checks
print("CRITICAL CHECKS:")
print("-" * 70)
check_critical("OPENAI_API_KEY", "OpenAI API key required for AI features", "sk-")
check_critical("SECRET_KEY", "JWT secret key required for authentication")
check_critical("DATABASE_URL", "Database connection string required")

# Optional checks
print("\nOPTIONAL CONFIGURATIONS:")
print("-" * 70)
check_optional("GOOGLE_CLIENT_ID", "Google OAuth (optional)")
check_optional("GITHUB_CLIENT_ID", "GitHub OAuth (optional)")
check_optional("REDIS_URL", "Redis for background jobs (optional)")
check_optional("SENTRY_DSN", "Sentry error tracking (optional)")

# Display results
print("\n" + "=" * 70)
print("VALIDATION RESULTS")
print("=" * 70)

if validations["CRITICAL"]:
    print("\n🔴 CRITICAL ISSUES (Must fix):")
    for issue in validations["CRITICAL"]:
        print(f"   {issue}")
    print("\nTo fix: Copy backend/.env.example to backend/.env and fill in required values")
    sys.exit(1)

if validations["WARNING"]:
    print("\n🟡 WARNINGS (Optional features disabled):")
    for issue in validations["WARNING"]:
        print(f"   {issue}")

print("\n🟢 CHECKS PASSED:")
for info in validations["INFO"]:
    print(f"   {info}")

print("\n" + "=" * 70)
print("✅ ENVIRONMENT READY FOR DEVELOPMENT")
print("=" * 70)
print("\nNext steps:")
print("1. Start backend:  python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000")
print("2. Start frontend: cd frontend && npm run dev")
print("3. Visit: http://localhost:5173")
print("4. API Docs: http://localhost:8000/docs")
print()
