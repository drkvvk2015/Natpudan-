"""Database package - re-exports from parent database.py module"""

# Re-export database functionality from parent database.py
# This allows "from app.database import get_db" to work correctly
import sys
from pathlib import Path

# Get the parent app directory
parent_dir = Path(__file__).parent.parent

# Import database module from parent (database.py)
import importlib.util
spec = importlib.util.spec_from_file_location("database_module", parent_dir / "database.py")
database_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(database_module)

# Export everything from database.py
SessionLocal = database_module.SessionLocal
get_db = database_module.get_db
init_db = database_module.init_db
engine = database_module.engine

__all__ = ['SessionLocal', 'get_db', 'init_db', 'engine']
