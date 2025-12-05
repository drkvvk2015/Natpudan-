#!/usr/bin/env python3
"""Simple static syntax checker for Python files in the backend.

Run from repository root:
    python3 scripts/check_python_syntax.py

Exits with code 0 when all files compile, non-zero otherwise.
"""
import os
import sys
import py_compile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"

errors = []

for dirpath, dirnames, filenames in os.walk(BACKEND):
    # skip virtualenvs and __pycache__
    if ".venv" in dirpath.split(os.sep) or "__pycache__" in dirpath:
        continue
    for fn in filenames:
        if not fn.endswith('.py'):
            continue
        path = Path(dirpath) / fn
        try:
            py_compile.compile(str(path), doraise=True)
        except Exception as e:
            errors.append((str(path.relative_to(ROOT)), str(e)))

if errors:
    print("Python syntax check FAILED for the following files:")
    for p, msg in errors:
        print(f" - {p}: {msg}")
    sys.exit(2)

print("Python syntax check passed: no syntax errors found.")
sys.exit(0)
